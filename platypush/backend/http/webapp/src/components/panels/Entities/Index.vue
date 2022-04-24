<template>
  <div class="row plugin entities-container">
    <Loading v-if="loading" />

    <header>
      <div class="col-11 left">
        <Selector :entity-groups="entityGroups" :value="selector" @input="selector = $event" />
      </div>

      <div class="col-1 right">
        <button title="Refresh" @click="refresh(null)">
          <i class="fa fa-sync-alt" />
        </button>
      </div>
    </header>

    <div class="groups-canvas">
      <EntityModal :entity="entities[modalEntityId]"
        :visible="modalVisible" @close="onEntityModal(null)"
        v-if="modalEntityId"
      />

      <NoItems v-if="!Object.keys(displayGroups || {})?.length">No entities found</NoItems>

      <div class="groups-container" v-else>
        <div class="group fade-in" v-for="group in displayGroups" :key="group.name">
          <div class="frame">
            <div class="header">
              <span class="section left">
                <Icon v-bind="entitiesMeta[group.name].icon || {}"
                  v-if="selector.grouping === 'type' && entitiesMeta[group.name]" />
                <Icon :class="pluginIcons[group.name]?.class" :url="pluginIcons[group.name]?.imgUrl"
                  v-else-if="selector.grouping === 'plugin' && pluginIcons[group.name]" />
              </span>

              <span class="section center">
                <div class="title" v-text="entitiesMeta[group.name].name_plural"
                  v-if="selector.grouping === 'type' && entitiesMeta[group.name]"/>
                <div class="title" v-text="group.name" v-else-if="selector.grouping === 'plugin'"/>
              </span>

              <span class="section right">
                <button title="Refresh" @click="refresh(group)">
                  <i class="fa fa-sync-alt" />
                </button>
              </span>
            </div>

            <div class="body">
              <div class="entity-frame" @click="onEntityModal(entity.id)"
                  v-for="entity in group.entities" :key="entity.id">
                <Entity
                  :value="entity"
                  @input="onEntityInput"
                  :error="!!errorEntities[entity.id]"
                  :loading="!!loadingEntities[entity.id]"
                  @loading="loadingEntities[entity.id] = $event"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils"
import Loading from "@/components/Loading";
import Icon from "@/components/elements/Icon";
import NoItems from "@/components/elements/NoItems";
import Entity from "./Entity.vue";
import Selector from "./Selector.vue";
import EntityModal from "./Modal"
import icons from '@/assets/icons.json'
import meta from './meta.json'

export default {
  name: "Entities",
  components: {Loading, Icon, Entity, Selector, NoItems, EntityModal},
  mixins: [Utils],

  props: {
    // Entity scan timeout in seconds
    entityScanTimeout: {
      type: Number,
      default: 30,
    },
  },

  data() {
    return {
      loading: false,
      loadingEntities: {},
      errorEntities: {},
      entityTimeouts: {},
      entities: {},
      modalEntityId: null,
      modalVisible: false,
      selector: {
        grouping: 'type',
        selectedEntities: {},
      },
    }
  },

  computed: {
    entitiesMeta() {
      return meta
    },

    pluginIcons() {
      return icons
    },

    entityGroups() {
      return {
        'id': Object.entries(this.groupEntities('id')).reduce((obj, [id, entities]) => {
          obj[id] = entities[0]
          return obj
        }, {}),
        'type': this.groupEntities('type'),
        'plugin': this.groupEntities('plugin'),
      }
    },

    displayGroups() {
      return Object.entries(this.entityGroups[this.selector.grouping]).filter(
        (entry) => entry[1].filter(
          (e) => !!this.selector.selectedEntities[e.id]
        ).length > 0
      ).sort((a, b) => a[0].localeCompare(b[0])).map(
        ([grouping, entities]) => {
          return {
            name: grouping,
            entities: entities.filter(
              (e) => e.id in this.selector.selectedEntities
            ),
          }
        }
      )
    },
  },

  methods: {
    groupEntities(attr) {
      return Object.values(this.entities).reduce((obj, entity) => {
        const entities = obj[entity[attr]] || {}
        entities[entity.id] = entity
        obj[entity[attr]] = Object.values(entities).sort((a, b) => {
            return a.name.localeCompare(b.name)
          })

        return obj
      }, {})
    },

    async refresh(group) {
      const entities = (group ? group.entities : this.entities) || {}
      const args = {}
      if (group)
        args.plugins = Object.keys(entities.reduce((obj, entity) => {
          obj[entity.plugin] = true
          return obj
        }, {}))

      this.loadingEntities = Object.values(entities).reduce((obj, entity) => {
          const self = this
          const id = entity.id
          if (this.entityTimeouts[id])
            clearTimeout(this.entityTimeouts[id])

          this.entityTimeouts[id] = setTimeout(() => {
              if (self.loadingEntities[id])
                delete self.loadingEntities[id]
              if (self.entityTimeouts[id])
                delete self.entityTimeouts[id]

              self.errorEntities[id] = entity
              self.notify({
                error: true,
                title: entity.plugin,
                text: `Scan timeout for ${entity.name}`,
              })
          }, this.entityScanTimeout * 1000)

          obj[id] = true
          return obj
      }, {})

      await this.request('entities.scan', args)
    },

    async sync() {
      this.loading = true

      try {
        this.entities = (await this.request('entities.get')).reduce((obj, entity) => {
          entity.name = entity?.meta?.name_override || entity.name
          entity.meta = {
            ...(meta[entity.type] || {}),
            ...(entity.meta || {}),
          }

          obj[entity.id] = entity
          return obj
        }, {})

        this.selector.selectedEntities = this.entityGroups.id
      } finally {
        this.loading = false
      }
    },

    clearEntityTimeouts(entityId) {
      if (this.errorEntities[entityId])
        delete this.errorEntities[entityId]
      if (this.loadingEntities[entityId])
        delete this.loadingEntities[entityId]
      if (this.entityTimeouts[entityId]) {
        clearTimeout(this.entityTimeouts[entityId])
        delete this.entityTimeouts[entityId]
      }
    },

    onEntityInput(entity) {
      this.entities[entity.id] = entity
      this.clearEntityTimeouts(entity.id)
      if (this.loadingEntities[entity.id])
        delete this.loadingEntities[entity.id]
    },

    onEntityUpdate(event) {
      const entityId = event.entity.id
      if (entityId == null)
        return

      this.clearEntityTimeouts(entityId)
      const entity = {...event.entity}
      if (event.entity?.state == null)
        entity.state = this.entities[entityId]?.state
      if (entity.meta?.name_override?.length)
        entity.name = entity.meta.name_override
      else if (this.entities[entityId]?.meta?.name_override?.length)
        entity.name = this.entities[entityId].meta.name_override
      else
        entity.name = event.entity?.name || this.entities[entityId]?.name

      entity.meta = {
        ...(meta[event.entity.type] || {}),
        ...(this.entities[entityId]?.meta || {}),
        ...(event.entity?.meta || {}),
      }

      this.entities[entityId] = entity
    },

    onEntityModal(entityId) {
      if (entityId) {
        this.modalEntityId = entityId
        this.modalVisible = true
      } else {
        this.modalEntityId = null
        this.modalVisible = false
      }
    },
  },

  mounted() {
    this.subscribe(
      this.onEntityUpdate,
      'on-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.sync()
  },
}
</script>

<style lang="scss" scoped>
@import "vars";
@import "~@/style/items";

.entities-container {
  --groups-per-row: 1;

  @include from($desktop) {
    --groups-per-row: 2;
  }

  @include from($fullhd) {
    --groups-per-row: 3;
  }

  width: 100%;
  height: 100%;
  overflow: auto;
  color: $default-fg-2;
  font-weight: 400;

  button {
    background: #ffffff00;
    border: 0;

    &:hover {
      color: $default-hover-fg;
    }
  }

  header {
    width: 100%;
    height: $selector-height;
    display: flex;
    background: $default-bg-2;
    box-shadow: $border-shadow-bottom;
    position: relative;

    .right {
      position: absolute;
      right: 0;
      text-align: right;
      margin-right: 0.5em;
      padding-right: 0.5em;

      button {
        padding: 0.5em 0;
      }
    }
  }

  .groups-canvas {
    width: 100%;
    height: calc(100% - #{$selector-height});
    overflow: auto;
  }

  .groups-container {
    @include from($desktop) {
      column-count: var(--groups-per-row);
    }
  }

  .group {
    width: 100%;
    max-height: 100%;
    position: relative;
    padding: $main-margin 0;
    display: flex;
    break-inside: avoid;

    @include from ($tablet) {
      padding: $main-margin;
    }

    .frame {
      @include from($desktop) {
        max-height: calc(100vh - #{$header-height} - #{$main-margin});
      }

      display: flex;
      flex-direction: column;
      flex-grow: 1;
      position: relative;
      box-shadow: $group-shadow;
      border-radius: 1em;
    }

    .header {
      width: 100%;
      height: $header-height;
      display: table;
      background: $header-bg;
      box-shadow: $header-shadow;
      border-radius: 1em 1em 0 0;

      .section {
        height: 100%;
        display: table-cell;
        vertical-align: middle;

        &.left, &.right {
          width: 10%;
        }

        &.right {
          text-align: right;
        }

        &.center {
          width: 80%;
          text-align: center;
        }
      }
    }

    .body {
      background: $default-bg-2;
      max-height: calc(100% - #{$header-height});
      overflow: auto;
      flex-grow: 1;

      .entity-frame:last-child {
        border-radius: 0 0 1em 1em;
      }
    }
  }

  :deep(.modal) {
    @include until($tablet) {
      width: 95%;
    }

    .content {
      @include until($tablet) {
        width: 100%;
      }

      @include from($tablet) {
        min-width: 30em;
      }

      .body {
        padding: 0;

        .table-row {
          padding: 0.5em;
        }
      }
    }
  }
}
</style>
