<template>
  <div class="tts-container">
    <form @submit.prevent="talk">
      <div class="field text-container">
        <label>
          <input type="text" name="text" placeholder="Text to say" :disabled="talking">
        </label>
      </div>
      <div class="field lang-container">
        <label>
          <input type="text" name="language" placeholder="Language code" :disabled="talking">
        </label>
      </div>
      <div class="field buttons">
        <button type="submit" :disabled="talking">
          <i class="fa fa-volume-up"></i>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Panel",
  mixins: [Utils],

  props: {
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      talking: false,
    }
  },

  methods: {
    async talk(event) {
      const args = [...event.target.querySelectorAll('input')].reduce((obj, el) => {
        if (el.value.length)
          obj[el.name] = el.value
        return obj
      }, {})

      this.talking = true
      try {
        await this.request(`${this.pluginName}.say`, args)
      } finally {
        this.talking = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.tts-container {
  height: max-content;
  background: $background-color;
  display: flex;
  justify-content: center;
  border: $default-border-3;
  box-shadow: $border-shadow-bottom-right;

  @media screen and (max-width: calc(#{$tablet - 1px})) {
    width: 100%;
  }

  @media screen and (min-width: $tablet) {
    width: 80%;
    border-radius: 1.5em;
    margin: 1.5em auto;
  }

  @media screen and (min-width: $desktop) {
    width: 30em;
  }

  form {
    width: 100%;
    border: none;
    box-shadow: none;
    padding: 1em .5em;
    margin: 0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    flex-direction: row;

    .field {
      margin: 0 .5em;
    }

    .text-container {
      width: 100%;
      margin-bottom: 1em;
    }

    input[type=text] {
      width: 100%;
    }

    button {
      border-radius: 1.5em;
    }

    input, button {
      &:hover {
        border-color: $default-hover-fg;
      }
    }
  }
}
</style>