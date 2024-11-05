<template>
  <div class="movies index">
    <Loading v-if="isLoading" />

    <NoItems :with-shadow="false"
             v-else-if="movies.length === 0">
      No movies found.
    </NoItems>

    <Results :results="movies"
             :sources="{'jellyfin': true}"
             :filter="filter"
             :selected-result="selectedResult"
             @add-to-playlist="$emit('add-to-playlist', $event)"
             @download="$emit('download', $event)"
             @play="$emit('play', $event)"
             @play-with-opts="$emit('play-with-opts', $event)"
             @remove-from-playlist="$emit('remove-from-playlist', $event)"
             @select="selectedResult = $event"
             @view="$emit('view', $event)"
             v-else />

    <SortButton :value="sort"
                :with-release-date="true"
                :with-critic-rating="true"
                :with-community-rating="true"
                @input="sort = $event"
                v-if="movies.length > 0" />
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Mixin from "@/components/panels/Media/Providers/Jellyfin/Mixin";
import NoItems from "@/components/elements/NoItems";
import Results from "@/components/panels/Media/Results";
import SortButton from "@/components/panels/Media/Providers/Jellyfin/components/SortButton";

export default {
  mixins: [Mixin],
  components: {
    Loading,
    NoItems,
    Results,
    SortButton,
  },

  computed: {
    movies() {
      return this.sortedItems?.filter((item) => item.item_type === 'movie') ?? []
    },
  },

  async mounted() {
    await this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "@/components/panels/Media/Providers/Jellyfin/common.scss";

.index {
  position: relative;
}
</style>
