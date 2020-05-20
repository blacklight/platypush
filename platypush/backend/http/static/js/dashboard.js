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
        enterFullScreen();
    },
});

