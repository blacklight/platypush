<template>
  <div class="switch" @click.stop="onToggle">
    <Loading v-if="loading" />
    <div class="name col-l-10 col-m-9 col-s-8">
      <button v-if="hasInfo" @click.prevent="onInfo">
        <i class="fa fa-info" />
      </button>
      <span class="name-content" v-text="name" />
    </div>
    <div class="toggler col-l-2 col-m-3 col-s-4">
      <ToggleSwitch :disabled="loading" :value="state" @input="onToggle" />
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Loading from "@/components/Loading";

export default {
  name: "Switch",
  components: {Loading, ToggleSwitch},
  emits: ['toggle', 'info'],

  props: {
    name: {
      type: String,
      required: true,
    },

    state: {
      type: Boolean,
      default: false,
    },

    loading: {
      type: Boolean,
      default: false,
    },

    hasInfo: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    onInfo(event) {
      event.stopPropagation()
      this.$emit('info')
      return false
    },

    onToggle(event) {
      event.stopPropagation()
      this.$emit('toggle')
      return false
    },
  }
}
</script>

<style lang="scss" scoped>
.switch {
  width: 100%;
  display: flex;
  position: relative;
  align-items: center;
  padding: .75em .5em;
  border-bottom: $default-border-2;
  cursor: pointer;

  &:hover {
    background: $hover-bg;
  }

  .toggler {
    text-align: right;
  }

  button {
    background: none;
    border: none;

    &:hover {
      color: $default-hover-fg-2;
    }
  }
}
</style>
