<template>
  <div class="calendar">
    <Loading v-if="loading" />

    <div class="no-events" v-else-if="!events.length">
      No events found
    </div>

    <div class="event upcoming-event" v-else-if="events.length > 0">
      <div class="date" v-text="formatDate(events[0].start)"></div>
      <div class="summary" v-text="events[0].summary"></div>
      <div class="time">
        {{ formatTime(events[0].start, false) }} -
        {{ formatTime(events[0].end, false) }}
      </div>
    </div>

    <div class="event-list" v-if="events.length > 1">
      <div class="event" v-for="event in events.slice(1, maxEvents)" :key="event.id">
        <div class="date col-2" v-text="formatDate(event.start)"></div>
        <div class="time col-2" v-text="formatTime(event.start, false)"></div>
        <div class="summary col-8" v-text="event.summary"></div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "Calendar",
  components: {Loading},
  mixins: [Utils],
  props: {
    // Maximum number of events to be rendered.
    maxEvents: {
      type: Number,
      required: false,
      default: 10,
    },

    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      required: false,
      default: 600,
    },
  },

  data: function() {
    return {
      events: [],
      loading: false,
    }
  },

  methods: {
    refresh: async function() {
      this.loading = true

      try {
        this.events = (await this.request('calendar.get_upcoming_events')).map(event => {
          if (event.start)
            event.start = new Date(event.start.dateTime || event.start.date)
          if (event.end)
            event.end = new Date(event.end.dateTime || event.end.date)

          return event
        })
      } finally {
        this.loading = false
      }
    },
  },

  mounted: function() {
    this.refresh()
    setInterval(this.refresh, parseInt((this.refreshSeconds*1000).toFixed(0)))
  },
}
</script>

<style lang="scss" scoped>
.calendar {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;

  .no-events {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75em;
  }

  .event {
    font-size: 1.1em;
  }

  .event-list {
    margin-top: 2em;
  }

  .upcoming-event {
    text-align: center;
    margin-bottom: .15em;
    font-size: 1.2em;

    .date {
      font-size: 1.1em;
    }

    .summary {
      text-transform: uppercase;
      font-size: 1.3em;
    }
  }
}
</style>