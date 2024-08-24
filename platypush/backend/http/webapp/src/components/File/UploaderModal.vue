<template>
  <div class="upload-file-modal-container">
    <Modal title="Upload File(s)" :visible="visible" @close="$emit('close')">
      <div class="modal-body">
        <FileUploader :path="path"
                      @complete="$emit('complete')"
                      @start="$emit('start')"
                      @error="$emit('error')" />
      </div>
    </Modal>
  </div>
</template>

<script>
import FileUploader from "./Uploader";
import Modal from "@/components/Modal";

export default {
  mixins: [FileUploader, Modal],
  components: {
    FileUploader,
    Modal,
  },
}
</script>

<style lang="scss" scoped>
.upload-file-modal-container {
  :deep(.modal) {
    .modal-body {
      position: relative;
    }
  }
}
</style>
