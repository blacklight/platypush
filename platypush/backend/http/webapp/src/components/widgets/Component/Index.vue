<template>
  <div class="component-widget">
    <Loading v-if="loading" />
    <div class="container" ref="container" />
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import components from './index'
import { createApp, h } from "vue";
import mitt from 'mitt';

const bus = mitt();

export default {
  name: "Elements",
  components: {Loading},
  mixins: [Utils],
  props: {
    content: {
      type: String,
    },
  },

  data() {
    return {
      loading: false,
      unwatch: null,
    }
  },

  methods: {
    _parseActions(element) {
      const actionsTags = [...element.children].filter((node) => node.tagName?.toLowerCase() === 'actions')
      const children = actionsTags?.length ? actionsTags[0].children : element.children
      const actionTags = [...children].filter((node) => node.tagName?.toLowerCase() === 'action')

      if (!actionTags?.length)
        return

      return [...actionTags]
          .map((actionTag) => {
            return {
              action: actionTag.attributes.name.value,
              args: [...actionTag.children].reduce((obj, arg) => {
                let value = undefined
                try {
                  value = JSON.parse(arg.innerText)
                } catch (e) {
                  if (arg.innerText?.length)
                    value = arg.innerText
                }

                obj[arg.tagName.toLowerCase()] = value
                return obj
              }, {}),
            }
          })
    },

    _parseVars(element) {
      const varsTags = [...element.children].filter((node) => node.tagName?.toLowerCase() === 'vars')
      if (!varsTags?.length)
        return

      return [...varsTags[0].children].reduce((vars, varTag) => {
        let value = undefined
        try {
          value = JSON.parse(varTag.innerText)
        } catch (e) {
          if (varTag.innerText?.length)
            value = varTag.innerText
        }
        vars[varTag.tagName.toLowerCase()] = value
        return vars
      }, {})
    },

    _parseHandlers(element) {
      const handlers = {}
      const parseHndlScript = (hndlText) => {
        return (app) => {
          return eval(`// noinspection JSUnusedLocalSymbols
          (async function (self) {
            ${hndlText}
          })`)(app)
        }
      }

      const parseEventHndl = (hndlText) => {
        return (app) => {
          return (event) => {
            return eval(`// noinspection JSUnusedLocalSymbols
            (async function (self, event) {
              ${hndlText}
            })`)(app, event)
          }
        }
      }

      const hndlTags = [...element.children].filter((node) => node.tagName?.toLowerCase() === 'handlers')
      if (hndlTags?.length) {
        const mounted = [...hndlTags[0].children].filter((node) => node.tagName?.toLowerCase() === 'mounted')
        if (mounted?.length)
          handlers.mounted = parseHndlScript(mounted[0].innerText)

        const refresh = [...hndlTags[0].children].filter((node) => node.tagName?.toLowerCase() === 'refresh')
        if (refresh?.length) {
          handlers.refresh = {
            handler: parseHndlScript(refresh[0].innerText),
            interval: refresh[0].attributes.interval?.value || 10,
          }
        }

        const events = [...hndlTags[0].children].filter((node) => node.tagName?.toLowerCase() === 'event')
        if (events?.length)
          handlers.events = events.reduce((events, hndlTag) => {
            events[hndlTag.attributes.type.value] = parseEventHndl(hndlTag.innerText)
            return events
          }, {})
      }

      const actionsTags = [...element.children].filter((node) => node.tagName?.toLowerCase() === 'actions')
      if (actionsTags?.length) {
        const beforeActionsTags = [...actionsTags[0].children].filter((node) => node.tagName?.toLowerCase() === 'before')
        if (beforeActionsTags?.length)
          handlers.beforeActions = parseHndlScript(beforeActionsTags[0].innerText)

        const afterActionsTags = [...actionsTags[0].children].filter((node) => node.tagName?.toLowerCase() === 'after')
        if (afterActionsTags?.length)
          handlers.afterActions = parseHndlScript(afterActionsTags[0].innerText)
      }

      return handlers
    },

    _parseProps(element) {
      return [...element.attributes].reduce((obj, attr) => {
        obj[attr.name] = attr.value
        return obj
      }, {})
    },

    propagateEvent(event) {
      bus.emit('event', event)
    },

    _addEventHandler() {
      this.unwatch = this.subscribe((event) => {
        bus.emit('event', event)
      })
    },

    _removeEventHandler() {
      if (this.unwatch) {
        this.unwatch()
        this.unwatch = null
      }
    },
  },

  mounted() {
    this.loading = true
    this._addEventHandler()

    try {
      this.$refs.container.innerHTML = this.content

      Object.entries(components).forEach(([name, component]) => {
        this.$options.components[name] = component;
        [...this.$refs.container.getElementsByTagName(name)].forEach((element) => {
          const props = this._parseProps(element)
          props.actions = this._parseActions(element)
          props.handlers = this._parseHandlers(element)
          props._vars = this._parseVars(element)

          createApp({
            render() { return h(component, props) },
            data() {
              return { bus: bus }
            },
          }).mount(element)
        })
      })

      for (const tagName of ['handlers', 'actions', 'vars'])
        this.$refs.container.getElementsByTagName(tagName).forEach((hndlTag) => {
          hndlTag.parentNode.removeChild(hndlTag)
        })
    } finally {
      this.loading = false
    }
  },

  unmounted() {
    this._removeEventHandler()
  },
}
</script>

<style lang="scss" scoped>
.component-widget {
  margin: -.75em 0 0 -.75em !important;
  padding: 0;
  width: calc(100% + 1.5em);
  height: calc(100% + 1.5em);
}
</style>
