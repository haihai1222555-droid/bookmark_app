function makeBookmarkHtml(bookmark) { //북마크를 만드는 함수
    let item = $('<div>').addClass('bookmark-item').attr('data-id', bookmark.id); //북마크 패널에 배열을 선언함 (유니티에 있는 배열과 매우 흡사)
    let titleButton = $('<button>').addClass('bookmark-title-button').attr('type', 'button'); //북마크 패널을 펼쳤다 접을 수 있는 버튼을 선언
    titleButton.append($('<span>').addClass('arrow').text('▶')); //화살표를 누르면 북마크 패널을 펼치 거나 접을 수 있음
    titleButton.append($('<span>').addClass('title-text').text(bookmark.title)); //화살표 뿐만 아니라 제목을 눌러도 북마크 패널을 펼치 거나 접을 수 있음
    let detail = $('<div>').addClass('bookmark-detail d-none'); //펼칠 북마크를 미리 숨겨둠 (미리 접은 상태)
    let address = $('<p>').text('사이트 주소: '); //펼친 북마크에 있는 URL을 띄움 (보안 때문에 길게 작성 되어 있음)
    address.append( //여기서부터
        $('<a>')
            .addClass('url-link')
            .attr('href', bookmark.url)
            .attr('target', '_blank')
            .attr('rel', 'noopener noreferrer')
            .text(bookmark.url)
    );//여기까지 URL을 보안 처리해서 띄우는 로직
    detail.append(address); //펼친 북마크에 URL을 띄움
    detail.append($('<button>').addClass('btn btn-outline-secondary btn-sm edit-button').text('수정')); //수정 버튼을 배치
    detail.append(' '); //버튼 사이의 간격을 만듦
    detail.append($('<button>').addClass('btn btn-outline-danger btn-sm delete-button').text('삭제')); //삭제 버튼을 배치

    item.append(titleButton); //북마크 패널에 버튼을 할당
    item.append(detail); //북마크 패널에 제목, URL 버튼 등등을 할당
    return item; //브라우저에 띄우기 위해 반환
}

function drawBookmarks(bookmarks) { //검색한 북마크를 불러오는 함수
    $('#bookmark-list').empty(); // 검색 결과를 불러오기 전에 전에 있던 북마크 패널을 화면에서 삭제

    if (bookmarks.length === 0) { // 검색 결과가 없으면 '검색 결과가 없습니다'를 띄움
        $('#bookmark-list').append($('<p>').addClass('empty-message').text('검색 결과가 없습니다.'));
        return;
    }

    for (let i = 0; i < bookmarks.length; i++) { //검색 결과가 있다면 북마크를 띄움
        $('#bookmark-list').append(makeBookmarkHtml(bookmarks[i]));
    }
}

function showAjaxError(xhr) { //북마크를 불러오지 못 했을 때 띄우는 경고창
    let message = '요청 처리 중 오류가 발생했습니다.';
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    }
    alert(message);
}

$('#show-add-form').click(function () { //새 북마크 창을 띄워주는 함수 ('+ 템플릿 추가'를 눌렀을 때)
    $('#add-form').removeClass('d-none');
});

$('#cancel-add-button').click(function () { //띄운 새 북마크 창을 없애주는 함수 ('취소'를 눌렀을 때)
    $('#add-form').addClass('d-none');
});

$('#create-button').click(function () { //띄운 새 북마크 창에서 생성을 눌렀을 때 사용자 DB에 넣어주는 함수
    $.ajax({
        type: 'POST',
        url: '/api/bookmarks',
        data: {
            title: $('#new-title').val(),
            url: $('#new-url').val()
        },
        success: function (response) {
            $('.empty-message').remove();
            $('#bookmark-list').prepend(makeBookmarkHtml(response.bookmark));
            $('#new-title').val('');
            $('#new-url').val('');
            $('#add-form').addClass('d-none');
        },
        error: showAjaxError
    });
});

$('#search-button').click(function () { //검색 버튼을 눌렀을 때 사용자 DB에서 불러와 띄워주는 함수
    $.ajax({
        type: 'GET',
        url: '/api/bookmarks/search',
        data: { keyword: $('#search-keyword').val() },
        success: function (response) {
            drawBookmarks(response.bookmarks);
        },
        error: showAjaxError
    });
});

$('#search-keyword').keydown(function (event) { //'Enter' 버튼을 눌렀을 때도 사용자 DB에서 불러와 띄워주는 함수
    if (event.key === 'Enter') {
        $('#search-button').click();
    }
});

$(document).on('click', '.bookmark-title-button', function () { //화살표나 타이틀을 눌러 북마크 패널을 펼치고 닫는 로직. 닫혀 있으면 '▼', 열려 있으면 '▶' 표시됨
    let detail = $(this).siblings('.bookmark-detail');
    detail.toggleClass('d-none');
    $(this).find('.arrow').text(detail.hasClass('d-none') ? '▶' : '▼');
});

$(document).on('click', '.edit-button', function () { //이미 있는 북마크를 수정할 때 사용하는 로직 (구 제목과 구 URL을 새 제목과 새 URL로 바꾸고 DB에 업데이트)
    let item = $(this).closest('.bookmark-item');
    let oldTitle = item.find('.title-text').text();
    let oldUrl = item.find('.url-link').attr('href');
    let newTitle = prompt('새 제목을 입력하세요.', oldTitle);

    if (newTitle === null) {
        return;
    }

    let newUrl = prompt('새 URL을 입력하세요.', oldUrl);
    if (newUrl === null) {
        return;
    }

    $.ajax({
        type: 'PUT',
        url: '/api/bookmarks/' + item.attr('data-id'),
        data: { title: newTitle, url: newUrl },
        success: function () {
            item.find('.title-text').text(newTitle);
            item.find('.url-link').attr('href', newUrl).text(newUrl);
        },
        error: showAjaxError
    });
});

$(document).on('click', '.delete-button', function () { //북마크 삭제는 다시 물어보는 로직. 만약 북마크를 삭제하고 더이상 저장 되어 있는 북마크가 없다면 '저장한 북마크가 없습니다.'를 띄움
    let item = $(this).closest('.bookmark-item');

    if (!confirm('이 북마크를 삭제할까요?')) {
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/api/bookmarks/' + item.attr('data-id'),
        success: function () {
            item.remove();
            if ($('.bookmark-item').length === 0) {
                $('#bookmark-list').append($('<p>').addClass('empty-message').text('저장한 북마크가 없습니다.'));
            }
        },
        error: showAjaxError
    });
});
