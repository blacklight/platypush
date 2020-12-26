<template>
  <Loading v-if="loading" />

  <div class="playlist fade-in" v-else>
    <div class="header-container">
      <MusicHeader>
        <div class="col-8 filter">
          <label>
            <input type="search" placeholder="Filter">
          </label>
        </div>

        <div class="col-4 buttons">
          <button title="Add item" @click="$refs.addToPlaylistModal.visible = true">
            <i class="fa fa-plus"></i>
          </button>

          <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
            <DropdownItem text="Save as playlist" icon-class="fa fa-save" :disabled="!tracks?.length"
                          @click="$refs.savePlaylistModal.visible = true" />
            <DropdownItem text="Swap tracks" icon-class="fa fa-retweet" :disabled="tracks?.length !== 2 || !selectionMode" />
            <DropdownItem :text="selectionMode ? 'End selection' : 'Start selection'" icon-class="far fa-check-square"
                          :disabled="!tracks?.length" @click="selectionMode = !selectionMode" />
            <DropdownItem :text="selectedTracks?.length === tracks?.length ? 'Unselect all' : 'Select all'"
                          icon-class="fa fa-check-double" :disabled="!tracks?.length"
                          @click="selectedTracks = [...Array(tracks.length).keys()]" />
            <DropdownItem text="Clear playlist" icon-class="fa fa-ban" :disabled="!tracks?.length" @click="$emit('clear')" />
          </Dropdown>
        </div>
      </MusicHeader>
    </div>

    <div class="body">
      <div class="no-content" v-if="!tracks?.length">
        No tracks are loaded
      </div>

      <div class="row track" v-for="(track, i) in tracks" :key="i" @dblclick="$emit('play', {pos: i})">
        <div class="col-10">
          <div class="title" v-text="track.title || '[No Title]'" />
          <div class="artist" v-text="track.artist || '[No Artist]'" />
          <div class="album" v-text="track.album" v-if="track.album" />
        </div>

        <div class="col-2 right-side">
          <span class="duration" v-text="convertTime(track.time)" />

          <span class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
              <DropdownItem text="Play" icon-class="fa fa-play" @click="$emit('play', {pos: i})" />
              <DropdownItem text="Add to playlist" icon-class="fa fa-list-ul" />
            </Dropdown>
          </span>
        </div>
      </div>
    </div>
  </div>

  <Modal :visible="false" ref="addToPlaylistModal">
  </Modal>

  <Modal :visible="false" ref="savePlaylistModal">
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";
import MusicHeader from "@/components/panels/Music/Header";
import MediaUtils from "@/components/Media/Utils";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";

export default {
  name: "Playlist",
  mixins: [MediaUtils],
  components: {DropdownItem, Dropdown, Modal, MusicHeader},
  emits: ['play', 'clear', 'add-to-playlist'],
  props: {
    tracks: {
      type: Array,
      default: () => [],
    },

    loading: {
      type: Boolean,
      default: false,
    },

    status: {
      type: Object,
      default: () => {},
    }
  },

  data() {
    return {
      selectionMode: false,
      selectedTracks: [],
    }
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

.playlist {
  width: 100%;
  display: flex;
  flex-direction: column;

  .header-container {
    button {
      border: 0;
      background: none;
    }

    .filter {
      input {
        width: 100%;
      }
    }

    .buttons {
      display: flex;
      justify-content: right;
    }
  }

  .body {
    height: calc(100% - #{$music-header-height});
    overflow: auto;
  }

  .no-content {
    height: 100%;
  }

  .track {
    display: flex;
    justify-content: center;
    padding: .75em .25em .25em .25em;
    box-shadow: 0 2.5px 2px -1px $default-shadow-color;
    cursor: pointer;

    &:hover {
      background: $hover-bg;
    }

    .title {
      font-size: 1em;
      font-weight: normal;
      margin: 0;
    }

    .artist, .album {
      display: inline-flex;
      opacity: 0.7;
      font-size: .9em;
    }

    .artist {
      margin-right: .25em;
    }

    .album {
      @include until($tablet) {
        display: none;
      }

      &::before {
        content: "\2022";
        margin-right: .25em;
      }
    }

    .right-side {
      display: flex;
      justify-content: right;
    }

    .duration,
    .actions {
      display: inline-flex;
      align-items: center;
    }

    .duration {
      font-size: .85em;
      opacity: .7;
    }

    .actions {
      ::v-deep button {
        opacity: .7;
      }
    }
  }
}

::v-deep button {
  background: none;
  padding: .5em .75em;
  border: 0;
}
</style>
