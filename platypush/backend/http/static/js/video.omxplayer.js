$(document).ready(function() {
    var $container = $('#video-container'),
        $searchForm = $('#video-search'),
        $ctrlForm = $('#video-ctrl');

    var initBindings = function() {
        $searchForm.on('submit', function(event) {
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

        $searchForm.find('button[data-action]').on('click', function(evt) {
            var action = $(this).data('action');
            var $btn = $(this);

            execute(
                {
                    type: 'request',
                    action: 'video.omxplayer.' + action,
                }
            );
        });
    };

    var init = function() {
        initBindings();
    };

    init();
});

