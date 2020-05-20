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
            fullscreen: false,
        };
    },

    methods: {
        enterFullScreen: function() {
            const self = this;
            enterFullScreen().then(() => {
                self.fullscreen = true;
            });
        },

        exitFullScreen: function() {
            const self = this;
            exitFullscreen().finally(() => {
                self.fullscreen = false;
            });
        },

        toggleFullScreen: function() {
            if (this.fullscreen) {
                this.exitFullScreen();
            } else {
                this.enterFullScreen();
            }
        },
    },

    created: function() {
        let m = window.location.href.match('#([a-zA-Z0-9._]+)$');
        if (m) {
            this.selectedPlugin = m[1];
        }

        m = window.location.href.match('[?&]fs=([01])');
        if (m) {
            this.fullscreen = !parseInt(m[1]);
            this.toggleFullScreen();
        }

        const self = this;
        setInterval(() => {
            self.now = new Date();
        }, 1000);

        initEvents();
    },
});

