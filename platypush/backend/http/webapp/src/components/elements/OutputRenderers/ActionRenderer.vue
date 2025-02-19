<template>
  <a class="action renderer"
     :class="{even: index % 2 === 0, odd: index % 2 !== 0, expanded}"
     :href="href">
    <div class="header" @click.prevent.stop="onClick">
      <div class="col-11 title">
        <div class="time-container">
          [<span class="time">{{ time }}</span>] &nbsp;
        </div>
        <div class="status icon-container" v-if="output.status">
          <i class="fas fa-check-circle" :class="statusClass" v-if="output.status === 'completed'" />
          <i class="fas fa-spinner fa-spin" :class="statusClass" v-else-if="output.status === 'running'" />
          <i class="fas fa-exclamation-circle" :class="statusClass" v-else />
        </div>
        <div class="icon-container" v-if="pluginName">
          <ExtensionIcon :name="pluginName" size="1.25em" />
        </div>
        <div class="action">
          <span class="type">{{ output.action }}</span>
        </div>
        <div class="running-time" v-if="runningTime">
          (<span class="value" :class="runningTimeClass">{{ displayRunningTime }}</span>)
        </div>
      </div>

      <div class="col-1 buttons">
        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
          <DropdownItem text="Raw Action" icon-class="fa fa-file-code" @input="showEditor = true" />
          <DropdownItem text="Copy to Clipboard" icon-class="fa fa-copy" @input="copy" />
        </Dropdown>
      </div>
    </div>

    <div class="body" @click.stop>
      <div class="expanded" v-if="expanded">
        <div class="row time">
          <span class="key"><i class="fas fa-clock"></i> Start Time</span>
          <span class="value scalar">{{ startedAt }}</span>
        </div>

        <div class="row time">
          <span class="key"><i class="fas fa-stopwatch"></i> Running Time</span>
          <span class="value scalar running-time" :class="runningTimeClass">{{ displayRunningTime }}</span>
        </div>

        <div class="row status">
          <span class="key"><i class="fas fa-check-circle" /> Status</span>
          <span class="value scalar" :class="statusClass">{{ output.status }}</span>
        </div>

        <div class="row type">
          <span class="key"><i class="fas fa-tag"></i> Action</span>
          <span class="value scalar">
            <span class="monospace">{{ output.action }}</span>
          </span>
        </div>

        <div class="row origin" v-if="output.origin">
          <span class="key"><i class="fas fa-map-marker-alt"></i> Origin</span>
          <span class="value scalar">{{ output?.origin }}</span>
        </div>

        <div class="row args" v-if="Object.keys(output.args || {}).length">
          <span class="key"><i class="fas fa-cogs"></i> Args</span>
          <span class="value object">
            <ObjectRenderer :output="output.args" />
          </span>
        </div>

        <div class="row args" v-if="output.response">
          <span class="key"><i class="fas fa-reply"></i> Response</span>
          <span class="value object">
            <span class="monospace" v-if="output.response == null || typeof output.response !== 'object'">{{ output.response }}</span>
            <ObjectRenderer :output="output.response" v-else />
          </span>
        </div>
      </div>
    </div>
  </a>

  <div class="editor-container" v-if="showEditor">
    <FileEditor :file="output.action"
                :text="indentedOutput"
                :visible="true"
                :uppercase="false"
                :with-save="false"
                content-type="json"
                @close="showEditor = false" />
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import ExtensionIcon from "@/components/elements/ExtensionIcon"
import FileEditor from "@/components/File/EditorModal";
import Mixin from './Mixin'
import ObjectRenderer from './ObjectRenderer'

export default {
  mixins: [Mixin],
  components: {
    Dropdown,
    DropdownItem,
    ExtensionIcon,
    FileEditor,
    ObjectRenderer,
  },

  data() {
    return {
      showEditor: false,
    }
  },

  computed: {
    startedAt() {
      const timestamp = this.output?.started_at || this.output?.timestamp
      if (!timestamp) {
        return ''
      }

      return this.formatDateTime(timestamp)
    },

    completedAt() {
      const timestamp = this.output?.completed_at
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
      const timestamp = this.output?.started_at || this.output?.timestamp
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

    pluginName() {
      if (!this.output?.action) {
        return null
      }

      const tokens = this.output.action.split('.')
      return tokens.slice(0, tokens.length - 1).join('.')
    },

    runningTime() {
      if (!(this.output?.completed_at && this.output?.started_at)) {
        return null
      }

      return this.output.completed_at - this.output.started_at
    },

    displayRunningTime() {
      const diff = this.runningTime
      if (diff < 0) {
        return null
      }

      if (diff < 1) {
        return `${(diff * 1000).toFixed(1)}ms`
      }

      if (diff < 60) {
        return `${diff.toFixed(1)}s`
      }

      return `${(diff / 60).toFixed(0)}m${(diff % 60).toFixed(0)}s`
    },

    runningTimeClass() {
      if (!this.runningTime) {
        return null
      }

      if (this.runningTime < 1) {
        return 'ok'
      }

      if (this.runningTime < 10) {
        return 'warning'
      }

      return 'error'
    },

    statusClass() {
      if (!this.output?.status) {
        return null
      }

      if (this.output.status === 'completed') {
        return 'success'
      }

      if (this.output.status === 'running') {
        return 'running'
      }

      return 'error'
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
      align-items: center;
      justify-content: flex-start;

      .action {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin-left: 0.25em;
      }

      .running-time {
        @include until($tablet) {
          display: none;
        }
      }
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

  .icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 0.25em;
  }

  .status {
    .success, &.success {
      color: #00bb00;
    }

    .running, &.running {
      color: #bbbb00;
    }

    .error, &.error {
      color: #bb0000;
    }
  }

  .running-time {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin-top: 0.1em;
    margin-left: 0.5em;
    font-size: 0.85em;

    .ok, &.ok {
      color: #00aa00;
    }

    .warning, &.warning {
      color: #999900;
    }

    .error, &.error {
      color: #aa0000;
    }
  }

  :deep(.extension-icon) {
    display: flex;
  }
}
</style>
