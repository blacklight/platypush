<template>
  <div class="light-group-container">
    <MenuPanel>
      <li class="header">
        <button class="back-btn" title="Back" @click="close" v-if="group">
          <i class="fas fa-chevron-left" />
        </button>
      </li>

      <div class="no-lights" v-if="!lights || !Object.keys(lights).length">
        No lights found
      </div>

      <li v-for="(light, id) in lightsSorted" :key="id" v-else>
        <Light :light="light" />
      </li>
    </MenuPanel>
  </div>
</template>

<script>
import Light from "@/components/Light/Light";
import MenuPanel from "@/components/MenuPanel";

export default {
  name: "Group",
  emits: ['close'],
  components: {MenuPanel, Light},
  props: {
    lights: {
      type: Object,
    },

    group: {
      type: Object,
    },
  },

  computed: {
    lightsSorted() {
      if (!this.lights)
        return []

      return Object.entries(this.lights)
          .sort((a, b) => a[1].name.localeCompare(b[1].name))
          .map(([id, light]) => {
            return {
              ...light,
              id: id,
            }
          })
    },
  },

  methods: {
    close(event) {
      event.stopPropagation()
      this.$emit('close')
    },
  },
}
</script>

<style lang="scss">
.light-group-container {
  width: 100%;
  height: 100%;

  .header {
    .back-btn {
      border: 0;

      &:hover {
        border: 0;
        color: $default-hover-fg;
      }
    }
  }

  li.header {
    .back-btn {
      background: none;
      margin-left: -0.75em;
    }
  }
}
</style>
