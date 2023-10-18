<template>
  <section class="doc">
    <header>
      <h2>
        <a class="title" :href="extension.doc_url" target="_blank">
          <i class="icon fas fa-book" />
          {{ extension.name }}
        </a>
      </h2>
    </header>

    <article v-if="doc" @click="onDocClick">
      <div class="doc-content" v-html="doc" />

      <div class="actions" v-if="Object.keys(extension.actions || {}).length > 0">
        <h3>
          <i class="icon fas fa-play" /> &nbsp;
          Actions
        </h3>

        <ul>
          <li class="action" v-for="actionName in actionNames" :key="actionName">
            <a :href="`/#execute?action=${extension.name}.${actionName}`">
              {{ extension.name }}.{{ actionName }}
            </a>
          </li>
        </ul>
      </div>

      <div class="events" v-if="Object.keys(extension.events || {}).length > 0">
        <h3>
          <i class="icon fas fa-flag" /> &nbsp;
          Events
        </h3>

        <ul>
          <li class="event" v-for="eventName in eventNames" :key="eventName">
            <a :href="extension.events[eventName].doc_url" target="_blank">
              {{ eventName }}
            </a>
          </li>
        </ul>
      </div>
    </article>
  </section>
</template>

<script>
import Utils from "@/Utils"
import { bus } from "@/bus";

export default {
  name: "Doc",
  mixins: [Utils],
  props: {
    extension: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      doc: null,
      localPageRegex: new RegExp('^/?#.*$'),
    }
  },

  computed: {
    actionNames() {
      return Object.keys(this.extension.actions).sort()
    },

    eventNames() {
      return Object.keys(this.extension.events).sort()
    },
  },

  methods: {
    async parseDoc() {
      if (!this.extension.doc?.length)
        return null

      return await this.request(
        'utils.rst_to_html',
        {text: this.extension.doc}
      )
    },

    refreshDoc() {
      this.parseDoc().then(doc => this.doc = doc)
    },

    // Intercept links to the documentation and replace them with
    // in-app connections, or opens them in a new tab if they
    // don't point to an internal documentation page.
    onDocClick(event) {
      if (event.target.tagName.toLowerCase() !== 'a')
        return true

      event.preventDefault()
      const href = event.target.getAttribute('href')
      if (!href)
        return true

      if (href.match(this.localPageRegex)) {
        window.location.href = href
        return true
      }

      const match = href.match(/^https:\/\/docs\.platypush\.tech\/platypush\/(plugins|backend)\/([\w.]+)\.html#?.*$/)
      if (!match) {
        event.preventDefault()
        window.open(href, '_blank')
        return true
      }

      let [type, name] = match.slice(1)
      if (type === 'backend')
        name = `backend.${name}`

      bus.emit('update:extension', name)
      event.preventDefault()
    },
  },

  mounted() {
    this.refreshDoc()
    this.$watch('extension.doc', this.refreshDoc)
  },
}
</script>

<style lang="scss" scoped>
$header-height: 3em;

section {
  height: 100%;

  header {
    height: $header-height;
    padding: 0.5em;
    border-bottom: 1px solid $border-color-2;

    h2 {
      margin: 0;
      padding: 0;
      font-size: 1.25em;
    }
  }

  article {
    height: calc(100% - #{$header-height});
    padding: 0.5em;
    overflow: auto;

    :deep(ul) {
      margin-left: 1em;

      li {
        list-style: disc;
      }
    }
  }

  .actions, .events {
    padding: 0.5em;
    overflow: auto;

    h3 {
      width: calc(100% - 1em);
      margin: 0 -0.5em;
      padding: 0 0.5em;
      font-size: 1.25em;
      opacity: 0.85;
      border-bottom: 1px solid $border-color-1;
    }

    ul {
      display: flex;
      flex-direction: column;
      margin: 0;

      li {
        width: 100%;
        display: block;
        margin: 0.5em 0;
        list-style: none;

        a {
          width: 100%;
          display: block;
        }
      }
    }

    pre {
      margin: 0;
    }
  }
}
</style>
