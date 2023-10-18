<template>
  <div class="stop-btn-container">
    <ConfirmDialog ref="modal" @input="stop">
      Are you sure that you want to stop the application?
      <br /><br />
      <span class="text-danger">
        This will stop the application and you will not be able to restart it
        through the Web interface!
      </span>
    </ConfirmDialog>

    <button class="btn btn-default stop-btn" @click="showDialog" @touch="showDialog">
      <i class="fas fa-stop" /> &nbsp; Stop Application
    </button>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog"
import Utils from '@/Utils'

export default {
  name: "StopButton",
  components: {ConfirmDialog},
  mixins: [Utils],
  methods: {
    showDialog() {
      this.$refs.modal.show()
    },

    async stop() {
      await this.request('application.stop')
    },
  },
}
</script>

<style lang="scss" scoped>
@import "@/style/common.scss";

.text-danger {
  color: $error-fg;
}
</style>
