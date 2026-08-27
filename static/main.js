function makeItem(data) {
    var item = $('<div>').addClass('bookmark-item').attr('data-id', data.id);
    var button = $('<button>').addClass('title-button').attr('type', 'button');
    button.append($('<span>').addClass('arrow').text('▶'));
    button.append(' ');
    button.append($('<span>').addClass('title-text').text(data.title));

    var detail = $('<div>').addClass('bookmark-detail d-none');
    var url = $('<p>').text('주소 : ');
    url.append($('<a>').addClass('url-link').attr('href', data.url).attr('target', '_blank').attr('rel', 'noopener noreferrer').text(data.url));
    detail.append(url);
    detail.append($('<button>').addClass('btn btn-secondary btn-sm edit-button').text('수정'));
    detail.append(' ');
    detail.append($('<button>').addClass('btn btn-danger btn-sm delete-button').text('삭제'));

    item.append(button);
    item.append(detail);
    return item;
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
        success: function () {
            location.reload();
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.message);
            } else {
                alert('오류가 발생했습니다.');
            }
        }
    });
});

$('#search-button').click(function () {
    $.ajax({
        type: 'GET',
        url: '/api/bookmarks/search',
        data: { keyword: $('#search-keyword').val() },
        success: function (data) {
            $('#bookmark-list').empty();
            if (data.bookmarks.length == 0) {
                $('#bookmark-list').append('<p class="empty-message">검색 결과가 없습니다.</p>');
            }
            for (var i = 0; i < data.bookmarks.length; i++) {
                $('#bookmark-list').append(makeItem(data.bookmarks[i]));
            }
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.message);
            } else {
                alert('오류가 발생했습니다.');
            }
        }
    });
});

$('#search-keyword').keydown(function (event) {
    if (event.key == 'Enter') {
        $('#search-button').click();
    }
});

$(document).on('click', '.title-button', function () {
    var detail = $(this).next('.bookmark-detail');
    detail.toggleClass('d-none');
    if (detail.hasClass('d-none')) {
        $(this).find('.arrow').text('▶');
    } else {
        $(this).find('.arrow').text('▼');
    }
});

$(document).on('click', '.edit-button', function () {
    let item = $(this).closest('.bookmark-item');
    let id = item.attr('data-id');
    let currentTitle = item.find('.title-text').text();
    let currentUrl = item.find('.url-link').attr('href');

    $('#edit-id').val(id);
    $('#edit-title').val(currentTitle);
    $('#edit-url').val(currentUrl);

    $('#edit-form').removeClass('d-none');
});

$('#cancel-edit-button').click(function () {
    $('#edit-form').addClass('d-none');
});

$('#save-edit-button').click(function () {
    let id = $('#edit-id').val();
    let newTitle = $('#edit-title').val();
    let newUrl = $('#edit-url').val();

    $.ajax({
        type: 'PUT',
        url: '/api/bookmarks/' + id,
        data: { title: newTitle, url: newUrl },

        success: function () {
            if (confirm('수정하시겠습니까?') == true) {
                let item = $('.bookmark-item[data-id="' + id + '"]');
                item.find('.title-text').text(newTitle);
                item.find('.url-link').attr('href', newUrl).text(newUrl);

                $('#edit-form').addClass('d-none');
            }
            else {
                return;
            }
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON);
            }
            else {
                alert('오류가 발생했습니다.');
            }
        }
    });
});

$(document).on('click', '.delete-button', function () {
    var item = $(this).closest('.bookmark-item');
    if (confirm('삭제할까요?') == false) {
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/api/bookmarks/' + item.attr('data-id'),
        success: function () {
            location.reload();
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.message);
            } else {
                alert('오류가 발생했습니다.');
            }
        }
    });
});
