<template>
  <div class="entity alarm-container">
    <div class="head" :class="{collapsed: collapsed}">
      <div class="icon col-1">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label col-5">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-and-toggler col-8" @click.stop="collapsed = !collapsed">
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
          <div class="name col-6">Enabled</div>
          <div class="value col-6">
            <ToggleSwitch :id="enableInputId" :value="value.enabled" @input="setEnabled" />
          </div>
        </label>
      </div>

      <div class="child buttons" v-if="isRunning || isSnoozed">
        <label :for="snoozeInputId" class="label col-6" v-if="isRunning">
          <div class="value">
            <button class="btn btn-default" @click="snooze">Snooze</button>
          </div>
        </label>

        <label :for="dismissInputId" class="label"
               :class="{'col-6': isRunning, 'col-12': !isRunning}">
          <div class="value">
            <button class="btn btn-default" @click="dismiss">Dismiss</button>
          </div>
        </label>
      </div>

      <div class="child edit" v-if="hasEdit">
        <div class="head" :class="{collapsed: editCollapsed}"
             @click.stop="editCollapsed = !editCollapsed">
          <div class="label name col-11">
            <i class="fas fa-pen-to-square" />&nbsp; Edit
          </div>

          <div class="value col-1 collapse-toggler">
            <i class="fas" :class="{'fa-chevron-down': editCollapsed, 'fa-chevron-up': !editCollapsed}" />
          </div>
        </div>

        <AlarmEditor v-if="!editCollapsed" :value="value" />
      </div>
    </div>
  </div>
</template>

<script>
import AlarmEditor from "./Alarm/AlarmEditor"
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import ToggleSwitch from "@/components/elements/ToggleSwitch";

export default {
  components: {AlarmEditor, EntityIcon, ToggleSwitch},
  mixins: [EntityMixin],
  emits: ['loading'],
  data: function() {
    return {
      collapsed: true,
      editCollapsed: true,
    }
  },

  computed: {
    hasEdit() {
      return !this.value.static
    },

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
            name: this.value.external_id,
            enabled: !this.value.enabled,
          }
        )

        await this.refresh()
      } finally {
        this.$emit('loading', false)
      }
    },

    async snooze() {
      this.$emit('loading', true)
      try {
        await this.request('alarm.snooze')
        await this.refresh()
      } finally {
        this.$emit('loading', false)
      }
    },

    async dismiss() {
      this.$emit('loading', true)
      try {
        await this.request('alarm.dismiss')
        await this.refresh()
      } finally {
        this.$emit('loading', false)
      }
    },

    async refresh() {
      this.$emit('loading', true)
      try {
        await this.request('alarm.status')
      } finally {
        this.$emit('loading', false)
      }
    },

    prevent(e) {
      e.stopPropagation()
    },
  },

  mounted() {
    this.$watch(
      () => this.value,
      (newValue, oldValue) => {
        if (newValue?.state !== oldValue?.state) {
          const notif = {image: {icon: 'stopwatch'}}
          switch (newValue?.state) {
            case 'RUNNING':
              notif.text = `Alarm ${newValue.name} is running`
              break
            case 'SNOOZED':
              notif.text = `Alarm ${newValue.name} has been snoozed`
              break
            case 'DISMISSED':
              notif.text = `Alarm ${newValue.name} has been dismissed`
              break
          }

          if (notif.text)
            this.notify(notif)
        }
      }
    )
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
    padding: 0;

    .child {
      min-height: 3em;
      display: flex;
      align-items: center;
      padding: 0 1em;

      &:hover {
        background: $hover-bg;
      }

      .label {
        width: 100%;
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

  .edit {
    &.child {
      flex-direction: column;
      padding: 0;
    }

    .head {
      width: 100%;
      padding: 0 1em;
      cursor: pointer;
      display: flex;
      align-items: center;
      border-top: $default-border-2;
      box-shadow: $border-shadow-bottom;

      .name {
        display: flex;
        align-items: center;
      }
    }
  }
}
</style>
