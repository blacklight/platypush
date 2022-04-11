<template>
  <div class="row plugin entities-container">
    <Loading v-if="loading" />

    <div class="entity-selector-container">
      <Selector :entity-groups="entityGroups" :value="selector" @input="selector = $event" />
    </div>

    <div class="groups-canvas">
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

              <span class="section right" />
            </div>

            <div class="body">
              <div class="entity-frame" v-for="entity in group.entities" :key="entity.id">
                <Entity :value="entity" @input="entities[entity.id] = $event" />
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
import icons from '@/assets/icons.json'
import meta from './meta.json'

export default {
  name: "Entities",
  components: {Loading, Icon, Entity, Selector, NoItems},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      entities: {},
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

    async refresh() {
      this.loading = true

      try {
        this.entities = (await this.request('entities.get')).reduce((obj, entity) => {
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

    onEntityUpdate(event) {
      const entityId = event.entity.id
      if (entityId == null)
        return

      this.entities[entityId] = {
        ...event.entity,
        meta: {
          ...(this.entities[entityId]?.meta || {}),
          ...(event.entity?.meta || {}),
        },
      }
    },
  },

  mounted() {
    this.subscribe(
      this.onEntityUpdate,
      'on-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.refresh()
  },
}
</script>

<style lang="scss">
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
  display: flex;
  flex-direction: column;
  overflow: auto;
  color: $default-fg-2;
  font-weight: 400;

  .entity-selector-container {
    height: $selector-height;
  }

  .groups-canvas {
    width: 100%;
    height: calc(100% - #{$selector-height});
    display: flex;
    flex-direction: column;
  }

  .groups-container {
    overflow: auto;
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
    padding: $main-margin;

    .frame {
      max-height: calc(100% - #{2 * $main-margin});
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
}
</style>
