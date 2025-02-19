<template>
  <a class="object renderer" :href="$route.fullPath"
     @click.prevent.stop="onClick">
    <div class="compact" v-if="!expanded">
      <i class="toggler fas fa-caret-right" />
      <span class="delimiter" v-text="typeof output === 'object' ? '{' : '['" />
      <span class="ellipsis">...</span>
      <span class="delimiter" v-text="typeof output === 'object' ? '}' : ']'" />
    </div>

    <div class="expanded" v-else>
      <i class="toggler fas fa-caret-down" />
      <div class="rows">
        <div class="row"
             :class="{even: index % 2 === 0, odd: index % 2 !== 0, args: (value instanceof Object) || Array.isArray(value)}"
             v-for="(value, key, index) in output"
             :key="key">
          <span class="key" v-text="key" />
          <span class="value scalar" v-text="value" v-if="!(value instanceof Object) && !Array.isArray(value)" />
          <span class="value object" v-else>
            <ObjectRenderer :output="value" />
          </span>
        </div>
      </div>
    </div>
  </a>
</template>

<script>
import Mixin from './Mixin'

export default {
  name: 'ObjectRenderer',
  mixins: [Mixin],

  methods: {
    onClick() {
      this.expanded = !this.expanded
    },
  },
}
</script>

<style lang="scss" scoped>
@import "./style.scss";

.renderer {
  .key {
    font-weight: bold;
  }

  .expanded {
    flex-direction: row;
  }

  .compact {
    cursor: pointer;
  }

  .toggler {
    margin: 0.75em 0.75em 0 0;
    cursor: pointer;

    &:hover {
      color: $default-hover-fg;
    }
  }
}
</style>
