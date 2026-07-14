<template>
  <div class="variables-container">
    <header>
      <input type="search"
             class="filter"
             title="Filter variables by name (case insensitive) or value (case sensitive)"
             placeholder="🔎 Filter by name or value"
             v-model="filter" />
    </header>

    <main>
      <Loading v-if="loading" />

      <NoItems v-else-if="!Object.keys(variables || {}).length">
        No Variables Configured
      </NoItems>

      <div class="variables-list" v-else>
        <div class="variables items">
          <div class="item" v-for="variable in displayedVariables" :key="variable.id">
            <Variable :value="variable"
                      @loading="loadingVariables[variable.id] = $event" />
          </div>
        </div>
      </div>

      <VariableModal :visible="showNewVariableModal"
                     @close="showNewVariableModal = false" />

      <FloatingButton icon-class="fa fa-plus"
                      text="Add Variable"
                      @click="showNewVariableModal = true" />
    </main>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import FloatingButton from "@/components/elements/FloatingButton";
import NoItems from "@/components/elements/NoItems";
import Variable from "@/components/panels/Entities/Variable"
import VariableModal from "@/components/panels/Entities/VariableModal"
import Utils from "@/Utils";

export default {
  components: {
    FloatingButton,
    Loading,
    NoItems,
    Variable,
    VariableModal,
  },

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
      filter: '',
      loading: false,
      loadingVariables: {},
      variables: {},
      showNewVariableModal: false,
    }
  },

  computed: {
    displayedVariables() {
      if (!this.filter?.length)
        return Object.values(this.variables)

      const filter = this.filter
      return Object.values(this.variables).filter(variable => {
        const nameMatch = variable.name.toLowerCase().includes(filter.toLowerCase())
        const valueMatch = (variable.value || '').includes(filter)
        return nameMatch || valueMatch
      })
    },
  },

  methods: {
    addOrUpdateVariable(entity) {
      if (!entity?.id || entity.type !== 'variable')
        return

      entity.name = entity?.meta?.name_override || entity.name
      this.variables[entity.id] = entity
    },

    async refresh() {
      const args = this.getUrlArgs()
      if (args.filter)
        this.filter = args.filter

      this.loading = true
      try {
        const entities = await this.request('entities.get')

        this.variables = {}
        entities
          .filter(entity => entity.type === 'variable')
          .forEach(entity => this.addOrUpdateVariable(entity))
      } finally {
        this.loading = false
      }
    },

    onEntityUpdate(msg) {
      const entity = msg?.entity
      if (entity?.type !== 'variable')
        return

      this.addOrUpdateVariable(entity)
    },

    onEntityDelete(msg) {
      const entity = msg?.entity
      if (entity?.type !== 'variable')
        return

      if (this.variables[entity.id])
        delete this.variables[entity.id]
    },
  },

  watch: {
    filter() {
      if (!this.filter?.length)
        this.setUrlArgs({ filter: null })
      else
        this.setUrlArgs({ filter: this.filter })
    },
  },

  async mounted() {
    await this.refresh()

    this.subscribe(
      this.onEntityUpdate,
      'on-variable-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.subscribe(
      this.onEntityDelete,
      'on-variable-entity-delete',
      'platypush.message.event.entities.EntityDeleteEvent'
    )
  },

  unmounted() {
    this.unsubscribe('on-variable-entity-update')
    this.unsubscribe('on-variable-entity-delete')
    this.setUrlArgs({ filter: null })
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$header-height: 3em;

.variables-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  flex-grow: 1;

  header {
    width: 100%;
    height: $header-height;
    background: $tab-bg;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid $default-shadow-color;

    input.filter {
      max-width: 600px;

      @include until($tablet) {
        width: calc(100% - 2em);
      }

      @include from($tablet) {
        width: 600px;
      }
    }
  }

  main {
    width: 100%;
    height: calc(100% - #{$header-height});
    overflow: auto;
    margin-bottom: 2em;
  }

  .variables-list {
    width: 100%;
    height: 100%;
    display: flex;
    background: $default-bg-6;
    flex-grow: 1;
    justify-content: center;
  }

  .variables {
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

    .item {
      padding: 0;

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
</style>
