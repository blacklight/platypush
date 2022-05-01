<template>
  <div class="entity light-container">
    <div class="head" :class="{expanded: expanded}">
      <div class="col-1 icon">
        <EntityIcon :icon="icon" :loading="loading" :error="error" />
      </div>

      <div class="col-s-8 col-m-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-s-3 col-m-2 buttons pull-right">
        <button @click.stop="expanded = !expanded">
          <i class="fas"
            :class="{'fa-angle-up': expanded, 'fa-angle-down': !expanded}" />
        </button>

        <ToggleSwitch :value="value.on" @input="toggle"
          @click.stop :disabled="loading || value.is_read_only" />
      </div>
    </div>

    <div class="body" v-if="expanded" @click.stop="prevent">
      <div class="row" v-if="cssColor">
        <div class="icon">
          <i class="fas fa-palette" />
        </div>
        <div class="input">
          <input type="color" :value="cssColor" @change="setLight({color: $event.target.value})" />
        </div>
      </div>

      <div class="row" v-if="value.brightness">
        <div class="icon">
          <i class="fas fa-sun" />
        </div>
        <div class="input">
          <Slider :range="[value.brightness_min, value.brightness_max]"
            :value="value.brightness" @input="setLight({brightness: $event.target.value})" />
        </div>
      </div>

      <div class="row" v-if="value.saturation">
        <div class="icon">
          <i class="fas fa-droplet" />
        </div>
        <div class="input">
          <Slider :range="[value.saturation_min, value.saturation_max]"
            :value="value.saturation" @input="setLight({saturation: $event.target.value})" />
        </div>
      </div>

      <div class="row" v-if="value.temperature">
        <div class="icon">
          <i class="fas fa-temperature-half" />
        </div>
        <div class="input">
          <Slider :range="[value.temperature_min, value.temperature_max]"
            :value="value.temperature" @input="setLight({temperature: $event.target.value})"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Slider from "@/components/elements/Slider"
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import {ColorConverter} from "@/components/panels/Light/color";

export default {
  name: 'Light',
  components: {ToggleSwitch, Slider, EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      expanded: false,
      colorConverter: null,
    }
  },

  computed: {
    rgbColor() {
      if (
        !this.colorConverter || this.value.hue == null ||
        (this.value.x == null && this.value.y == null)
      )
        return
      if (this.value.meta?.icon?.color)
        return this.value.meta.icon.color

      if (this.value.x && this.value.y)
        return this.colorConverter.xyToRgb(
          this.value.x,
          this.value.y,
          this.value.brightness
        )

      return this.colorConverter.hslToRgb(
        this.value.hue,
        this.value.saturation,
        this.value.brightness
      )
    },

    cssColor() {
      const rgb = this.rgbColor
      if (rgb)
        return this.colorConverter.rgbToHex(rgb)
      return null
    },

    icon() {
      const icon = {...(this.value.meta?.icon || {})}
      if (!icon.color && this.cssColor)
        icon.color = this.cssColor
      return icon
    },
  },

  methods: {
    prevent(event) {
      event.stopPropagation()
      return false
    },

    async toggle(event) {
      event.stopPropagation()
      this.$emit('loading', true)

      try {
        await this.request('entities.execute', {
          id: this.value.id,
          action: 'toggle',
        })
      } finally {
        this.$emit('loading', false)
      }
    },

    async setLight(attrs) {
      if (attrs.color) {
        const rgb = this.colorConverter.hexToRgb(attrs.color)
        if (this.value.x != null && this.value.y != null) {
          attrs.xy = this.colorConverter.rgbToXY(...rgb)
          delete attrs.color
        } else if (this.value.hue != null) {
          [attrs.hue, attrs.saturation, attrs.brightness] = this.colorConverter.rgbToHsl(...rgb)
          delete attrs.color
        }
      }

      this.execute({
        type: 'request',
        action: this.value.plugin + '.set_lights',
        args: {
          lights: [this.value.external_id],
          ...attrs,
        }
      })

      this.$emit('input', attrs)
    },
  },

  mounted() {
    const ranges = {}
    if (this.value.hue)
      ranges.hue = [this.value.hue_min, this.value.hue_max]
    if (this.value.saturation)
      ranges.sat = [this.value.saturation_min, this.value.saturation_max]
    if (this.value.brightness)
      ranges.bri = [this.value.brightness_min, this.value.brightness_max]
    if (this.value.temperature)
      ranges.ct = [this.value.temperature_min, this.value.temperature_max]

    this.colorConverter = new ColorConverter(ranges)
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.light-container {
  .body {
    .row {
      display: flex;

      .icon {
        width: 2em;
        text-align: center;
      }

      .input {
        width: calc(100% - 2em);

        [type=color] {
          width: 100%;
        }

        :deep(.slider) {
          margin-top: 0.5em;
        }
      }
    }
  }
}
</style>
