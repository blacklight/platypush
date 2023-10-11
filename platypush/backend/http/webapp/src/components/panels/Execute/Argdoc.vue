<template>
  <article class="argdoc-container" :class="{mobile: isMobile, widescreen: !isMobile}">
    <h2>
      Argument: <div class="argname" v-text="name" />
      <span class="flag required" v-if="args.required">[Required]</span>
      <span class="flag optional" v-else>[Optional]</span>
    </h2>

    <div class="doc html">
      <Loading v-if="loading" />
      <span v-else>
        <span v-html="doc" v-if="doc?.length" />
        <div class="type" v-if="args.type">
          <b>Type:</b> &nbsp; {{ args.type }}
        </div>
      </span>
    </div>
  </article>
</template>

<script>
import Loading from "@/components/Loading"

export default {
  name: 'Argdoc',
  components: { Loading },
  props: {
    args: {
      type: Object,
      default: () => ({}),
    },
    name: {
      type: String,
      required: true,
    },
    doc: String,
    loading: Boolean,
    isMobile: Boolean,
  }
}
</script>

<style lang="scss" scoped>
@import "common";

.argdoc-container {
  max-height: 50vh;
  display: flex;
  flex-direction: column;

  @include from($tablet) {
    width: calc(100% - #{$params-tablet-width} - 2em);
  }

  @include from($desktop) {
    width: calc(100% - #{$params-desktop-width} - 2em);
  }

  .argname {
    font-weight: bold;
    margin-left: 0.25em;
  }

  .doc {
    width: 100%;
    overflow: auto;
  }

  &.widescreen {
    @include until($tablet) {
      display: none;
    }
  }

  &.mobile {
    width: 100%;
    @include from($tablet) {
      display: none;
    }
  }

  .flag {
    font-size: 0.9em;
    margin-left: 0.5em;
    margin-bottom: 0.1em;

    &.required {
      color: $error-fg;
    }

    &.optional {
      color: $selected-fg;
    }
  }
}
</style>
