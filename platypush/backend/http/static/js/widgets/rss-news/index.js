Vue.component('rss-news', {
    template: '#tmpl-widget-rss-news',
    props: ['config'],

    data: function() {
        return {
            articles: [],
            queue: [],
            currentArticle: undefined,
        };
    },

    methods: {
        refresh: async function() {
            if (!this.queue.length) {
                this.articles = await request('db.select', {
                    engine: this.config.db,
                    query: "select s.title as source, e.title, e.summary, " +
                    "strftime('%Y-%m-%dT%H:%M:%fZ', e.published) as published " +
                    "from FeedEntry e join FeedSource s " +
                    "on e.source_id = s.id order by e.published desc limit " +
                    ('limit' in this.config ? this.config.limit : 10)
                });

                this.queue = [...this.articles];
            }

            if (!this.queue.length)
                return;

            this.currentArticle = this.queue.pop();
        },
    },

    mounted: function() {
        this.refresh();
        setInterval(this.refresh, 'refresh_seconds' in this.config ? this.config.refresh_seconds*1000 : 15000);
    },
});

