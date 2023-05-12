<template>
  <div class="row plugin entities-container">
    <Loading v-if="loading" />

    <header>
      <Selector
        :entity-groups="entityGroups"
        :value="selector"
        @input="selector = $event"
        @refresh="refresh"
        @show-variable-modal="variableModalVisible = true"
      />
    </header>

    <div class="groups-canvas">
      <EntityModal
        :entity="entities[modalEntityId]"
        :parent="entities[entities[modalEntityId].parent_id]"
        :children="childrenByParentId(modalEntityId)"
        :visible="modalVisible"
        :config-values="configValuesByParentId(modalEntityId)"
        @close="onEntityModal"
        @entity-update="modalEntityId = $event"
        v-if="modalEntityId && entities[modalEntityId]"
      />

      <VariableModal :visible="variableModalVisible" @close="variableModalVisible = false" />
      <NoItems v-if="!Object.keys(displayGroups || {})?.length">No entities found</NoItems>

      <div class="groups-container" v-else>
        <div class="group fade-in" v-for="group in displayGroups" :key="group.name">
          <div class="frame">
            <div class="header">
              <span class="section left">
                <Icon v-bind="entitiesMeta[typesByCategory[group.name]].icon || {}"
                  v-if="selector.grouping === 'category' && entitiesMeta[typesByCategory[group.name]]" />
                <Icon :class="pluginIcons[group.name]?.class" :url="pluginIcons[group.name]?.imgUrl"
                  v-else-if="selector.grouping === 'plugin' && pluginIcons[group.name]" />
              </span>

              <span class="section center">
                <div class="title" v-text="group.name" />
              </span>

              <span class="section right">
                <button title="Refresh" @click="refresh(group)">
                  <i class="fa fa-sync-alt" />
                </button>
              </span>
            </div>

            <div class="body">
              <div class="entity-frame"
                 v-for="entity in Object.values(group.entities).sort((a, b) => a.name.localeCompare(b.name))"
                 :key="entity.id">
                <Entity
                  :value="entity"
                  :children="childrenByParentId(entity.id)"
                  :all-entities="entities"
                  @show-modal="onEntityModal($event)"
                  @input="onEntityInput(entity)"
                  :error="!!errorEntities[entity.id]"
                  :key="entity.id"
                  :loading="!!loadingEntities[entity.id]"
                  @loading="loadingEntities[entity.id] = $event"
                  v-if="!entity.parent_id"
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
import VariableModal from "./VariableModal"
import { bus } from "@/bus";
import icons from '@/assets/icons.json'
import meta from './meta.json'

export default {
  name: "Entities",
  mixins: [Utils],
  components: {
    Entity,
    EntityModal,
    Icon,
    Loading,
    NoItems,
    Selector,
    VariableModal,
  },

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
      entityGroups: {
        id: {},
        category: {},
        plugin: {},
        type: {},
      },
      modalEntityId: null,
      modalVisible: false,
      variableModalVisible: false,
      selector: {
        grouping: 'plugin',
        selectedEntities: {},
        selectedGroups: {},
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

    typesByCategory() {
      return Object.entries(meta).reduce((obj, [type, meta]) => {
          obj[meta.name_plural] = type
          return obj
      }, {})
    },

    displayGroups() {
      return Object.entries(this.entityGroups[this.selector.grouping])
        .filter((entry) => this.selector.selectedGroups[entry[0]])
        .map(
          ([grouping, entities]) => {
            return {
              name: grouping,
              entities: Object.values(entities).filter(
                (e) => e.id in this.selector.selectedEntities
              ),
            }
          }
        )
        .filter((group) => group.entities?.length > 0)
        .sort((a, b) => a.name.localeCompare(b.name))
    },
  },

  methods: {
    addEntity(entity) {
      if (entity.parent_id != null)
        return  // Only group entities that have no parent

      this.entities[entity.id] = entity;
      ['id', 'type', 'category', 'plugin'].forEach((attr) => {
        if (entity[attr] == null)
          return

        if (attr == 'id')
          this.entityGroups[attr][entity[attr]] = entity
        else {
          if (!this.entityGroups[attr][entity[attr]])
            this.entityGroups[attr][entity[attr]] = {}
          this.entityGroups[attr][entity[attr]][entity.id] = entity
        }
      })
    },

    removeEntity(entity) {
      if (entity.parent_id != null)
        return  // Only group entities that have no parent

      ['id', 'type', 'category', 'plugin'].forEach((attr) => {
        if (this.entityGroups[attr][entity[attr]][entity.id])
          delete this.entityGroups[attr][entity[attr]][entity.id]
      })

      if (this.entities[entity.id])
        delete this.entities[entity.id]
    },

    _shouldSkipLoading(entity) {
      const children = Object.values(this.childrenByParentId(entity.id))
      const hasReadableChildren = children.filter((child) => {
        return (
          !child.is_configuration &&
          !child.is_write_only &&
          !child.is_query_disabled
        )
      }).length > 0

      return (
        entity.is_query_disabled ||
        entity.is_write_only ||
        (children.length && !hasReadableChildren)
      )
    },

    async refresh(group) {
      const entities = (group ? group.entities : this.entities) || {}
      const args = {}
      if (group)
        args.plugins = Object.values(entities).reduce((obj, entity) => {
          obj[entity.plugin] = true
          return obj
        }, {})

      this.loadingEntities = Object.values(entities).reduce((obj, entity) => {
          if (this._shouldSkipLoading(entity))
            return obj

          const self = this
          const id = entity.id
          if (this.entityTimeouts[id])
            clearTimeout(this.entityTimeouts[id])

          this.addEntity(entity)
          this.entityTimeouts[id] = setTimeout(() => {
              if (self.loadingEntities[id])
                delete self.loadingEntities[id]
              if (self.entityTimeouts[id])
                delete self.entityTimeouts[id]

              self.errorEntities[id] = entity
              console.warn(`Scan timeout for ${entity.name}`)
          }, this.entityScanTimeout * 1000)

          obj[id] = true
          return obj
      }, {})

      this.request('entities.scan', args)
    },

    async sync(setLoading=true) {
      if (setLoading)
        this.loading = true

      try {
        this.entities = (await this.request('entities.get')).reduce((obj, entity) => {
          entity.name = entity?.meta?.name_override || entity.name
          entity.category = meta[entity.type].name_plural
          entity.meta = {
            ...(meta[entity.type] || {}),
            ...(entity.meta || {}),
          }

          obj[entity.id] = entity
          this.addEntity(entity)
          return obj
        }, {})

        this.selector.selectedEntities = this.entityGroups.id
        this.refreshEntitiesCache()
      } finally {
        if (setLoading)
          this.loading = false
      }
    },

    childrenByParentId(parentId, selectConfig) {
      const entity = this.entities?.[parentId]
      if (!entity?.children_ids?.length)
        return {}

      return entity.children_ids.reduce((obj, id) => {
        const child = this.entities[id]
        if (
          child && (
            (!selectConfig && !child.is_configuration) ||
            (selectConfig && child.is_configuration)
          )
        )
          obj[id] = this.entities[id]
        return obj
      }, {})
    },

    configValuesByParentId(parentId) {
      return this.childrenByParentId(parentId, true)
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
      entity.category = meta[entity.type].name_plural
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

      entity.category = meta[entity.type].name_plural
      entity.meta = {
        ...(meta[event.entity.type] || {}),
        ...(this.entities[entityId]?.meta || {}),
        ...(event.entity?.meta || {}),
      }

      this.addEntity(entity)
      bus.publishEntity(entity)
    },

    onEntityDelete(event) {
      const entityId = event.entity?.id
      if (entityId == null)
        return
      if (entityId === this.modalEntityId)
        this.modalEntityId = null
      if (this.entities[entityId])
        this.removeEntity(this.entities[entityId])
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

    loadCachedEntities() {
      const cachedEntities = window.localStorage.getItem('entities')
      if (cachedEntities) {
        try {
          this.entities = JSON.parse(cachedEntities)
          if (!this.entities)
            throw Error('The list of cached entities is null')
        } catch (e) {
          console.warning('Could not parse cached entities', e)
          return false
        }

        Object.values(this.entities).forEach((entity) => this.onEntityUpdate({entity: entity}))
        this.selector.selectedEntities = this.entityGroups.id
        return true
      }

      return false
    },

    refreshEntitiesCache() {
      if (this.loading)
        return

      window.localStorage.setItem('entities', JSON.stringify(this.entities))
    },
  },

  async mounted() {
    this.subscribe(
      this.onEntityUpdate,
      'on-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.subscribe(
      this.onEntityDelete,
      'on-entity-delete',
      'platypush.message.event.entities.EntityDeleteEvent'
    )

    if (!this.loadCachedEntities()) {
      await this.sync()
      this.refresh()
    } else {
      await this.request('entities.scan')
      this.sync()
    }

    setInterval(() => this.refreshEntitiesCache(), 10000)
  },

  unmounted() {
    this.unsubscribe('on-entity-update')
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
    background: transparent;
    border: 0;

    &:hover {
      color: $default-hover-fg;
    }
  }

  header {
    width: calc(100% - 2px);
    height: $selector-height;
    display: flex;
    background: $default-bg-2;
    margin-left: 2px;
    box-shadow: $border-shadow-bottom;
    position: relative;
    z-index: 1;

    .right {
      position: absolute;
      right: 0;
      text-align: right;
      margin-right: 0.5em;
      padding-right: 0;

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
    @include until(#{$tablet - 1}) {
      background: $default-bg-2;
    }

    @include until(#{$desktop - 1}) {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    @include from($desktop) {
      column-count: var(--groups-per-row);
    }
  }

  .group {
    width: 100%;
    max-width: 600px;
    max-height: 100%;
    position: relative;
    display: flex;
    break-inside: avoid;

    @include until(#{$tablet - 1}) {
      padding: 0;
    }

    @include from($tablet) {
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

      @include from($tablet) {
        border-radius: 1em;
        box-shadow: $group-shadow;
      }
    }

    .header {
      width: 100%;
      height: $header-height;
      display: table;
      background: $header-bg;
      box-shadow: $header-shadow;

      @include until(#{$tablet - 1}) {
        border-bottom: 1px solid $border-color-2;
      }

      @include from($tablet) {
        border-radius: 1em 1em 0 0;
      }

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

      .title {
        text-transform: capitalize;

        @include until(#{$tablet - 1}) {
          font-weight: bold;
        }
      }
    }

    .body {
      max-height: calc(100% - #{$header-height});
      overflow: auto;
      flex-grow: 1;

      @include until(#{$tablet - 1}) {
        background: $default-bg-4;
      }

      @include from($tablet) {
        background: $default-bg-2;
      }

      .entity-frame {
        background: $background-color;

        @include until(#{$tablet - 1}) {
          margin: 0.75em 0.25em;
          border: $default-border-2;
          border-radius: 1em;
        }

        @include from($tablet) {
          &:last-child {
            border-radius: 0 0 1em 1em;
          }
        }
      }
    }
  }

  :deep(.modal) {
    @include until(#{$tablet - 1}) {
      width: calc(100% - 1em);

      .table-row {
        border-bottom: 1px solid $border-color-2;
      }
    }

    .table-row {
      .value {
        overflow: auto;
      }
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
