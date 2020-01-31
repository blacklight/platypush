Vue.component('plugin', {
    template: '#tmpl-plugin',
    props: ['config','tag'],

    data: function() {
        return {
            selected: false,
        };
    },
});

// Declaration of the main vue app
window.vm = new Vue({
    el: '#app',
    // Override {{ }} delimiters to prevent clash with Flask templates
    delimiters: ['[[',']]'],

    data: function() {
        return {
            config: window.config,
            selectedPlugin: undefined,
            now: new Date(),
        };
    },

    created: function() {
        m = window.location.href.match('#([a-zA-Z0-9._]+)$');
        if (m) {
            this.selectedPlugin = m[1];
        }

        const self = this;
        setInterval(() => {
            self.now = new Date();
        }, 1000);

        initEvents();
    },
});

