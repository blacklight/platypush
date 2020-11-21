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
  border-radius: .5rem;
  margin-bottom: 1rem;
  margin-right: 1rem;
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
    padding: .4rem;
    line-height: 3rem;
    letter-spacing: .1rem;
    font-weight: bold;
  }

  .body {
    @extend .vertical-center;
    height: 6em;
    overflow: hidden;
    padding-bottom: 1rem;
    letter-spacing: .05rem;
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
        font-size: 2.5rem;
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