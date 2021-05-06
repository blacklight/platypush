<template>
  <div class="row" v-if="item?.title">
    <div class="left side">Title</div>
    <div class="right side">
      <a :href="`https://www.imdb.com/title/${item.imdb_id}`" target="_blank" v-if="item.imdb_id"
         v-text="item.title" />
      <span v-else v-text="item.title" />
    </div>
  </div>

  <div class="row" v-if="item?.series">
    <div class="left side">TV Series</div>
    <div class="right side" v-text="item.series" />
  </div>

  <div class="row" v-if="item?.season">
    <div class="left side">Season</div>
    <div class="right side" v-text="item.season" />
  </div>

  <div class="row" v-if="item?.episode">
    <div class="left side">Episode</div>
    <div class="right side" v-text="item.episode" />
  </div>

  <div class="row" v-if="item?.num_seasons">
    <div class="left side">Number of seasons</div>
    <div class="right side" v-text="item.num_seasons" />
  </div>

  <div class="row" v-if="item?.synopsis">
    <div class="left side">Synopsis</div>
    <div class="right side" v-text="item.synopsis" />
  </div>

  <div class="row" v-if="item?.description">
    <div class="left side">Description</div>
    <div class="right side" v-text="item.description" />
  </div>

  <div class="row" v-if="item?.summary">
    <div class="left side">Summary</div>
    <div class="right side" v-text="item.summary" />
  </div>

  <div class="row" v-if="item?.overview">
    <div class="left side">Overview</div>
    <div class="right side" v-text="item.overview" />
  </div>

  <div class="row" v-if="item?.duration">
    <div class="left side">Duration</div>
    <div class="right side" v-text="convertTime(item.duration)" />
  </div>

  <div class="row" v-if="item?.country">
    <div class="left side">Country</div>
    <div class="right side" v-text="item.country" />
  </div>

  <div class="row" v-if="item?.network">
    <div class="left side">Network</div>
    <div class="right side" v-text="item.network" />
  </div>

  <div class="row" v-if="item?.status">
    <div class="left side">Status</div>
    <div class="right side" v-text="item.status" />
  </div>

  <div class="row" v-if="item?.rating">
    <div class="left side">Rating</div>
    <div class="right side" v-text="item.rating.percentage" />
  </div>

  <div class="row" v-if="item?.rating">
    <div class="left side">Votes</div>
    <div class="right side" v-text="item.rating.votes" />
  </div>

  <div class="row" v-if="item?.genres">
    <div class="left side">Genres</div>
    <div class="right side" v-text="item.genres.join(', ')" />
  </div>

  <div class="row" v-if="item?.channelId">
    <div class="left side">Channel</div>
    <div class="right side">
      <a :href="`https://www.youtube.com/channel/${item.channelId}`" target="_blank"
         v-text="item.channelTitle || `https://www.youtube.com/channel/${item.channelId}`" />
    </div>
  </div>

  <div class="row" v-if="item?.year">
    <div class="left side">Year</div>
    <div class="right side" v-text="item.year" />
  </div>

  <div class="row" v-if="item?.publishedAt">
    <div class="left side">Published at</div>
    <div class="right side" v-text="formatDate(item.publishedAt, true)" />
  </div>

  <div class="row" v-if="item?.file">
    <div class="left side">File</div>
    <div class="right side" v-text="item.file" />
  </div>

  <div class="row" v-if="item?.url">
    <div class="left side">URL</div>
    <div class="right side url">
      <a :href="item.url" target="_blank" v-text="item.url" />
    </div>
  </div>

  <div class="row" v-if="item?.trailer">
    <div class="left side">Trailer</div>
    <div class="right side url">
      <a :href="item.trailer" target="_blank" v-text="item.trailer" />
    </div>
  </div>

  <div class="row" v-if="item?.size">
    <div class="left side">Size</div>
    <div class="right side" v-text="convertSize(item.size)" />
  </div>

  <div class="row" v-if="item?.quality">
    <div class="left side">Quality</div>
    <div class="right side" v-text="item.quality" />
  </div>

  <div class="row" v-if="item?.seeds">
    <div class="left side">Seeds</div>
    <div class="right side" v-text="item.seeds" />
  </div>

  <div class="row" v-if="item?.peers">
    <div class="left side">Peers</div>
    <div class="right side" v-text="item.peers" />
  </div>

  <div class="row" v-if="item?.language">
    <div class="left side">Language</div>
    <div class="right side" v-text="item.language" />
  </div>
</template>

<script>
import Utils from "@/Utils";
import MediaUtils from "@/components/Media/Utils";

export default {
  name: "Info",
  mixins: [Utils, MediaUtils],
  props: {
    item: {
      type: Object,
      default: () => {},
    }
  }
}
</script>

<style lang="scss" scoped>
.row {
  display: flex;
  min-height: 3em;
  padding: .5em 1em;

  @include until ($tablet) {
    flex-direction: column;
  }

  @include from ($tablet) {
    align-items: center;
  }

  &:not(:last-child) {
    border-bottom: $default-border-2;
  }

  &:hover {
    background: $hover-bg;
    border-radius: .5em;
  }

  .side {
    align-items: center;
    display: inline-flex;

    &.url {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    @include until ($tablet) {
      display: flex;

      &.left {
        font-weight: bold;
      }

      &.right {
        justify-content: left;
      }
    }

    @include from ($tablet) {
      display: inline-flex;

      &.left {
        width: 22%;
        margin-right: 3%;
      }

      &.right {
        width: 75%;
        justify-content: right;
      }
    }
  }
}
</style>
