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
      <IconEditor :entity="entity" @input="onIconEdit" />
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
          <div class="title">
            <EntityIcon :entity="entity" :icon="entity.meta?.icon" /> &nbsp;
            {{ prettify(child.type) }}
          </div>
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
import IconEditor from "./IconEditor";
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import EditButton from "@/components/elements/EditButton";
import EntityIcon from "./EntityIcon"
import NameEditor from "@/components/elements/NameEditor";
import Utils from "@/Utils";
import Entity from "./Entity";

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
  components: {
    ConfirmDialog,
    EditButton,
    Entity,
    EntityIcon,
    IconEditor,
    Modal,
    NameEditor,
  },
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

    onIconEdit(icon) {
      this.$emit(
        'input',
        {
          ...this.entity,
          meta: {...this.entity.meta, icon},
        }
      )
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
@import "common";

:deep(.modal) {
  @include until($tablet) {
    width: 100%;
  }

  .table-row {
    display: flex;
    align-items: center;
    box-shadow: none;
    padding: 0.5em;
    border-bottom: 1px solid $border-color-2;

    &:hover {
      background: $hover-bg;
    }

    .title {
      font-weight: bold;

      @include from($tablet) {
        width: 50%;
        display: inline-block;
      }
    }

    .value {
      overflow: auto;

      @include from($tablet) {
        width: 50%;
        display: inline-block;
        text-align: right;
      }
    }
  }

  .content {
    @include until($tablet) {
      width: calc(100% - 1em) !important;
    }

    @include from($tablet) {
      min-width: 30em;
    }

    .body {
      padding: 0;

      @include from($desktop) {
        min-width: 45em;
      }
    }
  }

  button {
    border: none;
    background: none;
    padding: 0 0.5em;
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

  @include until(#{$tablet - 1}) {
    .entity-container-wrapper {
      &.collapsed {
        border-radius: 0;
        box-shadow: none;
        border-bottom: $default-border;
      }
    }
  }

}
</style>
