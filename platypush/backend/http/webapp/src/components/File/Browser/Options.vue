<template>
  <div class="browser-options">
    <Loading v-if="loading" />

    <div class="options-body" v-else>
      <div class="row item">
        <label>
          <input type="checkbox"
                 :checked="value.showHidden"
                 :value="value.showHidden"
                 @input="e => $emit('input', { ...value, showHidden: e.target.checked })">
          Show hidden files
        </label>
      </div>

      <div class="row item sort-container">
        <span>
          <label>
            Sort by

            <span>
              <select :value="value.sortBy" @input="e => $emit('input', { ...value, sortBy: e.target.value })">
                <option value="name" :selected="value.sortBy === 'name'">Name</option>
                <option value="size" :selected="value.sortBy === 'size'">Size</option>
                <option value="created" :selected="value.sortBy === 'created'">Creation Date</option>
                <option value="last_modified" :selected="value.sortBy === 'last_modified'">Last Modified</option>
              </select>
            </span>
          </label>
        </span>

        <span>
          <label>
              <input type="radio"
                     :checked="!value.reverseSort"
                     @input="e => $emit('input', { ...value, reverseSort: false })">
              Ascending
          </label>
          <label>
              <input type="radio"
                     :checked="value.reverseSort"
                     @input="e => $emit('input', { ...value, reverseSort: true })">
              Descending
          </label>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  emits: ['input'],
  mixins: [Utils],
  components: {
    Loading,
  },

  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.browser-options {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  .options-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
  }

  .item {
    padding: 1em;
    label {
      width: 100%;
      cursor: pointer;
    }

    &:last-child {
      border-bottom: none;
    }
  }

  .sort-container {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;

    span {
      width: 100%;
      display: flex;
      justify-content: space-between;
      padding: 0.5em 0;
    }
  }
}
</style>
