<template>
  <div class="extension">
    <header>
      <Tabs>
        <Tab :selected="selectedTab === 'doc'" icon-class="fas fa-book"
             @input="selectedTab = 'doc'">
          <span class="from tablet">Documentation</span>
        </Tab>

        <Tab :selected="selectedTab === 'install'" icon-class="fas fa-download"
             @input="selectedTab = 'install'">
          <span class="from tablet">Install</span>
        </Tab>

        <Tab :selected="selectedTab === 'config'" icon-class="fas fa-square-check"
             @input="selectedTab = 'config'">
          <span class="from tablet">Configuration</span>
        </Tab>
      </Tabs>
    </header>

    <div class="extension-body">
      <Doc v-if="selectedTab === 'doc'" :extension="extension" />
      <Config v-else-if="selectedTab === 'config'"
              :extension="extension"
              :config="config"
              :config-file="configFile" />
      <Install v-else-if="selectedTab === 'install'" :extension="extension" />
    </div>
  </div>
</template>

<script>
import Tab from "@/components/elements/Tab"
import Tabs from "@/components/elements/Tabs"
import Config from "./Config"
import Doc from "./Doc"
import Install from "./Install"

export default {
  name: "Extension",
  components: {
    Config,
    Doc,
    Install,
    Tab,
    Tabs,
  },

  props: {
    extension: {
      type: Object,
      required: true,
    },

    config: {
      type: Object,
    },

    configFile: {
      type: String,
    },
  },

  data() {
    return {
      selectedTab: 'doc',
    }
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$header-height: 3.6em;

.extension {
  width: 100%;
  height: 100%;
  background: $background-color;
  display: flex;
  flex-direction: column;
  border-top: 1px solid $border-color-1;
  box-shadow: $border-shadow-bottom;

  header {
    height: $header-height;

    :deep(.tabs) {
      margin: 0;
    }
  }

  .extension-body {
    height: calc(100% - #{$header-height});
    display: flex;
    flex-direction: column;
    overflow: auto;

    :deep(section) {
      height: calc(100% - #{$header-height});
    }
  }
}
</style>
