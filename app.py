import os
import re
import random
import smtplib
import time

from email.mime.text import MIMEText
from email.header import Header
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, flash
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "false").lower() == "true"

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
db = client[os.getenv("DB_NAME", "my_bookmark")]


@app.errorhandler(PyMongoError)
def handle_mongodb_error(error):
    if request.path.startswith("/api/"):
        return jsonify(
            {
                "ok": False,
                "message": "MongoDB 연결에 실패했습니다. Atlas 사용자 이름과 비밀번호를 확인해주세요.",
            }
        ), 503

    return render_template("database_error.html"), 503

def is_valid_id(user_id):
    pattern = r"^[a-z0-9]{4,12}$"
    return bool(re.match(pattern, user_id))

def is_valid_password(password):
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+=~])[A-Za-z\d!@#$%^&*()_+=~]{8,20}$"
    return bool(re.match(pattern, password))

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main"))

    error = ""

    if request.method == "POST":
        login_input = request.form.get("user_id", "").strip()
        password = request.form.get("password", "")

        matched_users = db.users.find({
            "$or":[
                {"user_id": login_input},
                {"user_name": login_input},
                {"email": login_input}
            ]
        })

        logged_in = False

        for user in matched_users:
            if user and check_password_hash(user["password"], password):
                  session["user_id"] = user["user_id"]
                  user_name = user.get("user_name", user["user_id"])
                  session["user_name"] = user_name

                  flash(f"{user_name}님 환영합니다.")
                  logged_in = True
                  return redirect(url_for("main"))
        
        if not logged_in:
             error = "회원 정보가 올바르지 않습니다."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""

    if request.method == "POST":
        user_name = request.form.get("user_name", "").strip()
        user_id = request.form.get("user_id", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_check = request.form.get("password_check", "")

        if not user_name or not user_id or not password:
            error = "이름, 아이디, 비밀번호를 모두 입력해주세요."
        elif not is_valid_id(user_id):
            error = "아아디는 4~12자의 영문 소문자, 숫자만 가능합니다."
        elif not is_valid_password(password):
            error = "비밀번호는 8~20자의 영문, 숫자, 특수문자를 조합해야 합니다."
        elif password != password_check:
            error = "비밀번호가 서로 다릅니다."
        elif db.users.find_one({"user_id": user_id}):
            error = "이미 사용 중인 아이디입니다."
        elif db.users.find_one({"email": email}):
            error="이미 사용 중인 이메일입니다."
        else:
            hashed_password = generate_password_hash(password)
            db.users.insert_one({"user_name": user_name, "user_id": user_id, "email": email, "password": hashed_password})
            return redirect(url_for("login"))

    return render_template("signup.html", error=error)

@app.route("/find-id")
def find_id():
    return render_template("find_id.html")

@app.route("/reset-password")
def reset_password():
    return render_template("reset_password.html")

@app.route("/api/find-id", methods=["POST"])
def api_find_id():
    user_name = request.form.get("user_name", "").strip()
    email = request.form.get("email", "").strip();

    if not session.get("is_email_verified") or session.get("auth_email") != email:
        return jsonify({"ok": False, "message": "이메일 인증이 필요합니다."}), 400

    user = db.users.find_one({"user_name": user_name, "email": email})
    if not user:
        return jsonify({"ok": False, "message": "일치하는 회원 정보를 찾을 수 없습니다."}), 404

    return jsonify({"ok": True, "user_id": user["user_id"]})

@app.route("/api/check-id", methods=["POST"])
def check_id():
    user_id = request.form.get("user_id", "").strip()

    if not user_id:
        return jsonify({"available": False, "message": "아이디를 입력해주세요."})

    if not is_valid_id(user_id):
        return jsonify({"available": False, "message": "아이디는 4~12자의 영문 소문자, 숫자만 가능합니다."})

    if db.users.find_one({"user_id": user_id}):
        return jsonify({"available": False, "message": "이미 사용 중인 아이디입니다."})

    return jsonify({"available": True, "message": "사용할 수 있는 아이디입니다."})

@app.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    user_name = request.form.get("user_name", "").strip()
    user_id = request.form.get("user_id", "").strip()
    email = request.form.get("email", "").strip()
    new_password = request.form.get("new_password", "")

    if not is_valid_password(new_password):
        return jsonify({"ok": False, "message": "새 비밀번호는 8~20자의 영문, 숫자, 특수문자를 조합해야 합니다."}), 400

    if not session.get("is_email_verified") or session.get("auth_email") != email:
        return jsonify({"ok": False, "message": "이메일 인증이 필요합니다."}), 400

    user = db.users.find_one({"user_name": user_name, "user_id": user_id, "email": email})
    if not user:
            return jsonify({"ok": False, "message": "일치하는 회원 정보를 찾을 수 없습니다."}), 404

    db.users.update_one({"_id": user["_id"]}, {"$set": {"password": generate_password_hash(new_password)}})
    session["is_email_verified"] = False
    return jsonify({"ok": True, "message": "비밀번호가 변경되었습니다."})

@app.route("/api/send-email-code", methods=["POST"])
def send_emal_code():
    email = request.form.get("email", "").strip()

    if not email:
        return jsonify({"ok": False, "message": "이메일을 입력해주세요."}), 400

    if db.users.find_one({"email": email}):
        return jsonify({"ok": False, "message": "이미 가입된 이메일입니다."}), 400
    

    auth_code = str(random.randint(100000, 999999))

    session["auth_email"] = email
    session["auth_code"] = auth_code
    session["auth_time"] = time.time()
    session["is_email_verified"] = False

    try:
        send_auth_email(email, auth_code)
        return jsonify({"ok": True, "message": "인증번호가 전송되었습니다. 메일함을 확인해주세요."})
    except Exception as e:
        print ("메일 발송 에러 : ", e)
        return jsonify({"ok": False, "message": "메일 발송에 실패했습니다. 이메일 주소를 확인해주세요."}), 500

@app.route("/api/verify-email-code", methods=["POST"])
def verify_email_code():
    user_code = request.form.get("code", "").strip()
    saved_code = session.get("auth_code")
    saved_time = session.get("auth_time", 0)

    if time.time() - saved_time > 600:
        return jsonify({"ok": True, "message": "인증번호 유효시간(10분)이 만료되었습니다. 재전송해주세요."}), 400

    if saved_code and user_code == saved_code:
        session["is_email_verified"] = True
        return jsonify({"ok": True, "message": "이메일 인증이 완료되었습니다."})
    else:
        return jsonify({"ok": True, "message": "인증번호가 일치하지 않습니다. 다시 확인해주세요."}), 400



@app.route("/main")
def main():
    user_id = session.get("user_id")
    user_name = session.get("user_name", user_id)
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

    return render_template("main.html", user_id=user_id, user_name=user_name, bookmarks=bookmark_list)

@app.route("/api/bookmarks", methods=["POST"])
def create_bookmark():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "message": ""}),401

    title = request.form.get("title", "").strip()
    url = request.form.get("url").strip()

    if not title or not url:
        return jsonify({"ok": False, "message": "제목과 URL을 모두 입력해주세요."}), 400

    result = db.bookmarks.insert_one({"owner": user_id, "title": title, "url": url})

    return jsonify(
        {
            "ok": True,
            "bookmark": {"id": str(result.inserted_id), "title": title, "url": url},
        }
    )


@app.route("/api/bookmarks/search")
def search_bookmarks():
    user_id = session.get("user_id")
    keyword = request.args.get("keyword", "").strip()
    condition = {"owner": user_id}

    if keyword:
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
    user_id = session.get("user_id");
    if not ObjectId.is_valid(bookmark_id):
        return jsonify({"ok": False, "message": "잘못된 북마크 번호입니다."}), 400

    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()


    result = db.bookmarks.update_one(
        {"_id": ObjectId(bookmark_id), "owner": user_id},
        {"$set": {"title": title, "url": url}},
    )

    if result.matched_count == 0:
        return jsonify({"ok": False, "message": "수정할 북마크를 찾지 못했습니다."}), 404

    return jsonify({"ok": True})


@app.route("/api/bookmarks/<bookmark_id>", methods=["DELETE"])
def delete_bookmark(bookmark_id):
    user_id = session.get("user_id")
    if not ObjectId.is_valid(bookmark_id):
        return jsonify({"ok": False, "message": "잘못된 북마크 번호입니다."}), 400

    result = db.bookmarks.delete_one({"_id": ObjectId(bookmark_id), "owner": user_id})

    if result.deleted_count == 0:
        return jsonify({"ok": False, "message": "삭제할 북마크를 찾지 못했습니다."}), 404

    return jsonify({"ok": True})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def send_auth_email(target_email, auth_code):
    mail_user=os.getenv("MAIL_USER")
    mail_pw = os.getenv("MAIL_PASSWORD")

    content = f"""나만의 북마크에 가입해주셔서 감사합니다.
    회원가입 인증번호는 [{auth_code}]입니다.
    인증 화면으로 돌아가 10분 내로 인증해 주시길 바랍니다."""

    msg = MIMEText(content, _charset="utf-8")
    msg["subject"] = Header("[나만의 북마크] 회원가입 이메일 인증번호", "utf-8")
    msg["From"] = f"나만의 북마크 <{mail_user}>"
    msg["To"] = target_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 587, timeout=10) as server:
        server.starttls()
        server.login(mail_user, mail_pw)
        server.send_message(msg)



if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
