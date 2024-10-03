<template>
  <div class="procedures-container">
    <header>
      <input type="search"
             class="filter"
             title="Filter procedures"
             placeholder="🔎"
             v-model="filter" />
    </header>

    <main>
      <Loading v-if="loading" />

      <NoItems v-else-if="!Object.keys(procedures || {}).length">
        No Procedures Configured
      </NoItems>

      <div class="procedures-list" v-else>
        <div class="procedures items">
          <div class="item" v-for="procedure in displayedProcedures" :key="procedure.name">
            <Procedure :value="procedure"
                       :selected="selectedProcedure === procedure.name"
                       :collapseOnHeaderClick="true"
                       @click="toggleProcedure(procedure)"
                       @input="updateProcedure(procedure)"
                       @delete="() => delete procedures[procedure.name]" />
          </div>
        </div>
      </div>

      <ProcedureEditor :value="newProcedure"
                       title="Add Procedure"
                       :with-name="true"
                       :with-save="true"
                       :read-only="false"
                       :visible="showNewProcedureEditor"
                       @input="updateProcedure(newProcedure)"
                       @close="resetNewProcedure"
                       v-if="showNewProcedureEditor" />

      <FloatingButton icon-class="fa fa-plus"
                      text="Add Procedure"
                      @click="showNewProcedureEditor = true" />
    </main>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import FloatingButton from "@/components/elements/FloatingButton";
import NoItems from "@/components/elements/NoItems";
import Procedure from "@/components/panels/Entities/Procedure"
import ProcedureEditor from "@/components/Procedure/ProcedureEditorModal"
import Utils from "@/Utils";

export default {
  components: {
    FloatingButton,
    Loading,
    NoItems,
    Procedure,
    ProcedureEditor,
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
      newProcedure: null,
      newProcedureTemplate: {
        name: '',
        actions: [],
        meta: {
          icon: {
            class: 'fas fa-cogs',
            url: null,
            color: null,
          },
        },
      },
      procedures: {},
      selectedProcedure: null,
      showConfirmClose: false,
      showNewProcedureEditor: false,
    }
  },

  computed: {
    displayedProcedures() {
      return Object.values(this.procedures)
        .filter(procedure => procedure.name.toLowerCase().includes(this.filter.toLowerCase()))
    },
  },

  methods: {
    mergeArgs(oldObj, newObj) {
      return {
        ...Object.fromEntries(
          Object.entries(oldObj || {}).map(([key, value]) => {
            const newValue = newObj?.[key]
            if (newValue != null) {
              if (typeof value === 'object' && !Array.isArray(value))
                return [key, this.mergeArgs(value, newValue)]

              return [key, newValue]
            }

            return [key, value]
          })
        ),

        ...Object.fromEntries(
          Object.entries(newObj || {}).filter(([key]) => oldObj?.[key] == null)
        ),
      }
    },

    updateProcedure(procedure) {
      if (!procedure?.name?.length)
        return

      const curProcedure = this.procedures[procedure.name]
      this.procedures[procedure.name] = {
        ...this.mergeArgs(curProcedure, procedure),
        name: procedure?.meta?.name_override || procedure.name,
      }

      this.showNewProcedureEditor = false
    },

    async refresh() {
      const args = this.getUrlArgs()
      if (args.filter)
        this.filter = args.filter

      this.loading = true
      try {
        this.procedures = await this.request('procedures.status')
      } finally {
        this.loading = false
      }
    },

    onEntityUpdate(msg) {
      const entity = msg?.entity
      if (entity?.plugin !== this.pluginName || !entity?.name?.length)
        return

      this.updateProcedure(entity)
    },

    onEntityDelete(msg) {
      const entity = msg?.entity
      if (entity?.plugin !== this.pluginName)
        return

      if (this.selectedProcedure === entity.name)
        this.selectedProcedure = null

      if (this.procedures[entity.name])
        delete this.procedures[entity.name]
    },

    resetNewProcedure() {
      this.showNewProcedureEditor = false
      this.newProcedure = JSON.parse(JSON.stringify(this.newProcedureTemplate))
    },

    toggleProcedure(procedure) {
      this.selectedProcedure =
        this.selectedProcedure === procedure.name ?
        null : procedure.name
    },
  },

  watch: {
    filter() {
      if (!this.filter?.length)
        this.setUrlArgs({ filter: null })
      else
        this.setUrlArgs({ filter: this.filter })
    },

    showNewProcedureEditor(val) {
      if (!val)
        this.resetNewProcedure()
    },
  },

  async mounted() {
    this.resetNewProcedure()
    await this.refresh()

    this.subscribe(
      this.onEntityUpdate,
      'on-procedure-entity-update',
      'platypush.message.event.entities.EntityUpdateEvent'
    )

    this.subscribe(
      this.onEntityDelete,
      'on-procedure-entity-delete',
      'platypush.message.event.entities.EntityDeleteEvent'
    )
  },

  unmounted() {
    this.unsubscribe('on-procedure-entity-update')
    this.unsubscribe('on-procedure-entity-delete')
    this.setUrlArgs({ filter: null })
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$header-height: 3em;

.procedures-container {
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

  .procedures-list {
    width: 100%;
    height: 100%;
    display: flex;
    background: $default-bg-6;
    flex-grow: 1;
    justify-content: center;
  }

  .procedures {
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
