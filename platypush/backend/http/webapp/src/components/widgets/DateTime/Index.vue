<template>
  <div class="date-time">
    <div class="date" v-text="formatDate(now)" v-if="_showDate" />
    <div class="time" v-text="formatTime(now, _showSeconds)" v-if="_showTime" />
  </div>
</template>

<script>
import Utils from "@/Utils";

// Widget to show date and time
export default {
  name: 'DateTime',
  mixins: [Utils],
  props: {
    // If false then don't display the date.
    showDate: {
      required: false,
      default: true,
    },

    // If false then don't display the time.
    showTime: {
      required: false,
      default: true,
    },

    // If false then don't display the seconds.
    showSeconds: {
      required: false,
      default: true,
    },
  },

  computed: {
    _showTime() {
      return this.parseBoolean(this.showTime)
    },

    _showDate() {
      return this.parseBoolean(this.showDate)
    },

    _showSeconds() {
      return this.parseBoolean(this.showSeconds)
    },
  },

  data: function() {
    return {
      now: new Date(),
    };
  },

  methods: {
    refreshTime() {
      this.now = new Date()
    },
  },

  mounted: function() {
    this.refreshTime()
    setInterval(this.refreshTime, 1000)
  },
}
</script>

<style lang="scss" scoped>
.date-time {
  .date {
    font-size: 1.3em;
  }

  .time {
    font-size: 2em;
  }
}
</style>
