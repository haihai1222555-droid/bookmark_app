import os
import re

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# .env에 적은 MongoDB 주소를 사용합니다.
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
db = client[os.getenv("DB_NAME", "my_bookmark")]


def login_user_id():
    """로그인한 아이디를 세션에서 꺼내는 작은 도움 함수입니다."""
    return session.get("user_id")


@app.errorhandler(PyMongoError)
def handle_mongodb_error(error):
    # MongoDB가 꺼져 있을 때 긴 개발자 오류 화면 대신 안내 화면을 보여줍니다.
    if request.path.startswith("/api/"):
        return jsonify(
            {
                "ok": False,
                "message": "MongoDB 연결에 실패했습니다. Atlas 사용자 이름과 비밀번호를 확인해주세요.",
            }
        ), 503

    return render_template("database_error.html"), 503


@app.route("/", methods=["GET", "POST"])
def login():
    # 이미 로그인했다면 메인 화면으로 이동합니다.
    if login_user_id():
        return redirect(url_for("main"))

    error = ""

    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "")
        user = db.users.find_one({"user_id": user_id})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user_id
            return redirect(url_for("main"))

        error = "회원 정보가 올바르지 않습니다."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""

    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "")
        password_check = request.form.get("password_check", "")

        if not user_id or not password:
            error = "아이디와 비밀번호를 모두 입력해주세요."
        elif password != password_check:
            error = "비밀번호가 서로 다릅니다."
        elif db.users.find_one({"user_id": user_id}):
            error = "이미 사용 중인 아이디입니다."
        else:
            hashed_password = generate_password_hash(password)
            db.users.insert_one({"user_id": user_id, "password": hashed_password})
            return redirect(url_for("login"))

    return render_template("signup.html", error=error)


@app.route("/api/check-id", methods=["POST"])
def check_id():
    # 회원가입 화면의 아이디 중복 확인 AJAX입니다.
    user_id = request.form.get("user_id", "").strip()

    if not user_id:
        return jsonify({"available": False, "message": "아이디를 입력해주세요."})

    if db.users.find_one({"user_id": user_id}):
        return jsonify({"available": False, "message": "이미 사용 중인 아이디입니다."})

    return jsonify({"available": True, "message": "사용할 수 있는 아이디입니다."})


@app.route("/main")
def main():
    # 로그인 사용자만 자신의 북마크를 볼 수 있습니다.
    user_id = login_user_id()
    if not user_id:
        return redirect(url_for("login"))

    bookmark_list = []
    bookmarks = db.bookmarks.find({"owner": user_id}).sort("_id", -1)

    for bookmark in bookmarks:
        bookmark_list.append(
            {
                "id": str(bookmark["_id"]),
                "title": bookmark["title"],
                "url": bookmark["url"],
            }
        )

    # 처음 화면은 Jinja2가 서버에서 목록을 그립니다.
    return render_template("main.html", user_id=user_id, bookmarks=bookmark_list)


@app.route("/api/bookmarks", methods=["POST"])
def create_bookmark():
    user_id = login_user_id()
    if not user_id:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()

    if not title or not url:
        return jsonify({"ok": False, "message": "제목과 URL을 모두 입력해주세요."}), 400

    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify({"ok": False, "message": "URL은 http:// 또는 https://로 시작해야 합니다."}), 400

    result = db.bookmarks.insert_one({"owner": user_id, "title": title, "url": url})

    return jsonify(
        {
            "ok": True,
            "bookmark": {"id": str(result.inserted_id), "title": title, "url": url},
        }
    )


@app.route("/api/bookmarks/search")
def search_bookmarks():
    user_id = login_user_id()
    if not user_id:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    keyword = request.args.get("keyword", "").strip()
    condition = {"owner": user_id}

    if keyword:
        # 검색 문자를 정규식 기호가 아닌 일반 글자로 취급합니다.
        condition["title"] = {"$regex": re.escape(keyword), "$options": "i"}

    result_list = []
    for bookmark in db.bookmarks.find(condition).sort("_id", -1):
        result_list.append(
            {
                "id": str(bookmark["_id"]),
                "title": bookmark["title"],
                "url": bookmark["url"],
            }
        )

    return jsonify({"ok": True, "bookmarks": result_list})


@app.route("/api/bookmarks/<bookmark_id>", methods=["PUT"])
def update_bookmark(bookmark_id):
    user_id = login_user_id()
    if not user_id:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    if not ObjectId.is_valid(bookmark_id):
        return jsonify({"ok": False, "message": "잘못된 북마크 번호입니다."}), 400

    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()

    if not title or not url:
        return jsonify({"ok": False, "message": "제목과 URL을 모두 입력해주세요."}), 400

    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify({"ok": False, "message": "URL은 http:// 또는 https://로 시작해야 합니다."}), 400

    # 북마크 번호뿐 아니라 owner도 함께 확인합니다.
    result = db.bookmarks.update_one(
        {"_id": ObjectId(bookmark_id), "owner": user_id},
        {"$set": {"title": title, "url": url}},
    )

    if result.matched_count == 0:
        return jsonify({"ok": False, "message": "수정할 북마크를 찾지 못했습니다."}), 404

    return jsonify({"ok": True})


@app.route("/api/bookmarks/<bookmark_id>", methods=["DELETE"])
def delete_bookmark(bookmark_id):
    user_id = login_user_id()
    if not user_id:
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    if not ObjectId.is_valid(bookmark_id):
        return jsonify({"ok": False, "message": "잘못된 북마크 번호입니다."}), 400

    # 다른 사람의 북마크는 번호를 알아도 삭제할 수 없습니다.
    result = db.bookmarks.delete_one({"_id": ObjectId(bookmark_id), "owner": user_id})

    if result.deleted_count == 0:
        return jsonify({"ok": False, "message": "삭제할 북마크를 찾지 못했습니다."}), 404

    return jsonify({"ok": True})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
