$(document).ready(function() {
    var onEvent = function(event) {
        if (event.args.type == 'platypush.message.event.web.widget.WidgetUpdateEvent') {
            var $widget = $('#' + event.args.widget);
            delete event.args.widget;

            for (var key of Object.keys(event.args)) {
                $widget.find('[data-bind=' + key + ']').text(event.args[key]);
            }
        }
    };

    var initDashboard = function() {
        if ('background_image' in window.config) {
            $('body').css('background-image', 'url(' + window.config.background_image + ')');
        }
    };

    var initEvents = function() {
        window.registerEventListener(onEvent);
    };

    var init = function() {
        initDashboard();
        initEvents();
    };

    init();
});

