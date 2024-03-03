<template>
  <div class="youtube-views-browser grid">
    <div class="item" @click="$emit('select', 'feed')">
      <div class="icon">
        <i class="fas fa-rss" />
      </div>
      <div class="name">Feed</div>
    </div>

    <div class="item" @click="$emit('select', 'playlists')">
      <div class="icon">
        <i class="fas fa-list" />
      </div>
      <div class="name">Playlists</div>
    </div>

    <div class="item" @click="$emit('select', 'subscriptions')">
      <div class="icon">
        <i class="fas fa-user" />
      </div>
      <div class="name">Subscriptions</div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['select'],
}
</script>
