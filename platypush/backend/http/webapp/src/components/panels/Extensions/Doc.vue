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

    <article v-html="doc" v-if="doc" @click="onDocClick" />
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
    }
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
      if (!event.target.tagName.toLowerCase() === 'a')
        return

      event.preventDefault()
      const href = event.target.getAttribute('href')
      if (!href)
        return

      const match = href.match(/^https:\/\/docs\.platypush\.tech\/platypush\/(plugins|backend)\/([\w.]+)\.html#?.*$/)
      if (!match) {
        event.preventDefault()
        window.open(href, '_blank')
        return
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
}
</style>
