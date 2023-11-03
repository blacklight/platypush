<template>
  <div class="restart-btn-container">
    <ConfirmDialog ref="modal" @input="restart">
      Are you sure that you want to restart the application?
    </ConfirmDialog>

    <button class="btn btn-default restart-btn" @click="showDialog" @touch="showDialog">
      <i class="fas fa-redo-alt" /> &nbsp; Restart Application
    </button>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog"
import Utils from '@/Utils'

export default {
  name: "RestartButton",
  components: {ConfirmDialog},
  mixins: [Utils],
  methods: {
    showDialog() {
      this.$refs.modal.show()
    },

    async restart() {
      await this.request('application.restart')
    },
  },
}
</script>

<style lang="scss" scoped>
@import "@/style/common.scss";
</style>
