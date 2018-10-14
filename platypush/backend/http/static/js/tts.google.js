$(document).ready(function() {
    var $container = $('#tts-container'),
        $ttsForm = $('#tts-form');

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
                    action: 'tts.google.say',
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

