$(document).ready(function() {
    var $container = $('#video-container'),
        $form = $('#video-form');

    var initBindings = function() {
        $form.on('submit', function(event) {
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
                    action: 'video.omxplayer.stop',
                },

                function() {
                    execute(
                        {
                            type: 'request',
                            action: 'video.omxplayer.play',
                            args: formData,
                        }
                    )
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

