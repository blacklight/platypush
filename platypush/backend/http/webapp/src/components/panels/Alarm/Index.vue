<template>
  <Loading v-if="loading" />

  <NoItems v-else-if="!Object.keys(alarms).length">
    No alarms configured
  </NoItems>

  <div class="alarms-container" v-else>
    <div class="alarms items">
      <div class="item" v-for="alarm in alarms" :key="alarm.external_id">
        <Entity :value="alarm" @show-modal="selectedAlarm = alarm.external_id" />
      </div>
    </div>
  </div>

  <EntityModal
    :entity="alarms[selectedAlarm]"
    :visible="modalVisible"
    :config-values="{}"
    @close="selectedAlarm = null"
    v-if="modalVisible" />

  <FloatingButton icon-class="fa fa-plus" text="Add Alarm"
                  @click="addAlarmModalVisible = true" />
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import EntityModal from "@/components/panels/Entities/Modal";
import Entity from "@/components/panels/Entities/Entity";
import FloatingButton from "@/components/elements/FloatingButton";
import NoItems from "@/components/elements/NoItems";

export default {
  components: {Entity, EntityModal, FloatingButton, Loading, NoItems},
  mixins: [Utils],
  props: {
    pluginName: {
      type: String,
    },

    config: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      loading: false,
      addAlarmModalVisible: false,
      alarms: {},
      selectedAlarm: null,
    }
  },

  computed: {
    modalVisible() {
      return this.alarms[this.selectedAlarm] != null
    },
  },

  methods: {
    addAlarm(alarm) {
      alarm.name = alarm?.meta?.name_override || alarm.name
      alarm.meta = {
        ...alarm.meta,
        icon: {
          'class': (alarm.meta?.icon?.['class'] || 'fas fa-stopwatch'),
        },
      }

      this.alarms[alarm.external_id] = alarm
    },

    async refresh() {
      this.$emit('loading', true)
      try {
        (await this.request('entities.get', {plugins: [this.pluginName]})).forEach(
          entity => this.addAlarm(entity)
        )
      } finally {
        this.$emit('loading', false)
      }
    },

    async onEntityUpdate(msg) {
      const entity = msg?.entity
      if (entity?.plugin !== this.pluginName)
        return

      this.addAlarm(entity)
    },

    async onEntityDelete(msg) {
      const entity = msg?.entity
      if (entity?.plugin !== this.pluginName)
        return

      if (this.selectedAlarm === entity.external_id)
        this.selectedAlarm = null

      if (this.alarms[entity.external_id])
        delete this.alarms[entity.external_id]
    },
  },

  mounted() {
    this.refresh()

    this.subscribe(
      this.onEntityUpdate,
      'on-alarm-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.subscribe(
      this.onEntityDelete,
      'on-alarm-entity-delete',
      'platypush.message.event.entities.EntityDeleteEvent'
    )
  },

  unmounted() {
    this.unsubscribe('on-alarm-entity-update')
    this.unsubscribe('on-alarm-entity-delete')
  },
}
</script>

<style lang="scss" scoped>
.alarms-container {
  display: flex;
  height: 100%;
  background: $default-bg-6;
  flex-grow: 1;
  overflow-y: auto;
  justify-content: center;

  .alarms {
    @include until($tablet) {
      width: 100%;
    }

    @include from($tablet) {
      width: calc(100% - 2em);
      margin-top: 1em;
      border-radius: 1em;
    }

    max-width: 800px;
    background: $default-bg-2;
    display: flex;
    flex-direction: column;
    margin-bottom: auto;
    box-shadow: $border-shadow-bottom-right;

    :deep(.item) {
      .entity-container {
        &:first-child {
          border-top-left-radius: 1em;
          border-top-right-radius: 1em;
        }

        &:last-child {
          border-bottom-left-radius: 1em;
          border-bottom-right-radius: 1em;
        }
      }
    }
  }
}
</style>
