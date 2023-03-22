<template>
  <Modal :visible="visible" class="entity-modal" :title="entity.name || entity.external_id" v-if="entity">
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

    <div class="table-row" v-if="entity.external_url">
      <div class="title">External URL</div>
      <div class="value url">
        <a :href="entity.external_url" target="_blank" :text="entity.external_url" />
      </div>
    </div>

    <div class="table-row" v-if="entity.image_url">
      <div class="title">Image</div>
      <div class="value">
        <img class="entity-image" :src="entity.image_url">
      </div>
    </div>

    <div class="table-row" v-if="parent">
      <div class="title">Parent</div>
      <div class="value">
        <a class="url" @click="$emit('entity-update', parent.id)"
          v-text="parent.name"
        />
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

    <div class="table-row delete-entity-container"
      @click="$refs.deleteConfirmDiag.show()">
      <div class="title">Delete Entity</div>
      <div class="value">
        <button @click.stop="$refs.deleteConfirmDiag.show()">
          <i class="fas fa-trash" />
        </button>
      </div>
    </div>

    <div class="section children-container" v-if="Object.keys(children || {}).length">
      <div class="title section-title" @click="childrenCollapsed = !childrenCollapsed">
       <div class="col-11">
         <i class="fas fa-sitemap" /> &nbsp;
         Children
       </div>

       <div class="col-1 pull-right">
         <i class="fas"
           :class="{'fa-chevron-down': childrenCollapsed, 'fa-chevron-up': !childrenCollapsed}" />
       </div>
      </div>

      <div class="children-container-info" v-if="!childrenCollapsed">
        <div class="table-row" :class="{hidden: !child.name?.length || child.is_configuration}"
          v-for="child in children" :key="child.id">
          <div class="value">
            <a class="url" @click="$emit('entity-update', child.id)"
              v-text="child.name"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="section extra-info-container">
      <div class="title section-title" @click="extraInfoCollapsed = !extraInfoCollapsed">
       <div class="col-11">
         <i class="fas fa-circle-info" /> &nbsp;
         Extra Info
       </div>

       <div class="col-1 pull-right">
         <i class="fas"
           :class="{'fa-chevron-down': extraInfoCollapsed, 'fa-chevron-up': !extraInfoCollapsed}" />
       </div>
      </div>

      <div class="extra-info" v-if="!extraInfoCollapsed">
        <div v-for="value, attr in entity" :key="attr">
          <div class="table-row" v-if="value != null && specialFields.indexOf(attr) < 0">
            <div class="title" v-text="prettify(attr)" />
            <div class="value" v-text="stringify(value)" />
          </div>
        </div>

        <div v-for="value, attr in (entity.data || {})" :key="attr">
          <div class="table-row" v-if="value != null">
            <div class="title" v-text="prettify(attr)" />
            <div class="value" v-text="stringify(value)" />
          </div>
        </div>
      </div>
    </div>

    <div class="section config-container"
      v-if="computedConfig.length">
      <div class="title section-title"
        @click="configCollapsed = !configCollapsed">
       <div class="col-11">
         <i class="fas fa-screwdriver-wrench" /> &nbsp;
         Configuration
       </div>

       <div class="col-1 pull-right">
         <i class="fas"
           :class="{'fa-chevron-down': configCollapsed, 'fa-chevron-up': !configCollapsed}" />
       </div>
      </div>

      <div class="entities" v-if="!configCollapsed">
        <Entity
         v-for="entity in computedConfig"
         :key="entity.id"
         :value="entity"
         @input="$emit('input', entity)" />
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
import Entity from "./Entity";
import meta from './meta.json';

// These fields have a different rendering logic than the general-purpose one
const specialFields = [
  'created_at',
  'data',
  'description',
  'external_id',
  'external_url',
  'id',
  'image_url',
  'is_configuration',
  'meta',
  'name',
  'plugin',
  'updated_at',
  'parent_id',
]

export default {
  name: "EntityModal",
  components: {Entity, Modal, EditButton, NameEditor, Icon, ConfirmDialog},
  mixins: [Utils],
  emits: ['input', 'loading', 'entity-update'],
  props: {
    entity: {
      type: Object,
      required: true,
    },

    parent: {
      type: Object,
    },

    children: {
      type: Object,
    },

    visible: {
      type: Boolean,
      default: false,
    },

    configValues: {
      type: Object,
      default: () => {},
    },
  },

  computed: {
    computedConfig() {
      return Object.values(this.configValues).sort(
        (a, b) => (a.name || '').localeCompare(b.name || '')
      )
    },
  },

  data() {
    return {
      loading: false,
      editName: false,
      editIcon: false,
      configCollapsed: true,
      childrenCollapsed: true,
      extraInfoCollapsed: true,
      specialFields: specialFields,
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

    stringify(value) {
      if (value == null)
        return ''
      if (Array.isArray(value) || typeof value === 'object')
        return JSON.stringify(value, null, 2)
      return '' + value
    },
  },
}
</script>

<style lang="scss" scoped>
:deep(.modal) {
  .body {
    padding: 0;

    @include from($desktop) {
      min-width: 45em;
    }

    .table-row {
      box-shadow: none;
      padding: 0.5em;
    }
  }

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
    cursor: pointer;
    button {
      color: $error-fg;
    }
  }

  @mixin section-title {
    display: flex;
    cursor: pointer;
    padding: 1em;
    text-transform: uppercase;
    letter-spacing: 0.033em;
    border-top: $default-border;
    box-shadow: $border-shadow-bottom;

    &:hover {
      background: $hover-bg;
    }
  }

  .section {
    margin: 0;

    .section-title {
      @include section-title;
    }
  }

  .config-container {
    .title {
      @include section-title;
    }
  }

  .extra-info-container {
    .value {
      white-space: pre-wrap;
      opacity: 0.8;
    }
  }

  .value {
    &.url, a {
      text-align: right;
      text-decoration: underline;
      opacity: 0.8;

      &:hover {
        opacity: 0.6;
      }
    }

    .entity-image {
      max-height: 5em;
    }
  }
}
</style>
