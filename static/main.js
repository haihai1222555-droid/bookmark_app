// 북마크 한 개의 HTML을 만드는 함수입니다.
function makeBookmarkHtml(bookmark) {
    let item = $('<div>').addClass('bookmark-item').attr('data-id', bookmark.id);
    let titleButton = $('<button>').addClass('bookmark-title-button').attr('type', 'button');
    titleButton.append($('<span>').addClass('arrow').text('▶'));
    titleButton.append($('<span>').addClass('title-text').text(bookmark.title));

    let detail = $('<div>').addClass('bookmark-detail d-none');
    let address = $('<p>').text('사이트 주소: ');
    address.append(
        $('<a>')
            .addClass('url-link')
            .attr('href', bookmark.url)
            .attr('target', '_blank')
            .attr('rel', 'noopener noreferrer')
            .text(bookmark.url)
    );
    detail.append(address);
    detail.append($('<button>').addClass('btn btn-outline-secondary btn-sm edit-button').text('수정'));
    detail.append(' ');
    detail.append($('<button>').addClass('btn btn-outline-danger btn-sm delete-button').text('삭제'));

    item.append(titleButton);
    item.append(detail);
    return item;
}

function drawBookmarks(bookmarks) {
    $('#bookmark-list').empty();

    if (bookmarks.length === 0) {
        $('#bookmark-list').append($('<p>').addClass('empty-message').text('검색 결과가 없습니다.'));
        return;
    }

    for (let i = 0; i < bookmarks.length; i++) {
        $('#bookmark-list').append(makeBookmarkHtml(bookmarks[i]));
    }
}

function showAjaxError(xhr) {
    let message = '요청 처리 중 오류가 발생했습니다.';
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    }
    alert(message);
}

$('#show-add-form').click(function () {
    $('#add-form').removeClass('d-none');
});

$('#cancel-add-button').click(function () {
    $('#add-form').addClass('d-none');
});

$('#create-button').click(function () {
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

$('#search-button').click(function () {
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

$('#search-keyword').keydown(function (event) {
    if (event.key === 'Enter') {
        $('#search-button').click();
    }
});

// AJAX로 새로 만든 항목에도 작동하도록 document에 이벤트를 연결합니다.
$(document).on('click', '.bookmark-title-button', function () {
    let detail = $(this).siblings('.bookmark-detail');
    detail.toggleClass('d-none');
    $(this).find('.arrow').text(detail.hasClass('d-none') ? '▶' : '▼');
});

$(document).on('click', '.edit-button', function () {
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

$(document).on('click', '.delete-button', function () {
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
