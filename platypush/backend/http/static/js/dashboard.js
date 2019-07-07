Vue.component('widget', {
    template: '#tmpl-widget',
    props: ['config','tag'],
});

// Declaration of the main vue app
window.vm = new Vue({
    el: '#app',

    props: {
        config: {
            type: Object,
            default: () => window.config,
        },
    },

    data: function() {
        return {
            iframeModal: {
                visible: false,
            },
        };
    },

    created: function() {
        initEvents();
    },
});

// $(document).ready(function() {
//     var onEvent = function(event) {
//         if (event.args.type == 'platypush.message.event.web.widget.WidgetUpdateEvent') {
//             var $widget = $('#' + event.args.widget);
//             delete event.args.widget;

//             for (var key of Object.keys(event.args)) {
//                 $widget.find('[data-bind=' + key + ']').text(event.args[key]);
//             }
//         } else if (event.args.type == 'platypush.message.event.web.DashboardIframeUpdateEvent') {
//             var url = event.args.url;
//             var $modal = $('#iframe-modal');
//             var $iframe = $modal.find('iframe');
//             $iframe.attr('src', url);
//             $iframe.prop('width',  event.args.width  || '100%');
//             $iframe.prop('height', event.args.height || '600');

//             if ('timeout' in event.args) {
//                 setTimeout(function() {
//                     $iframe.removeAttr('src');
//                     $modal.fadeOut();
//                 }, parseFloat(event.args.timeout) * 1000);
//             }

//             $modal.fadeIn();
//         }
//     };

//     var initDashboard = function() {
//         if (window.config.dashboard.background_image) {
//             $('body').css('background-image', 'url(' + window.config.dashboard.background_image + ')');
//         }
//     };

//     var initEvents = function() {
//         registerEventListener(onEvent);
//     };

//     var init = function() {
//         initDashboard();
//         initEvents();
//     };

//     init();
// });

