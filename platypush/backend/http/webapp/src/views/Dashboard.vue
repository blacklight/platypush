<template>
  <Loading v-if="loading" />

  <div id="dashboard" class="col-12" :class="classes" :style="style">
    <Row v-for="(row, i) in rows" :key="i" :class="row.class" :style="row.style">
      <keep-alive v-for="(widget, j) in row.widgets" :key="j">
        <Widget :style="widget.style" :class="widget.class">
          <component :is="widget.component" v-bind="getWidgetProps(widget)" />
        </Widget>
      </keep-alive>
    </Row>
  </div>
</template>

<script>
import { defineAsyncComponent, shallowRef } from 'vue'
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

    _refreshSeconds() {
      return parseFloat(this.refreshSeconds) || 0
    },
  },

  methods: {
    getWidgetProps(widget) {
      const props = {...widget.props}
      if (props.class)
        delete props.class

      return props
    },

    parseTemplate(tmpl) {
      const node = new DOMParser().parseFromString(tmpl, 'text/xml').childNodes[0]
      const self = this
      this.style = node.attributes.style?.nodeValue
      this.class = node.attributes.class?.nodeValue

      this.rows = [...node.getElementsByTagName('Row')].map((row) => {
        return {
          style: row.attributes.style?.nodeValue,
          class: row.attributes.class?.nodeValue,
          widgets: [...row.children].map((el) => {
            const component = shallowRef(
              defineAsyncComponent(
                () => import(`@/components/widgets/${el.nodeName}/Index`)
              )
            )

            const style = el.attributes.style?.nodeValue
            const classes = el.attributes.class?.nodeValue
            const attrs = [...el.attributes].reduce((obj, node) => {
              if (node.nodeName !== 'style') {
                obj[node.nodeName] = node.nodeValue
              }

              return obj
            }, {
              content: el.innerHTML,
            })

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
        this.notifyError(`Dashboard ${name} not found`)
      }

      this.parseTemplate(template)
    },
  },

  mounted() {
    this.refreshDashboard()
    if (this._refreshSeconds) {
      const self = this
      setInterval(() => {
        self.refreshDashboard()
      }, parseInt((this._refreshSeconds*1000).toFixed(0)))
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~lato-font/scss/public-api";
$lato-font-path: "~lato-font/fonts";

@include lato-include-font('medium');

#dashboard {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 1em 1em 0 1em;
  background: $dashboard-bg;
  background-size: cover;
  font-family: Lato, proxima-nova, Helvetica Neue, Arial, sans-serif;

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
