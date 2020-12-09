<template>
  <Loading v-if="loading" />
  <div class="scene row name" @click="onSelect">
    {{ scene.name || `[Scene ${scene.id}]` }}
  </div>
</template>

<script>
export default {
  name: "Light",
  emits: ['select'],
  props: {
    scene: {
      type: Object,
      default: () => {},
    },

    group: {
      type: Object,
      default: () => {},
    },

    loading: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    onSelect() {
      if (this.loading)
        return false

      this.$emit('select')
    },
  },
}
</script>
