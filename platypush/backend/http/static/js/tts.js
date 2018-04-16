$(document).ready(function() {
    var $container = $('#tts-container'),
        $ttsForm = $('#tts-form');

    var execute = function(request, onSuccess, onError, onComplete) {
        request['target'] = 'localhost';
        return $.ajax({
            type: 'POST',
            url: '/execute',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(request),
            complete: function() {
                if (onComplete) {
                    onComplete();
                }
            },
            error: function(xhr, status, error) {
                if (onError) {
                    onError(xhr, status, error);
                }
            },
            success: function(response, status, xhr) {
                if (onSuccess) {
                    onSuccess(response, status, xhr);
                }
            },
            beforeSend: function(xhr) {
                if (window.token) {
                    xhr.setRequestHeader('X-Token', window.token);
                }
            },
        });
    };

    var initBindings = function() {
        $ttsForm.on('submit', function(event) {
            var formData = $(this).serializeArray().reduce(function(obj, item) {
                var value = item.value.trim();
                if (value.length > 0) {
                    obj[item.name] = item.value;
                }

                return obj;
            }, {});

            execute(
                {
                    type: 'request',
                    action: 'tts.say',
                    args: formData,
                }
            );

            return false;
        });
    };

    var init = function() {
        initBindings();
    };

    init();
});

