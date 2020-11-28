<template>
  <div class="notification fade-in" :class="{warning: warning, error: error}" @click="clicked">
    <div class="title" v-if="title" v-text="title"></div>
    <div class="body">
      <div class="image col-3" v-if="image || warning || error">
        <div class="row">
          <img :src="image.src" v-if="image && image.src" alt="">
          <i :class="['fa', 'fa-' + image.icon]" :style="image.color ? '--color: ' + image.color : ''"
             v-else-if="image && image.icon"></i>
          <i :class="image.iconClass" :style="image.color ? '--color: ' + image.color : ''"
             v-else-if="image && image.iconClass"></i>
          <i class="fa fa-exclamation" v-else-if="warning"></i>
          <i class="fa fa-times" v-else-if="error"></i>
        </div>
      </div>
      <div class="text col-9" v-if="text && !!image" v-text="text"></div>
      <div class="text col-9" v-if="html && !!image" v-html="html"></div>
      <div class="text row horizontal-center" v-if="text && !image" v-text="text"></div>
      <div class="text row horizontal-center" v-if="html && !image" v-html="html"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Notification",
  props: ['id','text','html','title','image','link','error','warning'],

  methods: {
    clicked() {
      if (this.link) {
        window.open(this.link, '_blank');
      }

      this.$emit('clicked', this.id);
    },
  },
}
</script>

<style lang="scss" scoped>
.notification {
  background: $notification-bg;
  border: $notification-border;
  border-radius: 1em;
  margin-bottom: 0.25em !important;
  margin-right: 0.1em;
  padding: 0.5em;
  cursor: pointer;

  &:hover {
    background: $notification-hover-bg;
    &.warning { background: $notification-warning-hover-bg; }
    &.error { background: $notification-error-hover-bg; }
  }

  &.warning {
    background: $notification-warning-bg;
    border: $notification-warning-border;
    .image { --color: $notification-warning-icon-color; }
  }

  &.error {
    background: $notification-error-bg;
    border: $notification-error-border;
    .image { --color: $notification-error-icon-color; }
  }

  .title {
    color: $notification-title-fg;
    font-size: 1.25em;
    font-weight: normal;
    margin: 0.25em 0;
    padding: 0;
    letter-spacing: 0.07em;
  }

  .body {
    @extend .vertical-center;
    height: 6em;
    overflow: hidden;
    padding-bottom: 0.1em;
    letter-spacing: 0.05em;
  }

  .image {
    height: 100%;
    text-align: center;
    --color: $notification-icon-color;

    .row {
      @extend .vertical-center;
      @extend .horizontal-center;
      width: 100%;
      height: 100%;

      .fa {
        font-size: 2.5em;
        color: var(--color);
      }

      img {
        width: 80%;
        height: 80%;
      }
    }
  }
}
</style>