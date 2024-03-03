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
      <div class="child enable">
        <label :for="enableInputId" class="label">
          <div class="name col-6">Enabled</div>
          <div class="value col-6">
            <ToggleSwitch :id="enableInputId" :value="value.enabled" @input="setEnabled" />
          </div>
        </label>
      </div>

      <div class="child buttons" v-if="isRunning || isSnoozed">
        <label class="label col-6" v-if="isRunning">
          <div class="value">
            <button class="btn btn-default" @click="snooze">
              <i class="fas fa-pause" /> &nbsp;
              Snooze
            </button>
          </div>
        </label>

        <label class="label"
               :class="{'col-6': isRunning, 'col-12': !isRunning}">
          <div class="value">
            <button class="btn btn-default" @click="dismiss">
              <i class="fas fa-times" /> &nbsp;
              Dismiss
            </button>
          </div>
        </label>
      </div>

      <div class="child remove" @click="$refs.removeDialog.show" v-if="hasEdit">
        <label class="label">
          <div class="value">
            <i class="fas fa-trash" /> &nbsp; Remove
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

    <Modal title="Alarm Running" ref="runningModal" :visible="isRunning">
      <div class="alarm-running-modal">
        <div class="icon blink">
          <i class="fas fa-stopwatch" />
        </div>

        <div class="title">
          <h3><b>{{ value.name }}</b> is running</h3>
        </div>

        <div class="buttons">
          <label class="label">
            <button class="btn btn-default" @click="snooze">
              <i class="fas fa-pause" /> &nbsp;
              Snooze
            </button>
          </label>

          <label class="label">
            <button class="btn btn-default" @click="dismiss">
              <i class="fas fa-times" /> &nbsp;
              Dismiss
            </button>
          </label>
        </div>
      </div>
    </Modal>

    <ConfirmDialog ref="removeDialog" @input="remove">
      Are you sure you want to remove alarm <b>{{ value.name }}</b>?
    </ConfirmDialog>
  </div>
</template>

<script>
import AlarmEditor from "./Alarm/AlarmEditor"
import ConfirmDialog from "@/components/elements/ConfirmDialog"
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import Modal from "@/components/Modal";
import ToggleSwitch from "@/components/elements/ToggleSwitch";

export default {
  mixins: [EntityMixin],
  emits: ['loading'],
  components: {
    AlarmEditor,
    ConfirmDialog,
    EntityIcon,
    Modal,
    ToggleSwitch,
  },

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

    async remove() {
      this.$emit('loading', true)
      try {
        await this.request(
          'alarm.delete',
          {
            name: this.value.name,
          }
        )
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

  .remove {
    color: $error-fg;
    cursor: pointer;

    label {
      cursor: pointer;
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

  :deep(.modal-container) {
    cursor: default;

    .content {
      width: 50em;
      max-width: 90%;

      .body {
        width: 100%;
      }
    }

    .alarm-running-modal {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1em;

      .icon {
        font-size: 3.5em;
        color: $selected-fg;
      }

      .title {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 1em;
      }

      .buttons {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;

        label {
          width: 50%;
          text-align: center;
          cursor: pointer;
        }

        button {
          margin: 0.5em;
        }
      }
    }
  }
}

.blink {
  animation: blink-animation 2s infinite;
}

@keyframes blink-animation {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.1;
  }

  100% {
    opacity: 1;
  }
}
</style>
