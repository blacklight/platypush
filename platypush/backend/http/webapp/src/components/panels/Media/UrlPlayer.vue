<template>
  <form class="url-player" @submit.prevent="$emit('play', value)">
    <div class="row">
      <label>
        Play URL (use the file:// prefix for local files)
        <input type="text"
               v-model="value"
               ref="playUrlInput"
               autofocus />
      </label>
    </div>

    <div class="row footer">
      <button type="submit" :disabled="!value?.length">
        <i class="fa fa-play"></i> Play
      </button>
    </div>
  </form>
</template>

<script>
export default {
  emits: ['input', 'play'],
  props: {
    playUrl: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      value: this.playUrl,
    }
  },
}
</script>

<style lang="scss" scoped>
.url-player {
  padding: 0;
  margin: 0;
  border: none;
  border-radius: 0;
  box-shadow: none;

  .body {
    padding: 1em !important;
  }

  input[type=text] {
    width: 100%;
  }

  [type=submit] {
    background: initial;
    border-color: initial;
    border-radius: 1.5em;

    &:hover {
      color: $default-hover-fg-2;
    }
  }

  .footer {
    display: flex;
    justify-content: right;
    padding: 0;
    margin-top: 1em;
  }
}
</style>
