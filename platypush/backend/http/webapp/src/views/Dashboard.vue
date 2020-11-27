<template>
  <Loading v-if="loading" />

  <div id="dashboard" class="columns is-mobile" :class="classes" :style="style">
    <Row v-for="(row, i) in rows" :key="i" :class="row.class" :style="row.style">
      <keep-alive v-for="(widget, j) in row.widgets" :key="j">
        <Widget :style="widget.style" :class="widget.class">
          <component :is="widget.component" v-bind="widget.props" />
        </Widget>
      </keep-alive>
    </Row>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import Utils from '@/Utils'
import Loading from "@/components/Loading";
import Row from "@/components/widgets/Row";
import Widget from "@/components/widgets/Widget";

export default {
  name: 'Dashboard',
  mixins: [Utils],
  components: {Widget, Loading, Row},
  props: {
    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      required: false,
      default: 0,
    },
  },

  data() {
    return {
      rows: [],
      loading: false,
      style: undefined,
      class: undefined,
    }
  },

  computed: {
    classes() {
      return this.class
    },
  },

  methods: {
    parseTemplate(name, tmpl) {
      const node = new DOMParser().parseFromString(tmpl, 'text/xml').childNodes[0]
      const self = this
      this.style = node.attributes.style ? node.attributes.style.nodeValue : undefined
      this.class = node.attributes.class ? node.attributes.class.nodeValue : undefined

      this.rows = [...node.getElementsByTagName('Row')].map((row) => {
        return {
          style: row.attributes.style ? row.attributes.style.nodeValue : undefined,
          class: row.attributes.class ? row.attributes.class.nodeValue : undefined,
          widgets: [...row.children].map((el) => {
            const component = defineAsyncComponent(
                () => import(`@/components/widgets/${el.nodeName}/Index`)
            )

            const style = el.attributes.style ? el.attributes.style.nodeValue : undefined
            const classes = el.attributes.class ? el.attributes.class.nodeValue : undefined
            const attrs = [...el.attributes].reduce((obj, node) => {
              if (node.nodeName !== 'style') {
                obj[node.nodeName] = node.nodeValue
              }

              return obj
            }, {})

            const widget = {
              component: component,
              style: style,
              class: classes,
              props: attrs || {},
            }

            self.$options.components[el.nodeName] = component
            return widget
          })
        }
      })

      this.loading = false
    },

    async refreshDashboard() {
      this.loading = true
      this.widgets = []
      const name = this.$route.params.name
      const template = (await this.request('config.get_dashboard', { name: name }))

      if (!template) {
        this.error(`Dashboard ${name} not found`)
      }

      this.parseTemplate(name, template)
    },
  },

  mounted() {
    this.refreshDashboard()
    if (this.refreshSeconds) {
      const self = this
      setInterval(() => {
        self.refreshDashboard()
      }, parseInt((this.refreshSeconds*1000).toFixed(0)))
    }
  }
}
</script>

<style lang="scss" scoped>
#dashboard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 1em 1em 0 1em;
  background: $dashboard-bg;
  background-size: cover;

  .blurred {
    filter: blur(0.075em);
  }
}
</style>

<style>
html {
  overflow: auto !important;
}
</style>
