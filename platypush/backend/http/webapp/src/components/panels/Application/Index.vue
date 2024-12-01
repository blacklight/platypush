<template>
  <div class="app-container">
    <div class="tabs">
      <Tabs>
        <Tab :selected="selectedView === 'actions'"
             icon-class="fas fa-cogs"
             @input="selectedView = 'actions'">
          Actions
        </Tab>

        <Tab :selected="selectedView === 'events'"
             icon-class="fas fa-bolt"
             @input="selectedView = 'events'">
          Events
        </Tab>
      </Tabs>
    </div>

    <div class="content">
      <Actions v-if="selectedView === 'actions'" />
      <Events v-else-if="selectedView === 'events'" />
    </div>
  </div>
</template>

<script>
import Actions from "./Actions"
import Events from "./Events"
import Tabs from "@/components/elements/Tabs"
import Tab from "@/components/elements/Tab"
import Utils from '@/Utils'

export default {
  mixins: [Utils],
  components: {
    Actions,
    Events,
    Tab,
    Tabs,
  },

  data() {
    return {
      selectedView: 'actions',
    }
  },

  methods: {
    setView(view) {
      if (!view?.length) {
        const urlArgs = this.getUrlArgs()
        if (urlArgs.view?.length) {
          view = urlArgs.view
        }
      }

      if (!view?.length) {
        return
      }

      this.selectedView = view
    },
  },

  watch: {
    $route() {
      this.setView()
    },

    selectedView() {
      this.setUrlArgs({ view: this.selectedView })
    },
  },

  created() {
    this.setView()
  },
}
</script>

<style lang="scss" scoped>
$tabs-height: 3.5em;

.app-container {
  width: 100%;
  height: 100%;

  :deep(.tabs) {
    width: 100%;
    height: $tabs-height;
    display: flex;
    align-items: center;
    margin-top: -0.1em;
    box-shadow: $border-shadow-bottom;

    .tab {
      height: $tabs-height;
    }
  }

  .content {
    height: calc(100vh - #{$tabs-height});
    background-color: $background-color;
  }
}
</style>
