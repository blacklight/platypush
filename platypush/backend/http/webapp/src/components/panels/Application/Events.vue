<template>
  <div class="events-container">
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
$header-height: 3.25em;
$header-margin: 0.25em;
$footer-height: 2em;
$btn-container-width: 5em;

.events-container {
  width: 100%;
  height: 100%;
  position: relative;
  margin: 0;
  background: $background-color;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow: hidden;

  .header {
    width: 100%;
    height: $header-height;
    margin-bottom: $header-margin;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    background: $default-bg-4;
    padding: 0 0.5em;
    box-shadow: $border-shadow-bottom;

    .filter-container {
      width: calc(100% - #{$btn-container-width});
    }

    .btn-container {
      width: $btn-container-width;
      display: flex;
      flex-direction: row;
      justify-content: flex-end;

      button {
        background: none;
        border: none;
        padding: 0.5em;
        margin-right: 0.5em;
      }
    }

    input[type="text"] {
      width: 100%;
      max-width: 40em;
    }
  }

  .body {
    width: 100%;
    height: calc(100% - #{$header-height} - #{$header-margin} - #{$footer-height});
    position: relative;
    margin: 0 0 $footer-height 0;
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    overflow: auto;
  }

  .footer {
    width: 100%;
    height: $footer-height;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    position: absolute;
    bottom: 0;
    font-size: 0.75em;
    background: $default-bg-4;
    box-shadow: $border-shadow-top;
  }
}
</style>
