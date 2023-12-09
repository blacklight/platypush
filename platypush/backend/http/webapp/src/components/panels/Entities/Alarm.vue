<template>
  <div class="entity alarm-container">
    <div class="head" :class="{collapsed: collapsed}">
      <div class="icon col-1">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label col-6">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-and-toggler col-7" @click.stop="collapsed = !collapsed">
        <div class="value" v-if="!value.enabled">Disabled</div>
        <div class="value" v-else-if="isRunning">Running</div>
        <div class="value" v-else-if="isSnoozed">Snoozed</div>
        <div class="value next-run" v-else-if="nextRun">
          <div class="date" v-text="nextRun.toDateString()" />
          <div class="time" v-text="nextRun.toLocaleTimeString()" />
        </div>

        <div class="collapse-toggler" @click.stop="collapsed = !collapsed">
          <i class="fas" :class="{'fa-chevron-down': collapsed, 'fa-chevron-up': !collapsed}" />
        </div>
      </div>
    </div>

    <div class="body children" v-if="!collapsed" @click.stop="prevent">
      <div class="child">
        <label :for="enableInputId" class="label">
          <div class="name col-s-12 col-m-6">Enabled</div>
          <div class="value col-s-12 col-m-6">
            <ToggleSwitch :id="enableInputId" :value="value.enabled" @input="setEnabled" />
          </div>
        </label>
      </div>

      <div class="child buttons" v-if="isRunning || isSnoozed">
        <label :for="snoozeInputId" class="label col-s-12 col-m-6" v-if="isRunning">
          <div class="value">
            <button class="btn btn-default" @click="snooze">Snooze</button>
          </div>
        </label>

        <label :for="dismissInputId" class="label col-s-12"
               :class="{'col-m-6': isRunning, 'col-m-12': isSnoozed}">
          <div class="value">
            <button class="btn btn-default" @click="dismiss">Dismiss</button>
          </div>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import ToggleSwitch from "@/components/elements/ToggleSwitch";

export default {
  components: {EntityIcon, ToggleSwitch},
  mixins: [EntityMixin],
  emits: ['loading'],
  data: function() {
    return {
      collapsed: true,
    }
  },

  computed: {
    isCollapsed() {
      return this.collapsed
    },

    isRunning() {
      return this.value.state === 'RUNNING'
    },

    isSnoozed() {
      return this.value.state === 'SNOOZED'
    },

    nextRun() {
      if (!(this.value.next_run && this.value.enabled))
        return null

      return new Date(this.value.next_run * 1000)
    },

    enableInputId() {
      return `alarm-input-${this.value.name}`
    },

    snoozeInputId() {
      return `alarm-snooze-${this.value.name}`
    },

    dismissInputId() {
      return `alarm-dismiss-${this.value.name}`
    },
  },

  methods: {
    async setEnabled() {
      this.$emit('loading', true)
      try {
        await this.request(
          'alarm.set_enabled',
          {
            name: this.value.name,
            enabled: !this.value.enabled,
          }
        )
      } finally {
        this.$emit('loading', false)
      }
    },

    async snooze() {
      this.$emit('loading', true)
      try {
        await this.request('alarm.snooze')
      } finally {
        this.$emit('loading', false)
      }
    },

    async dismiss() {
      this.$emit('loading', true)
      try {
        await this.request('alarm.dismiss')
      } finally {
        this.$emit('loading', false)
      }
    },

    prevent(e) {
      e.stopPropagation()
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

$icon-width: 2em;

.alarm-container {
  .head {
    .icon, .collapse-toggler {
      width: $icon-width;
    }

    .label, .value-and-toggler {
      min-width: calc(((100% - (2 * $icon-width)) / 2) - 1em);
      max-width: calc(((100% - (2 * $icon-width)) / 2) - 1em);
    }

    .label {
      margin-left: 1em;
    }

    .value-and-toggler {
      text-align: right;
    }

    .value {
      .date {
        font-weight: normal;
      }
    }
  }

  .body {
    .child {
      .label {
        font-weight: bold;
      }
    }

    .value {
      text-align: right;

      input {
        width: 1em;
        height: 1em;
      }
    }

    .buttons {
      .value {
        text-align: center;
      }

      button {
        border: 1px solid $border-color-2;
        border-radius: 0.25em;
        padding: 0 1em;
        margin: 0.5em;
        height: 3em;
      }
    }
  }
}
</style>
