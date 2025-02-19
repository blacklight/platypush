<template>
  <div class="app-tab events-container">
    <div class="header">
      <div class="filter-container">
        <input type="text" v-model="filter" placeholder="Filter events" />
      </div>

      <div class="btn-container">
        <button @click="running = !running" :title="(running ? 'Pause' : 'Start') + ' capturing'">
          <i :class="running ? 'fa fa-pause' : 'fa fa-play'" />
        </button>

        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
          <DropdownItem :text="follow ? 'Unfollow' : 'Follow'" icon-class="fa fa-eye" @input="follow = !follow" />
          <DropdownItem text="Export Events" icon-class="fa fa-download" @input="download" />
          <DropdownItem text="Clear Events" icon-class="fa fa-trash" @input="clear" />
        </Dropdown>
      </div>
    </div>

    <div class="body" ref="body">
      <EventRenderer v-for="(event, index) in filteredEvents"
                     :key="index"
                     :index="index"
                     :output="event" />
    </div>

    <div class="footer">
      <Loading v-if="running" />
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import EventRenderer from "@/components/elements/OutputRenderers/EventRenderer";
import Loading from "@/components/Loading";
import Utils from '@/Utils'
import { bus } from "@/bus";

export default {
  mixins: [Utils],
  components: {
    Dropdown,
    DropdownItem,
    EventRenderer,
    Loading,
  },

  data() {
    return {
      filter: '',
      follow: true,
      output: [],
      running: true,
      error: null,
    }
  },

  computed: {
    filteredEvents() {
      const filter = this.filter?.toLowerCase()
      return Object.keys(this.serializedEvents)
        .filter((i) => {
          if (!filter?.length) {
            return true
          }

          return this.serializedEvents[i].includes(filter)
        })
        .map((i) => this.outputObjects[i])
    },

    outputString() {
      return this.outputStrings.join('\n')
    },

    outputObjects() {
      return this.output.map((item) => {
        try {
          return JSON.parse(item)
        } catch (err) {
          return item
        }
      })
    },

    outputStrings() {
      return this.output.map((item) => {
        try {
          return JSON.stringify(item)
        } catch (err) {
          return item
        }
      })
    },

    serializedEvents() {
      return this.outputObjects.map((item) => {
        try {
          return JSON.stringify(item).toLowerCase()
        } catch (err) {
          return item
        }
      })
    },
  },

  methods: {
    clear() {
      this.output = []
    },

    download() {
      const blob = new Blob([this.outputString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `events-${new Date().toISOString()}.json`
      a.click()
      URL.revokeObjectURL(url)
    },

    onEvent(msg) {
      if (!this.running) {
        return
      }

      this.output.push(msg)
    },
  },

  watch: {
    output: {
      deep: true,
      handler() {
        if (!this.follow) {
          return
        }

        this.$nextTick(() => {
          this.$refs.body.scrollTop = this.$refs.body.scrollHeight
        })
      },
    },
  },

  mounted() {
    this.setUrlArgs({ view: 'events' })
    bus.on('event', this.onEvent)
  },
}
</script>

<style lang="scss" scoped>
@import "./style.scss";
</style>
