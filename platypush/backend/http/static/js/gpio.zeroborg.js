$(document).ready(function() {
    var $container = $('#zb-container'),
        $controlsContainer = $('.zb-controls-container');

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
        $controlsContainer.on('mousedown touchstart', '.zb-ctrl-btn[data-direction]', function() {
            console.log($(this).data('direction') + ' press start');

            $(this).addClass('selected');
            execute({
                type: 'request',
                action: 'gpio.zeroborg.drive',
                args: {
                    direction: $(this).data('direction')
                }
            });
        });

        $controlsContainer.on('mouseup touchend', '.zb-ctrl-btn[data-direction]', function() {
            console.log($(this).data('direction') + ' press end');

            $(this).removeClass('selected');
            execute({
                type: 'request',
                action: 'gpio.zeroborg.stop',
            });
        });
    };

    var init = function() {
        initBindings();
    };

    init();
});

