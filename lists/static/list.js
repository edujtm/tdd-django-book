
window.Superlists = {};

window.Superlists.updateItems = function (url) {
    $.get(url).done(function (response) {
            let rows = '';
            for (let i = 0; i < response.items.length; i++) {
                const item = response.items[i];
                rows += '\n<tr><td>' + (i + 1) + ': ' + item.text + '</td></tr>'
            }

            $('#id_list_table').html(rows);
        });
};

window.Superlists.initialize = function (params) {
    $('input[name="text"]').on('keypress', function () {
        $('.has-error').hide()
    });

    if (params) {
        window.Superlists.updateItems(params.listApiUrl);
        const form = $('#id_item_form');

        form.on('submit', function (event) {
            event.preventDefault();
            $.post(params.itemsApiUrl, {
                'list': params.listId,
                'text': form.find('input[name="text"]').val(),
                'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val(),
            }).done(function () {
                window.Superlists.updateItems(params.listApiUrl);
            }).fail(function (xhr) {
                $('.has-error').show();
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    json_data = xhr.responseJSON;
                    $('.has-error .help-block').html(json_data.error)
                }
            });
        });
    }


};

