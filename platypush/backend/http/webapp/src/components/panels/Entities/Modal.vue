<template>
  <Modal :visible="visible" :title="entity.name || entity.external_id">
    <div class="table-row">
      <div class="title">
        Name
        <EditButton @click="editName = true" v-if="!editName" />
      </div>
      <div class="value">
        <NameEditor :value="entity.name" @input="onRename"
          @cancel="editName = false" :disabled="loading" v-if="editName" />
        <span v-text="entity.name" v-else />
      </div>
    </div>

    <div class="table-row">
      <div class="title">Icon</div>
      <div class="value icon-container">
        <i class="icon" :class="entity.meta.icon.class" v-if="entity?.meta?.icon?.class" />
      </div>
    </div>

    <div class="table-row">
      <div class="title">Plugin</div>
      <div class="value" v-text="entity.plugin" />
    </div>

    <div class="table-row">
      <div class="title">Internal ID</div>
      <div class="value" v-text="entity.id" />
    </div>

    <div class="table-row" v-if="entity.external_id">
      <div class="title">External ID</div>
      <div class="value" v-text="entity.external_id" />
    </div>

    <div class="table-row" v-if="entity.description">
      <div class="title">Description</div>
      <div class="value" v-text="entity.description" />
    </div>

    <div class="table-row" v-if="entity.created_at">
      <div class="title">Created at</div>
      <div class="value" v-text="formatDateTime(entity.created_at)" />
    </div>

    <div class="table-row" v-if="entity.updated_at">
      <div class="title">Updated at</div>
      <div class="value" v-text="formatDateTime(entity.updated_at)" />
    </div>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";
import EditButton from "@/components/elements/EditButton";
import NameEditor from "@/components/elements/NameEditor";
import Utils from "@/Utils";

export default {
  name: "Entity",
  components: {Modal, EditButton, NameEditor},
  mixins: [Utils],
  emits: ['input', 'loading'],
  props: {
    entity: {
      type: Object,
      required: true,
    },

    visible: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      editName: false,
      editIcon: false,
    }
  },

  methods: {
    async onRename(newName) {
      this.loading = true

      try {
        const req = {}
        req[this.entity.id] = newName
        await this.request('entities.rename', req)
      } finally {
        this.loading = false
        this.editName = false
      }
    }
  },
}
</script>

<style lang="scss" scoped>
:deep(.modal) {
  .icon-container {
    display: inline-flex;
    align-items: center;
  }
}
</style>
