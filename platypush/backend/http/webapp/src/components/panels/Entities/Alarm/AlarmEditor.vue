<template>
  <div class="alarm-editor-container" :class="{'with-changes': hasChanges}">
    <Loading v-if="loading" />

    <form class="alarm-editor" @submit.prevent="save">
      <div class="head">
        <div class="row item">
          <div class="col-8">
            <input type="text" ref="nameInput" placeholder="Alarm name" v-model="editForm.name" />
          </div>

          <div class="col-4 buttons" v-if="hasChanges">
            <button type="button" class="reset-btn" title="Reset" @click="editForm = {...value}">
              <i class="fas fa-undo" />
            </button>

            <button type="submit" class="save-btn" title="Save">
              <i class="fas fa-save" />
            </button>
          </div>
        </div>
      </div>

      <div class="body">
        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-question" />
              Condition
            </label>
            <br />

            <span class="subtext">
              <span class="text">
                The condition that must be met for the alarm to trigger.
                <a href="https://crontab.guru" target="_blank">Cron syntax</a> is supported.
              </span>
            </span>

            <div class="condition-type radio">
              <label :class="{selected: editForm.condition_type === 'cron'}">
                <input type="radio" value="cron" v-model="editForm.condition_type" />&nbsp;
                Periodic
              </label>&nbsp;&nbsp;

              <label :class="{selected: editForm.condition_type === 'timestamp'}">
                <input type="radio" value="timestamp" v-model="editForm.condition_type" />&nbsp;
                Date/Time
              </label>&nbsp;&nbsp;

              <label :class="{selected: editForm.condition_type === 'interval'}">
                <input type="radio" value="interval" v-model="editForm.condition_type" />&nbsp;
                Timer
              </label>
            </div>
          </div>

          <div class="value">
            <CronEditor :value="value.condition_type === 'cron' ? editForm.when : null"
                        @input="onWhenInput($event, 'cron')"
                        v-if="editForm.condition_type === 'cron'" />

            <input type="datetime-local"
                   :value="value.condition_type === 'timestamp' ? editForm.when : null"
                   @input="onWhenInput($event.target.value, 'timestamp')"
                   v-else-if="editForm.condition_type === 'timestamp'">

            <TimeInterval :value="value.condition_type === 'interval' ? editForm.when : null"
                   @input="onWhenInput($event, 'interval')"
                   v-else-if="editForm.condition_type === 'interval'" />
          </div>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-music" />
              Media
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                Path or URL of the media resource to play when the alarm triggers.
              </span>
            </span>
          </div>

          <div class="value">
            <FileSelector :value="editForm.media" @input="editForm.media = $event" />
          </div>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-puzzle-piece" />
              Media Plugin
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                The plugin to use to play the media resource.
              </span>
            </span>
          </div>

          <div class="value">
            <input type="text" v-model="editForm.media_plugin" />
          </div>
        </div>

        <div class="row item">
          <label>
            <div class="name">
              <label>
                <i class="icon fas fa-repeat" />
                Repeat Media
              </label>
              <br />
              <span class="subtext">
                <span class="text">
                  Whether to repeat the media resource when it finishes playing
                  if the alarm is still running.
                </span>
              </span>
            </div>

            <div class="value">
              <ToggleSwitch :value="editForm.media_repeat"
                            @input="editForm.media_repeat = $event.target.checked" />
            </div>
          </label>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-volume-high" />
              Volume
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                The volume to play the media resource at.
              </span>
            </span>
          </div>

          <div class="value">
            <Slider :value="audioVolume" :range="[0, 100]"
                    @change="onVolumeChange" />
          </div>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-bell" />
              Snooze interval
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                How long the alarm should be paused after being triggered and
                manually snoozed.
              </span>
            </span>
          </div>

          <div class="value">
            <TimeInterval :value="editForm.snooze_interval"
                          @input="editForm.snooze_interval = $event" />
          </div>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-xmark" />
              Dismiss timeout
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                How long the alarm should run before being automatically dismissed.
              </span>
            </span>
          </div>

          <div class="value">
            <TimeInterval :value="editForm.dismiss_interval"
                          @input="editForm.dismiss_interval = $event" />
          </div>
        </div>

        <div class="row item">
          <div class="name">
            <label>
              <i class="icon fas fa-play" />
              Actions
            </label>
            <br />
            <span class="subtext">
              <span class="text">
                Actions to perform when the alarm triggers.
              </span>
            </span>
          </div>

          <div class="value">
            <ProcedureEditor :value="procedure"
                             :with-name="false"
                             @input="onActionsInput($event)" />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import ProcedureEditor from "@/components/Procedure/ProcedureEditor"
import Slider from "@/components/elements/Slider"
import CronEditor from "@/components/elements/CronEditor"
import FileSelector from "@/components/elements/FileSelector"
import TimeInterval from "@/components/elements/TimeInterval"
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import Utils from "@/Utils"

export default {
  emits: ['input'],
  mixins: [Utils],
  components: {
    CronEditor,
    FileSelector,
    Loading,
    ProcedureEditor,
    Slider,
    TimeInterval,
    ToggleSwitch,
  },

  props: {
    value: {
      type: Object,
      required: true,
    },

    newAlarm: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      editForm: {...this.value},
    }
  },

  computed: {
    procedure() {
      return {
        actions: [...(this.editForm.actions || [])],
      }
    },

    audioVolume() {
      return this.editForm.audio_volume ?? this.defaultVolume
    },

    defaultVolume() {
      return this.$root.config?.alarm?.audio_volume ?? 100
    },

    hasChanges() {
      return Object.keys(this.changes).length > 0
    },

    changes() {
      const changes = {}

      if ((this.value.audio_volume ?? this.defaultVolume) !== this.audioVolume)
        changes.audio_volume = this.audioVolume
      if (JSON.stringify(this.editForm.actions) !== JSON.stringify(this.value.actions))
        changes.actions = this.editForm.actions;

      [
        'dismiss_interval',
        'media',
        'media_plugin',
        'media_repeat',
        'name',
        'snooze_interval',
        'when',
      ].forEach(key => {
        if (this.editForm[key] !== this.value[key])
          changes[key] = this.editForm[key]
      })

      return changes
    },
  },

  methods: {
    actionsToArgs(actions) {
      return actions?.map(action => {
        if (action.name) {
          action.action = action.name
          delete action.name
        }

        return action
      }) ?? []
    },

    onWhenInput(value, type) {
      if (value == null)
        return

      switch (type) {
        case 'timestamp':
          value = new Date(value).toISOString()
          break

        case 'cron':
        case 'interval':
          break

        default:
          console.error('Unknown cron type', type)
          return
      }

      this.editForm.when = value
      this.editForm.condition_type = type
    },

    onActionsInput(procedure) {
      this.editForm.actions = procedure.actions
    },

    onVolumeChange(event) {
      this.editForm.audio_volume = parseFloat(event.target.value)
    },

    async save() {
      this.loading = true
      let args = {}
      let action = null

      if (this.newAlarm) {
        action = 'alarm.add'
        args = {
          name: this.editForm.name,
          when: this.editForm.when,
          media: this.editForm.media,
          media_plugin: this.editForm.media_plugin,
          audio_volume: this.editForm.audio_volume,
          snooze_interval: this.editForm.snooze_interval,
          dismiss_interval: this.editForm.dismiss_interval,
          actions: this.actionsToArgs(this.editForm.actions),
        }
      } else {
        action = 'alarm.edit'
        args = {
          name: this.value.name,
          ...this.changes,
        }

        if (this.changes.actions)
          args.actions = this.actionsToArgs(this.changes.actions)

        if (this.changes.name != null) {
          args.name = this.value.name
          args.new_name = this.changes.name
        }
      }

      try {
        const alarm = await this.request(action, args)
        this.$emit('input', alarm)
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.$nextTick(() => {
      this.$refs.nameInput.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
$header-height: 3.5em;

.alarm-editor-container {
  width: 100%;
  height: 50em;
  max-height: 65vh;
  background: $default-bg-2;
  cursor: default;

  .head {
    width: 100%;
    height: $header-height;

    .row {
      width: 100%;
      height: 100%;
      box-shadow: $border-shadow-bottom;
      display: flex;
      align-items: center;
    }

    input[type=text] {
      width: 100%;
      max-width: 30em;
    }

    .buttons {
      height: 100%;
      display: flex;
      justify-content: right;
      align-items: center;
      padding: 0;

      button {
        margin: 0.25em 0 0.25em 0.5em;

        &.save-btn:hover {
          background: $background-color;
        }
      }
    }
  }

  .body {
    height: calc(100% - #{$header-height});
    overflow: auto;
  }

  .alarm-editor {
    width: 100%;
    height: 100%;
    padding: 0;

    .item {
      padding: 0.5em 1em;
      border-bottom: $default-border-2;

      .name {
        label {
          margin: 0;
          font-weight: bold;

          .icon {
            opacity: 0.75;
            margin-right: 0.5em;
          }
        }

        .condition-type {
          margin: 0.25em 0;

          label {
            &.selected {
              font-weight: bold;
            }

            &:not(.selected) {
              font-weight: normal;
            }
          }
        }
      }

      .value {
        input {
          width: 100%;
        }
      }
    }
  }

  .subtext {
    display: block;
    font-size: 0.9em;
    opacity: 0.8;
    margin-bottom: 0.5em;
  }

  input[type=text] {
    min-height: 2em;
  }
}
</style>
