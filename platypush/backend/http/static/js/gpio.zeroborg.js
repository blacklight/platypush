$(document).ready(function() {
    var $container = $('#zb-container'),
        $controlsContainer = $('.zb-controls-container'),
        curDirection = undefined;

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
            var direction = $(this).data('direction');
            curDirection = direction;
            console.log(direction + ' press start');

            $(this).addClass('selected');
            execute({
                type: 'request',
                action: 'gpio.zeroborg.drive',
                args: {
                    direction: direction
                }
            });
        });

        $controlsContainer.on('mouseup touchend', '.zb-ctrl-btn[data-direction]', function() {
            console.log($(this).data('direction') + ' press end');
            curDirection = undefined;

            $(this).removeClass('selected');
            execute({
                type: 'request',
                action: 'gpio.zeroborg.stop',
            });
        });

        $controlsContainer.on('click touch', '.zb-ctrl-btn[data-action]', function() {
            console.log('Running ' + $(this).data('action') + ' action');

            if ($(this).data('action') === 'stop') {
                $controlsContainer.find('.zb-ctrl-btn[data-action=auto]').removeClass('selected');
                curDirection = undefined;

                execute({
                    type: 'request',
                    action: 'gpio.zeroborg.stop',
                });
            } else if ($(this).data('action') === 'auto') {
                $(this).toggleClass('selected');
                curDirection = 'auto_toggle';

                execute({
                    type: 'request',
                    action: 'gpio.zeroborg.drive',
                    args: {
                        direction: 'auto_toggle'
                    }
                });
            }
        });

        var keyEventToDirection = function(event) {
            var direction;

            switch (event.keyCode) {
                case 32:  // SPACE bar
                    direction = 'auto'; break;
                case 37:  // LEFT
                    direction = 'left'; break;
                case 38:  // UP
                    direction = 'up'; break;
                case 39:  // RIGHT
                    direction = 'right'; break;
                case 40:  // DOWN
                    direction = 'down'; break;
                default:
                    return;
            }

            return direction;
        };

        $container.on('keydown', function(event) {
            if (curDirection) {
                return;
            }

            var direction = keyEventToDirection(event);
            if (direction) {
                if (direction === 'auto') {
                    $controlsContainer.find('.zb-ctrl-btn[data-action=auto]').click();
                } else {
                    $controlsContainer.find('.zb-ctrl-btn[data-direction=' + direction + ']').mousedown();
                }
            }
        });

        $container.on('keyup', function(event) {
            var direction = keyEventToDirection(event);
            if (direction) {
                if (direction === 'auto') {
                    $controlsContainer.find('.zb-ctrl-btn[data-action=auto]').click();
                    $controlsContainer.find('.zb-ctrl-btn[data-action=stop]').click();
                } else {
                    $controlsContainer.find('.zb-ctrl-btn[data-direction=' + direction + ']').mouseup();
                }
            }
        });
    };

    var init = function() {
        initBindings();
    };

    init();
});

