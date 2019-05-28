Vue.component('notifications', {
    template: '#tmpl-notifications',
    props: {
        duration: {
            // Default notification duration in milliseconds
            type: Number,
            default: 10000,
        }
    },

    data: function() {
        return {
            index: 0,
            notifications: {},
            timeouts: {},
        };
    },

    methods: {
        create: function(args) {
            var id = this.index++;
            Vue.set(this.notifications, id, args);

            if (args.duration == null) {
                args.duration = this.duration;
            }

            if (args.duration != 0) {
                this.timeouts[id] = setTimeout(this.destroy.bind(null, id), args.duration);
            }
        },

        destroy: function(id) {
            Vue.delete(this.notifications, id);
            delete this.timeouts[id];
        },
    },
});

Vue.component('notification', {
    template: '#tmpl-notification',
    props: ['id','text','html','title','image','link','error','warning'],

    methods: {
        mousein: function(event) {
        },

        mouseout: function(event) {
        },
        clicked: function(event) {
            if (this.link) {
                window.open(this.link, '_blank');
            }

            this.$emit('clicked', this.id);
        },
    },
});

function createNotification(args) {
    window.vm.$refs.notifications.create(args);
}

