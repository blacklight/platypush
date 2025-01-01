<template>
  <div class="app-tab monitor-container">
    <div class="header">
      <div class="filter-container">
        <input type="text" v-model="filter" placeholder="Filter actions" />
      </div>

      <div class="btn-container">
        <button @click="running = !running" :title="(running ? 'Pause' : 'Start') + ' capturing'">
          <i :class="running ? 'fa fa-pause' : 'fa fa-play'" />
        </button>

        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
          <DropdownItem :text="follow ? 'Unfollow' : 'Follow'" icon-class="fa fa-eye" @input="follow = !follow" />
          <DropdownItem text="Export Actions Dump" icon-class="fa fa-download" @input="download" />
          <DropdownItem text="Import Actions Dump" icon-class="fa fa-upload" @input="importActions" />
          <DropdownItem text="Clear Completed Actions" icon-class="fa fa-trash"
                        @input="actions = Object.fromEntries(Object.entries(actions).filter(([_, action]) => action.status === 'running'))" />
          <DropdownItem text="Clear Actions" icon-class="fa fa-trash" @input="actions = {}" />
        </Dropdown>
      </div>
    </div>

    <div class="body" ref="body">
      <Loading v-if="loading" />
      <ActionRenderer v-for="(action, index) in filteredActions"
                     :key="index"
                     :index="index"
                     :output="action" />
    </div>

    <div class="footer">
      <Loading v-if="running" />
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import ActionRenderer from "@/components/elements/OutputRenderers/ActionRenderer";
import Loading from "@/components/Loading";
import Utils from '@/Utils'

export default {
  mixins: [Utils],
  components: {
    Dropdown,
    DropdownItem,
    ActionRenderer,
    Loading,
  },

  data() {
    return {
      actions: {},
      error: null,
      filter: '',
      follow: true,
      loading: true,
      running: true,
      ws: null,
      wsRetryTimeout: 500,
      wsRetryTimeoutMax: 30000,
      wsRetryTimer: null,
    }
  },

  computed: {
    filteredActions() {
      const filter = this.filter?.toLowerCase()
      return Object.keys(this.serializedActions || {})
        .filter((id) => {
          if (!filter?.length) {
            return true
          }

          return this.serializedActions[id].includes(filter)
        })
        .map((id) => this.actions[id])
    },

    actionsString() {
      return JSON.stringify(
        Object.values(this.actions || [])
          .sort((a, b) => a.started_at - b.started_at)
          .map((item) => {
            try {
              return JSON.parse(item)
            } catch (err) {
              // Already a string
              return item
            }
          }
        ), null, 2
      )
    },

    serializedActions() {
      return Object.entries(this.actions || {})
        .reduce(
          (acc, [key, item]) => {
            try {
              acc[key] = JSON.stringify(item).toLowerCase()
            } catch (err) {
              // Already a string
              acc[key] = item
            }

            return acc
          }, {}
        )
    },
  },

  methods: {
    download() {
      const blob = new Blob([this.actionsString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `monitor-${new Date().toISOString()}.json`
      a.click()
      URL.revokeObjectURL(url)
    },

    importActions() {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      input.onchange = async () => {
        const file = input.files[0]
        const reader = new FileReader()
        reader.onload = async () => {
          try {
            this.actions = JSON.parse(reader.result)
          } catch (err) {
            this.notify({
              error: true,
              title: 'Error importing actions',
              text: err.toString(),
            })
          }
        }
        reader.readAsText(file)
      }
      input.click()
    },

    initWs() {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
        this.ws = new WebSocket(`${protocol}://${location.host}/ws/monitor`)
        this.ws.onopen = this.onOpen
        this.ws.onmessage = this.onMessage
        this.ws.onerror = this.onError
        this.ws.onclose = this.onClose
      } catch (err) {
        this.onError(err)
      }
    },

    onOpen() {
      this.wsRetryTimeout = 500
      console.info('Monitor websocket opened')
    },

    onMessage(msg) {
      if (!this.running) {
        return
      }

      const action = JSON.parse(msg.data)
      this.actions[action.id] = action
    },

    onClose() {
      this.ws = null

      if (!this.running || !this.wsRetryTimer) {
        return
      }

      if (this.wsRetryTimeout < this.wsRetryTimeoutMax) {
        this.wsRetryTimeout *= 2
      }

      console.info(`Monitor websocket closed, retrying in ${this.wsRetryTimeout / 1000} seconds`)
      this.wsRetryTimer = setTimeout(this.initWs, this.wsRetryTimeout)
    },

    onError(error) {
        this.notify({
          error: true,
          title: 'Monitor websocket error',
          text: error.toString(),
        })

      console.error('Monitor websocket error')
      console.error(error)
    },

    async init() {
      this.initWs()
      this.loading = true

      try {
        this.actions = (await this.request('application.get_pending_actions')).reduce(
          (acc, action) => {
            acc[action.id] = action
            return acc
          }, {}
        )
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    actions: {
      deep: true,
      handler() {
        if (!this.running) {
          return
        }

        this.$nextTick(() => {
          this.$refs.body.scrollTop = this.$refs.body.scrollHeight
        })
      },
    },
  },

  mounted() {
    this.setUrlArgs({ view: 'monitor' })
    this.init()
  },

  unmounted() {
    if (this.ws) {
      try {
        this.ws.close()
      } catch (err) {
        console.debug('Error while closing the monitor websocket')
      }
    }
  },
}
</script>

<style lang="scss" scoped>
@import "./style.scss";
</style>
