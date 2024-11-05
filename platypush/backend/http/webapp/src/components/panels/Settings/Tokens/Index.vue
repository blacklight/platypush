<template>
  <div class="tokens-container">
    <Loading v-if="loading" />

    <div class="main" v-else>
      <div class="header">
        <div class="tabs-container">
          <Tabs>
            <Tab :selected="tokenType === 'api'"
                 @input="tokenType = 'api'">
              API Tokens
            </Tab>

            <Tab :selected="tokenType === 'jwt'"
                 @input="tokenType = 'jwt'">
              JWT Tokens
            </Tab>
          </Tabs>
        </div>
      </div>

      <div class="body">
        <JwtToken v-if="tokenType === 'jwt'"
                  :current-user="currentUser" />

        <ApiToken v-else
                  :current-user="currentUser" />
      </div>
    </div>
  </div>
</template>

<script>
import ApiToken from "./ApiToken"
import JwtToken from "./JwtToken"
import Loading from "@/components/Loading"
import Tab from "@/components/elements/Tab"
import Tabs from "@/components/elements/Tabs"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  components: {
    ApiToken,
    JwtToken,
    Loading,
    Tab,
    Tabs,
  },

  props: {
    currentUser: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      token: null,
      tokenType: null,
    }
  },

  methods: {
    refresh() {
      const args = this.getUrlArgs()
      this.$nextTick(() => {
        this.tokenType = args.type?.length ? args.type : 'api'
      })
    },
  },

  watch: {
    tokenType(value) {
      this.setUrlArgs({type: value})
    },

    $route() {
      this.refresh()
    },
  },

  mounted() {
    this.refresh()
  },

  unmounted() {
    this.setUrlArgs({type: null})
  },
}
</script>

<style lang="scss" scoped>
$header-height: 4em;

.tokens-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .header {
    width: 100%;
    height: $header-height;
    align-items: center;
  }

  .main {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .header {
    height: $header-height;
    margin-top: -0.2em;
  }

  .body {
    height: calc(100% - #{$header-height} - 0.2em);
    overflow: auto;
  }
}
</style>
