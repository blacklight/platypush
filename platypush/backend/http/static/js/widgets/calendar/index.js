Vue.component('calendar', {
    template: '#tmpl-widget-calendar',
    props: ['config'],

    data: function() {
        return {
            events: [],
        };
    },

    methods: {
        refresh: async function() {
            this.events = (await request('calendar.get_upcoming_events')).map(event => {
                if (event.start)
                    event.start = new Date(event.start.dateTime || event.start.date);
                if (event.end)
                    event.end = new Date(event.end.dateTime || event.end.date);

                return event;
            });
        },

        formatDate: function(date) {
            return date.toDateString().substring(0, 10);
        },

        formatTime: function(date) {
            return date.toTimeString().substring(0, 5);
        },
    },

    mounted: function() {
        this.refresh();
        setInterval(this.refresh, 600000);
    },
});

