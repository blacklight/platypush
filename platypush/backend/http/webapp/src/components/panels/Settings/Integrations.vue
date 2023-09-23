<template>
  <div class="integrations-container">
    <Loading v-if="loading" />

    <div class="body">
      <!-- TODO -->
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  name: "Integrations",
  components: {Loading},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      plugins: {},
      backends: {},
    }
  },

  methods: {
    async loadIntegrations() {
      this.loading = true

      try {
          [this.plugins, this.backends] =
            await Promise.all([
              this.request('inspect.get_all_plugins'),
              this.request('inspect.get_all_backends'),
            ])
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadIntegrations()
  }
}
</script>

<style lang="scss">
.integrations-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-top: .15em;

  .body {
    background: $background-color;
    display: flex;
  }
}
</style>
