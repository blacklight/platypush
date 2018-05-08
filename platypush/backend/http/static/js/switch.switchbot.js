$(document).ready(function() {
    var switches,
        $switchbotContainer = $('#switchbot-container');

    var initBindings = function() {
        $switchbotContainer.on('click touch', '.switch-ctrl-container', function() {
            var $input = $(this).find('.switch-ctrl');
            var addr = $input.attr('name');
            $input.prop('checked', true);

            execute(
                {
                    type: 'request',
                    action: 'switch.switchbot.press',
                    args: {
                        device: addr
                    }
                },

                onSuccess = function(response) {
                    $input.prop('checked', false);
                }
            );
        });
    };

    var init = function() {
        initBindings();
    };

    init();
});

