<template>
  <div id="dashboard" class="columns is-mobile" :class="{blurred: loading}" :style="style">
    <keep-alive v-for="(widget, i) in widgets" :key="i">
      <Widget :style="widget.style">
        <component :is="widget.component" v-bind="widget.props" />
      </Widget>
    </keep-alive>
  </div>

  <Loading v-if="loading" />
</template>

<script>
import { defineAsyncComponent } from 'vue'
import Utils from '@/Utils'
import Loading from "@/components/Loading";
import Widget from "@/widgets/Widget";

export default {
  name: 'Dashboard',
  mixins: [Utils],
  components: {Widget, Loading},
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
      widgets: [],
      loading: false,
      style: undefined,
    }
  },

  methods: {
    parseTemplate(name, tmpl) {
      const node = new DOMParser().parseFromString(tmpl, 'text/xml').childNodes[0]
      const self = this;
      this.style = node.attributes.style ? node.attributes.style.nodeValue : undefined;

      [...node.children].forEach((el) => {
        const component = defineAsyncComponent(
            () => import(`@/widgets/${el.nodeName}/Index`)
        )

        const style = el.attributes.style ? el.attributes.style.nodeValue : undefined;
        const attrs = [...el.attributes].reduce((obj, node) => {
          if (node.nodeName !== 'style') {
            obj[node.nodeName] = node.nodeValue
          }

          return obj
        }, {})

        self.$options.components[el.nodeName] = component
        self.widgets.push({
          component: component,
          style: style,
          props: attrs || {},
        })
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
      setTimeout(() => {
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
  margin: 0;
  padding: 1em 1em 0 1em;
  background: $dashboard-bg;
  background-size: cover;

  .blurred {
    filter: blur(0.075em);
  }
}
</style>
