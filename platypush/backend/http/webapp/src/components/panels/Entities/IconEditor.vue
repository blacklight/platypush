<template>
  <form class="icon-editor"
        @submit="onIconEdit(newIcon, $event)"
        @click.stop>
    <div class="row item">
      <div class="title">
        Icon
        <EditButton title="Edit Icon"
                    @click.stop="editIcon = true"
                    v-if="!editIcon" />
      </div>
      <div class="value icon-canvas">
        <span class="icon-editor" v-if="editIcon">
          <span class="icon-edit-form" v-if="newIcon != null">
            <span class="icon-container">
              <img :src="currentIcon.url" v-if="currentIcon?.url" />
              <i :class="currentIcon.class" :style="{color: currentIcon.color}" v-else />
            </span>

            <NameEditor :value="currentIcon.url || currentIcon.class"
                        :disabled="loading"
                        @keyup="newIcon = $event.target.value?.trim()"
                        @input="onIconEdit(newIcon)"
                        @cancel="editIcon = false">
              <button type="button"
                      title="Reset"
                      @click.stop="onIconEdit(null, $event)">
                <i class="fas fa-rotate-left" />
              </button>
            </NameEditor>
          </span>

          <span class="help">
            Supported: image URLs or
            <a href="https://fontawesome.com/icons" target="_blank">FontAwesome icon classes</a>.
          </span>
        </span>

        <Icon v-bind="currentIcon" v-else />
      </div>
    </div>

    <div class="row item">
      <div class="title">
        Icon color
      </div>
      <div class="value icon-color-picker">
        <input type="color"
               :value="currentIcon.color"
               @input.stop
               @change.stop="onIconColorEdit">
        <button type="button"
                title="Reset"
                @click.stop="onIconColorEdit(null)">
          <i class="fas fa-rotate-left" />
        </button>
      </div>
    </div>
  </form>
</template>

<script>
import EditButton from "@/components/elements/EditButton";
import Icon from "@/components/elements/Icon";
import NameEditor from "@/components/elements/NameEditor";
import Utils from "@/Utils";
import meta from './meta.json';

export default {
  components: {
    EditButton,
    Icon,
    NameEditor,
  },
  mixins: [Utils],
  emits: ['change', 'input'],
  props: {
    entity: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      editIcon: false,
      loading: false,
      newIcon: null,
      newColor: null,
    }
  },

  computed: {
    currentIcon() {
      return {
        ...((meta[this.entity.type] || {})?.icon || {}),
        ...(this.entity.meta?.icon || {}),
        ...(this.newIcon ? this.iconObj(this.newIcon) : {}),
        ...(this.newColor?.length ? {color: this.newColor} : {}),
      }
    },
  },

  methods: {
    async edit(icon, event) {
      const req = {
        [this.entity.id]: {icon},
      }
      this.loading = true

      if (event)
        event.stopPropagation()

      try {
        const entity = (await this.request('entities.set_meta', req))[0]
        icon = entity?.meta?.icon
        if (icon) {
          this.$emit('input', icon)
        }
      } finally {
        this.loading = false
        this.editIcon = false
      }
    },

    async onIconEdit(newIcon, event) {
      const icon = {
        ...this.currentIcon,
        ...(this.iconObj(newIcon) || {}),
      }

      await this.edit(icon, event)
    },

    async onIconColorEdit(event) {
      const color = event?.target?.value
      const icon = {
        ...this.currentIcon,
        ...(color?.length ? {color} : {color: null}),
      }

      this.newColor = color
      await this.edit(icon, event)
    },

    iconObj(iconStr) {
      if (!iconStr?.length)
        return {
          ...this.currentIcon,
          url: this.entity.meta?.icon?.url,
          class: this.entity.meta?.icon?.class,
        }

      if (iconStr.startsWith('http'))
        return {url: iconStr}

      return {class: iconStr}
    },
  },

  watch: {
    editIcon() {
      this.newIcon = (this.entity.meta?.icon?.['class'] || this.entity.meta?.icon?.url)?.trim()
    },

    newIcon() {
      this.$emit('change', this.currentIcon)
    },

    newColor() {
      this.$emit('change', this.currentIcon)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.icon-editor {
  width: 100%;
  display: flex;
  flex-direction: column;

  .item {
    display: flex;
    align-items: center;
    padding-bottom: 0.5em;

    @include until($tablet) {
      flex-direction: column;
      justify-content: center;
    }

    .title {
      width: 10em;

      @include until($tablet) {
        width: 100%;
      }
    }

    .value {
      display: inline-flex;
      flex: 1;
      justify-content: flex-end;

      @include until($tablet) {
        width: 100%;
        justify-content: flex-start;
      }
    }

    .icon-editor {
      align-items: flex-end;

      @include until($tablet) {
        align-items: flex-start;
      }

      .icon-container {
        margin-right: 0.5em;
      }

      img {
        max-width: 2em;
        max-height: 2em;
      }
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
        margin-right: 0.5em;
      }
    }
  }

  button {
    border: none;
    background: none;
    padding: 0 0.5em;
  }

  .help {
    font-size: 0.75em;
  }
}
</style>
