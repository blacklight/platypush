<template>
  <div class="tv-samsung-ws-container">
    <div class="controls" tabindex="1">
      <div class="row section">
        <div class="col-4">
          <button @click="home" value="home" title="Home">
            <i class="fas fa-home" />
          </button>
        </div>
        <div class="col-4">&nbsp;</div>
        <div class="col-4 pull-right">
          <button @click="power" class="power" value="power" title="Power Off">
            <i class="fas fa-power-off" />
          </button>
        </div>
      </div>

      <div class="row rows section">
        <div class="row">
          <div class="col-4">
            <button @click="back" value="back" title="Back">
              <i class="fas fa-undo" />
            </button>
          </div>
          <div class="col-4">
            <button @click="info" value="info" title="Info">
              <i class="fas fa-info" />
            </button>
          </div>
          <div class="col-4">
            <button @click="source" value="source" title="Select source">
              <i class="fas fa-plug" />
            </button>
          </div>
        </div>
        <div class="row">
          <div class="col-4">
            <button @click="menu" value="menu" title="Menu">
              <i class="fas fa-bars" />
            </button>
          </div>
          <div class="col-4">
            <button @click="tools" value="tools" title="Tools">
              <i class="fas fa-tools" />
            </button>
          </div>
          <div class="col-4">
            <button @click="browser" value="browser" title="Open browser">
              <i class="fas fa-globe" />
            </button>
          </div>
        </div>
      </div>

      <div class="volume-channel section">
        <div class="volume col-5">
          <div class="row">
            <button @click="volumeUp" value="volume_up" title="Volume Up">
              <i class="fas fa-plus" />
            </button>
          </div>
          <div class="row">
            <i class="fas fa-volume-up" />
          </div>
          <div class="row">
            <button @click="volumeDown" value="volume_down" title="Volume Down">
              <i class="fas fa-minus" />
            </button>
          </div>
          <div class="row">
            <button @click="mute" value="mute" title="Mute">
              <i class="fas fa-volume-mute" />
            </button>
          </div>
        </div>

        <div class="col-2">&nbsp;</div>

        <div class="channel col-5">
          <div class="row">
            <button @click="channelUp" value="channel_up" title="Next Channel">
              <i class="fas fa-plus" />
            </button>
          </div>
          <div class="row">
            CH
          </div>
          <div class="row">
            <button @click="channelDown" value="channel_down" title="Previous Channel">
              <i class="fas fa-minus" />
            </button>
          </div>
          <div class="row">
            <button @click="channel" value="channel" title="Select Channel">
              <i class="fas fa-keyboard" />
            </button>
          </div>
        </div>
      </div>

      <div class="directions section">
        <div class="row">
          <div class="col-4">&nbsp;</div>
          <div class="col-4">
            <button @click="up" value="up" title="Up">
              <i class="fas fa-chevron-up" />
            </button>
          </div>
          <div class="col-4">&nbsp;</div>
        </div>

        <div class="row">
          <div class="col-4">
            <button @click="left" value="left" title="Left">
              <i class="fas fa-chevron-left" />
            </button>
          </div>
          <div class="col-4">
            <button @click="enter" value="enter" title="Enter/OK">
              <i class="far fa-circle" />
            </button>
          </div>
          <div class="col-4">
            <button @click="right" value="right" title="Right">
              <i class="fas fa-chevron-right" />
            </button>
          </div>
        </div>

        <div class="row">
          <div class="col-4">&nbsp;</div>
          <div class="col-4">
            <button @click="down" value="down" title="Down">
              <i class="fas fa-chevron-down" />
            </button>
          </div>
          <div class="col-4">&nbsp;</div>
        </div>
      </div>

      <div class="row colors section">
        <div class="col-3">
          <button class="color red" @click="color" value="red" title="Red Button" />
        </div>
        <div class="col-3">
          <button class="color green" @click="color" value="green" title="Green Button" />
        </div>
        <div class="col-3">
          <button class="color yellow" @click="color" value="yellow" title="Yellow Button" />
        </div>
        <div class="col-3">
          <button class="color blue" @click="color" value="blue" title="Blue Button" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "TvSamsungWs",
  mixins: [Utils],

  methods: {
    async up() {
      await this.request('tv.samsung.ws.up')
    },

    async down() {
      await this.request('tv.samsung.ws.down')
    },

    async left() {
      await this.request('tv.samsung.ws.left')
    },

    async right() {
      await this.request('tv.samsung.ws.right')
    },

    async enter() {
      await this.request('tv.samsung.ws.enter')
    },

    async power() {
      await this.request('tv.samsung.ws.power')
    },

    async red() {
      await this.request('tv.samsung.ws.red')
    },

    async yellow() {
      await this.request('tv.samsung.ws.yellow')
    },

    async green() {
      await this.request('tv.samsung.ws.green')
    },

    async blue() {
      await this.request('tv.samsung.ws.blue')
    },

    async volumeUp() {
      await this.request('tv.samsung.ws.volume_up')
    },

    async volumeDown() {
      await this.request('tv.samsung.ws.volume_down')
    },

    async channelUp() {
      await this.request('tv.samsung.ws.channel_up')
    },

    async channelDown() {
      await this.request('tv.samsung.ws.channel_down')
    },

    async mute() {
      await this.request('tv.samsung.ws.mute')
    },

    async home() {
      await this.request('tv.samsung.ws.home')
    },

    async back() {
      await this.request('tv.samsung.ws.back')
    },

    async menu() {
      await this.request('tv.samsung.ws.menu')
    },

    async info() {
      await this.request('tv.samsung.ws.info')
    },

    async source() {
      await this.request('tv.samsung.ws.source')
    },

    async tools() {
      await this.request('tv.samsung.ws.tools')
    },

    async browser() {
      const url = prompt('URL to open').trim()
      if (!url.length) {
        return
      }

      await this.request('tv.samsung.ws.open_browser', {'url': url})
    },

    async channel() {
      const ch = prompt('Channel number').trim()
      if (!ch.length) {
        return
      }

      await this.request('tv.samsung.ws.channel', {channel: parseInt(ch)})
    },

    async color(event) {
      await this.request('tv.samsung.ws.' + event.target.value)
    }
  },
}
</script>

<style lang="scss" scoped>
.tv-samsung-ws-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;

  .controls {
    width: 100%;
    max-width: 300px;
    height: max-content;
    display: flex;
    align-items: center;
    flex-direction: column;
    background: $background-color;
    padding: 0 1em;
    border: $default-border-2;
    border-radius: 2em;
    box-shadow: 0 2px 9px 2px #bbb;

    @include until($tablet) {
      height: calc(100% - 1em);
      margin: 0;
    }

    @include from($tablet) {
      justify-content: center;
    }

    @include from($desktop) {
      margin-top: 2em;
    }

    .power { color: red; }
    button { margin: .5em 0; }
  }

  .rows {
    flex-direction: column;

    * {
      button {
        width: 100%;
      }
    }
  }

  .section {
    width: 100%;
    display: flex;
    margin: .5em 0;
    padding: .5em 0;
    border-bottom: $default-border-2;

    &:first-child {
      margin-top: .5em;
    }

    &:last-child {
      margin-bottom: 1em;
    }
  }

  .directions {
    flex-direction: column;

    * {
      button {
        width: 5em;
        height: 4em;
      }
    }
  }

  .volume, .channel {
    text-align: center;
  }

  .colors {
    height: 4em;
    text-align: center;
    border: none;
    margin-top: -1em;

    .color {
      width: 3em;
      height: 3em;
      padding: 0;
      border-radius: 2em;

      &.red { background: red; }
      &.green { background: green; }
      &.yellow { background: yellow; }
      &.blue { background: blue; }
    }
  }
}
</style>
