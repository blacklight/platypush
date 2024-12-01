<template>
  <a class="event renderer"
     :class="{even: index % 2 === 0, odd: index % 2 !== 0, expanded}"
     :href="href"
     @click.prevent.stop="onClick">
    <div class="header">
      <div class="col-11 title">
        <div class="time-container">
          [<span class="time">{{ time }}</span>] &nbsp;
        </div>
        <div class="type-container">
          <span class="type">{{ type }}</span>
        </div>
      </div>

      <div class="col-1 buttons">
        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
          <DropdownItem text="Raw Event" icon-class="fa fa-file-code" @input="showEditor = true" />
          <DropdownItem text="Copy to Clipboard" icon-class="fa fa-copy" @input="copy" />
        </Dropdown>
      </div>
    </div>

    <div class="body">
      <div class="expanded" @click.stop v-if="expanded">
        <div class="row time">
          <span class="key"><i class="fas fa-clock"></i> Time</span>
          <span class="value scalar">{{ datetime }}</span>
        </div>

        <div class="row type">
          <span class="key"><i class="fas fa-tag"></i> Type</span>
          <span class="value scalar">
            <a v-if="typeDocHref" :href="typeDocHref" target="_blank">{{ type }}</a>
          </span>
        </div>

        <div class="row id">
          <span class="key"><i class="fas fa-id-badge"></i> ID</span>
          <span class="value scalar">{{ output?.id }}</span>
        </div>

        <div class="row origin">
          <span class="key"><i class="fas fa-map-marker-alt"></i> Origin</span>
          <span class="value scalar">{{ output?.origin }}</span>
        </div>

        <div class="row args">
          <span class="key"><i class="fas fa-cogs"></i> Args</span>
          <span class="value object">
            <ObjectRenderer :output="output.args" />
          </span>
        </div>
      </div>
    </div>

    <div class="editor-container" v-if="showEditor">
      <FileEditor :file="type.split('.').pop()"
                  :text="indentedOutput"
                  :visible="true"
                  :uppercase="false"
                  :with-save="false"
                  content-type="json"
                  @close="showEditor = false" />
    </div>
  </a>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import FileEditor from "@/components/File/EditorModal";
import Mixin from './Mixin'
import ObjectRenderer from './ObjectRenderer'

export default {
  mixins: [Mixin],
  components: {
    Dropdown,
    DropdownItem,
    FileEditor,
    ObjectRenderer,
  },

  data() {
    return {
      showEditor: false,
    }
  },

  computed: {
    datetime() {
      const timestamp = this.output?.timestamp || this.output?._timestamp
      if (!timestamp) {
        return ''
      }

      return this.formatDateTime(timestamp)
    },

    indentedOutput() {
      if (!Object.keys(this.output || {})?.length) {
        return ''
      }

      try {
        return JSON.stringify(this.output, null, 2)
      } catch (err) {
        return this.output
      }
    },

    time() {
      const timestamp = this.output?.timestamp || this.output?._timestamp
      if (!timestamp) {
        return ''
      }

      return this.formatTime(timestamp)
    },

    href() {
      const route = this.$route.fullPath
      if (route.match(/&index=\d+/)) {
        return route.replace(/&index=\d+/, `&index=${this.index}`)
      }

      return route + (
        this.index != null ? `&index=${this.index}` : ''
      )
    },

    type() {
      return this.output?.args?.type
    },

    typeDocHref() {
      if (!this.type?.length) {
        return ''
      }

      const parts = this.type
        .replace(/^platypush\.message\.event\./, '')
        .split('.')

      const module = parts.splice(0, parts.length - 1).join('.')
      return `https://docs.platypush.tech/platypush/events/${module}.html#${this.type}`
    },
  },

  methods: {
    async copy() {
      await this.copyToClipboard(this.indentedOutput)
    },

    onClick() {
      this.expanded = !this.expanded
      this.setUrlArgs({index: this.expanded && this.index != null ? this.index : undefined})
    },
  },

  mounted() {
    const args = this.getUrlArgs()
    if (args.index == this.index?.toString()) {
      this.expanded = true
    }
  },
}
</script>

<style lang="scss" scoped>
@import "./style.scss";

.renderer {
  width: 100%;

  .header {
    .title {
      display: flex;
      flex-direction: row;
    }

    .buttons {
      display: flex;
      justify-content: flex-end;
    }
  }

  .body {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: $default-bg-3;
  }

  .expanded {
    width: 100%;
    max-width: 800px;
    margin: 0.5em auto;
    padding: 0 1em;
    border-radius: 0.5em;
    border: $default-border-2;
  }
}
</style>
