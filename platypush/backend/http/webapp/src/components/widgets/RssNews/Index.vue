<template>
  <div class="rss-news">
    <div class="article" v-if="currentArticle">
      <div class="source" v-text="currentArticle.source"></div>
      <div class="title" v-text="currentArticle.title"></div>
      <div class="published" v-text="new Date(currentArticle.published).toDateString() + ', ' + new Date(currentArticle.published).toTimeString().substring(0,5)"></div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

/**
 * In order to use this widget you need to configure the `backend.http.poll` backend to
 * poll a list of RSS sources.
 */
export default {
  name: "RssNews",
  mixins: [Utils],
  props: {
    // Database engine string pointing to the source of the RSS feeds.
    // If not otherwise configured, you should set this to
    // `sqlite:///<HOME>/.local/share/platypush/feeds/rss.db`.
    db: {
      type: String,
      required: true,
    },

    // Maximum number of items to be shown in a cycle.
    limit: {
      type: Number,
      required: false,
      default: 25,
    },

    // How long an entry should be displayed before moving to the next one.
    refreshSeconds: {
      type: Number,
      required: false,
      default: 15,
    },
  },

  data: function() {
    return {
      articles: [],
      queue: [],
      currentArticle: undefined,
    }
  },

  methods: {
    refresh: async function() {
      if (!this.queue.length) {
        this.articles = await this.request('db.select', {
          engine: this.db,
          query: `
            select s.title as source, e.title, e.summary,
                   strftime('%Y-%m-%dT%H:%M:%fZ', e.published) as published
            from FeedEntry e join FeedSource s
              on e.source_id = s.id order by e.published desc limit ${this.limit}`,
        })

        this.queue = [...this.articles]
      }

      if (!this.queue.length)
        return

      this.currentArticle = this.queue.pop()
    },
  },

  mounted: function() {
    this.refresh()
    setInterval(this.refresh, parseInt((this.refreshSeconds*1000).toFixed(0)))
  },
}
</script>

<style lang="scss" scoped>
.rss-news {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;

  .article {
    width: 90%;
    padding: 0 2em;

    .source {
      font-size: 1.7em;
      font-weight: bold;
      margin-bottom: .5em;
    }

    .title {
      font-size: 1.7em;
      font-weight: normal;
      margin-bottom: .5em;
    }

    .published {
      text-align: right;
      font-size: 1em;
    }
  }
}
</style>
