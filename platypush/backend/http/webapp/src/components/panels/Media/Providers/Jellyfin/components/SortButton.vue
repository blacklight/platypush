<template>
  <div class="sort-buttons">
    <Dropdown :icon-class="btnIconClass"
              glow right
              :title="title">
      <div class="sort-buttons-dropdown-body">
        <div class="title">Sort Direction</div>
        <DropdownItem text="Ascending"
                      icon-class="fa fa-arrow-up-short-wide"
                      :item-class="{ active: !value?.desc }"
                      @input="onDescChange(false)" />
        <DropdownItem text="Descending"
                      icon-class="fa fa-arrow-down-wide-short"
                      :item-class="{ active: value?.desc }"
                      @input="onDescChange(true)" />

        <div class="title">Sort By</div>
        <DropdownItem text="Name"
                      icon-class="fa fa-font"
                      :item-class="{ active: value?.attr === 'title' }"
                      @input="onAttrChange('title')" />
        <DropdownItem text="Release Date"
                      icon-class="fa fa-calendar"
                      :item-class="{ active: value?.attr === 'year' }"
                      @input="onAttrChange('year')"
                      v-if="withReleaseDate" />
        <DropdownItem text="Critics Rating"
                      icon-class="fa fa-star"
                      :item-class="{ active: value?.attr === 'critic_rating' }"
                      @input="onAttrChange('critic_rating')"
                      v-if="withCriticRating" />
        <DropdownItem text="Community Rating"
                      icon-class="fa fa-users"
                      :item-class="{ active: value?.attr === 'community_rating' }"
                      @input="onAttrChange('community_rating')"
                      v-if="withCommunityRating" />
      </div>
    </Dropdown>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/FloatingDropdownButton";
import DropdownItem from "@/components/elements/DropdownItem";
import Utils from '@/Utils'

export default {
  emits: ['input'],
  mixins: [Utils],
  components: {
    Dropdown,
    DropdownItem,
  },

  props: {
    value: {
      type: Object,
      required: true,
    },

    withReleaseDate: {
      type: Boolean,
      default: false,
    },

    withCriticRating: {
      type: Boolean,
      default: false,
    },

    withCommunityRating: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    btnIconClass() {
      return this.value?.desc ? 'fa fa-arrow-down-wide-short' : 'fa fa-arrow-up-short-wide'
    },

    title() {
      return 'Sort By: ' + (this.value?.attr ?? '[none]') + ' ' + (this.value?.desc ? 'descending' : 'ascending')
    },
  },

  methods: {
    onAttrChange(attr) {
      this.$emit('input', { attr, desc: !!this.value?.desc })
    },

    onDescChange(desc) {
      this.$emit('input', { attr: this.value?.attr, desc })
    },
  },

  watch: {
    value() {
      this.setUrlArgs({
        sort: this.value?.attr,
        desc: this.value?.desc,
      })
    },
  },

  mounted() {
    const urlArgs = this.getUrlArgs()
    const sortBy = urlArgs.sort
    const desc = urlArgs.desc?.toString() === 'true'

    if (sortBy || desc) {
      this.$emit('input', { attr: sortBy, desc })
    }
  },

  unmounted() {
    this.setUrlArgs({
      sort: null,
      desc: null,
    })
  },
}
</script>

<style lang="scss">
.sort-buttons {
  .floating-btn {
    z-index: 100;
  }
}

.sort-buttons-dropdown-body {
  .title {
    font-weight: bold;
    text-align: center;
    box-shadow: $border-shadow-bottom;
    border-top: $default-border-2;
  }

  .item {
    &.active {
      color: $selected-fg;
    }
  }
}
</style>
