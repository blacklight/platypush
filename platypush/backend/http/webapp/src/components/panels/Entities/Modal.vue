<template>
  <Modal :visible="visible" :title="entity.name || entity.external_id">
    <ConfirmDialog ref="deleteConfirmDiag" title="Confirm entity deletion" @input="onDelete">
      Are you <b>sure</b> that you want to delete this entity? <br/><br/>
      Note: you should only delete an entity if its plugin has been disabled
      or the entity is no longer reachable.<br/><br/>
      Otherwise, the entity will simply be created again upon the next scan.
    </ConfirmDialog>

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
      <div class="title">
        Icon
        <EditButton @click="editIcon = true" v-if="!editIcon" />
      </div>
      <div class="value icon-canvas">
        <span class="icon-editor" v-if="editIcon">
          <NameEditor :value="entity.meta?.icon?.class || entity.meta?.icon?.url" @input="onIconEdit"
            @cancel="editIcon = false" :disabled="loading">
            <button type="button" title="Reset" @click="onIconEdit(null)"
                @touch="onIconEdit(null)">
              <i class="fas fa-rotate-left" />
            </button>
          </NameEditor>
          <span class="help">
            Supported: image URLs or
            <a href="https://fontawesome.com/icons" target="_blank">FontAwesome icon classes</a>.
          </span>
        </span>

        <Icon v-bind="entity?.meta?.icon || {}" v-else />
      </div>
    </div>

    <div class="table-row">
      <div class="title">
        Icon color
      </div>
      <div class="value icon-color-picker">
        <input type="color" :value="entity.meta?.icon?.color" @change="onIconColorEdit">
        <button type="button" title="Reset" @click="onIconColorEdit(null)"
            @touch="onIconColorEdit(null)">
          <i class="fas fa-rotate-left" />
        </button>
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

    <div v-for="value, attr in entity.data || {}" :key="attr">
      <div class="table-row" v-if="value != null">
        <div class="title" v-text="prettify(attr)" />
        <div class="value" v-text="'' + value" />
      </div>
    </div>

    <div class="table-row" v-if="entity.created_at">
      <div class="title">Created at</div>
      <div class="value" v-text="formatDateTime(entity.created_at)" />
    </div>

    <div class="table-row" v-if="entity.updated_at">
      <div class="title">Updated at</div>
      <div class="value" v-text="formatDateTime(entity.updated_at)" />
    </div>

    <div class="table-row delete-entity-container">
      <div class="title">Delete Entity</div>
      <div class="value">
        <button @click="$refs.deleteConfirmDiag.show()">
          <i class="fas fa-trash" />
        </button>
      </div>
    </div>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";
import Icon from "@/components/elements/Icon";
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import EditButton from "@/components/elements/EditButton";
import NameEditor from "@/components/elements/NameEditor";
import Utils from "@/Utils";
import meta from './meta.json'

export default {
  name: "Entity",
  components: {Modal, EditButton, NameEditor, Icon, ConfirmDialog},
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
    },

    async onDelete() {
      this.loading = true

      try {
        await this.request('entities.delete', [this.entity.id])
      } finally {
        this.loading = false
      }
    },

    async onIconEdit(newIcon) {
      this.loading = true

      try {
        const icon = {url: null, class: null}
        if (newIcon?.length) {
          if (newIcon.startsWith('http'))
            icon.url = newIcon
          else
            icon.class = newIcon
        } else {
          icon.url = (meta[this.entity.type] || {})?.icon?.url
          icon.class = (meta[this.entity.type] || {})?.icon?.['class']
        }

        const req = {}
        req[this.entity.id] = {icon: icon}
        await this.request('entities.set_meta', req)
      } finally {
        this.loading = false
        this.editIcon = false
      }
    },

    async onIconColorEdit(event) {
      this.loading = true

      try {
        const icon = this.entity.meta?.icon || {}
        if (event)
          icon.color = event.target.value
        else
          icon.color = null

        const req = {}
        req[this.entity.id] = {icon: icon}
        await this.request('entities.set_meta', req)
      } finally {
        this.loading = false
        this.editIcon = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
:deep(.modal) {
  .icon-canvas {
    display: inline-flex;
    align-items: center;

    @include until($tablet) {
      .icon-container {
        justify-content: left;
      }
    }

    @include from($tablet) {
      .icon-container {
        justify-content: right;
      }
    }
  }

  .icon-editor {
    display: flex;
    flex-direction: column;
  }

  button {
    border: none;
    background: none;
    padding: 0 0.5em;
  }

  .help {
    font-size: 0.75em;
  }

  .delete-entity-container {
    color: $error-fg;
    button {
      color: $error-fg;
    }
  }
}
</style>
