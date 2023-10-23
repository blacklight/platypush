<template>
  <div class="entity assistant-container">
    <TextPrompt ref="prompt">
      Enter a text query to send to the assistant.
    </TextPrompt>

    <div class="head" @click="onHeadClick">
      <div class="col-1 icon entity-icon" ref="icon">
        <EntityIcon
          :entity="value"
          :class="{active: value.conversation_running}"
          :loading="loading"
          :error="error" />
      </div>

      <div class="label">
        <div class="name" ref="name" v-text="value.name" />
      </div>

      <div class="value-container">
        <button @click.stop="collapsed = !collapsed">
          <i class="fas"
            :class="{'fa-angle-up': !collapsed, 'fa-angle-down': collapsed}" />
        </button>
      </div>
    </div>

    <div class="body" ref="body" v-if="!collapsed" @click.stop="prevent">
      <div class="row" @click.stop="stopConversation" v-if="value.conversation_running">
        <div class="icon">
          <i class="fas fa-comment-slash" />
        </div>
        <div class="label">
          <div class="name">Stop Conversation</div>
        </div>
        <div class="value">
          <ToggleSwitch
            @click.stop="stopConversation"
            :value="false"
            :disabled="loading" />
        </div>
      </div>

      <div class="row" @click.stop="startConversation" v-else>
        <div class="icon">
          <i class="fas fa-comment" />
        </div>
        <div class="label">
          <div class="name">Start Conversation</div>
        </div>
        <div class="value">
          <ToggleSwitch
            @click.stop="startConversation"
            :value="false"
            :disabled="loading" />
        </div>
      </div>

      <div class="row" @click.stop="toggleMute">
        <div class="icon">
          <i class="fas fa-microphone-lines-slash" />
        </div>
        <div class="label">
          <div class="name">Muted</div>
        </div>
        <div class="value">
          <ToggleSwitch
            @click.stop="toggleMute"
            :value="value.is_muted"
            :disabled="loading" />
        </div>
      </div>

      <div class="row" @click.stop="showPrompt">
        <div class="icon">
          <i class="fas fa-keyboard" />
        </div>
        <div class="label">
          <div class="name">Send query from text prompt</div>
        </div>
        <div class="value">
          <ToggleSwitch
            @click.stop="showPrompt"
            :value="false"
            :disabled="loading" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TextPrompt from "@/components/elements/TextPrompt"
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import EntityIcon from "./EntityIcon"
import EntityMixin from "./EntityMixin"

export default {
  name: 'Assistant',
  mixins: [EntityMixin],
  components: {
    EntityIcon,
    TextPrompt,
    ToggleSwitch,
  },

  data() {
    return {
      collapsed: true,
      showTextQueryPrompt: false,
      modalId: 'assistant-text-prompt-modal',
    }
  },

  methods: {
    hidePrompt() {
      document.body.querySelector(`#${this.modalId}`)?.remove()
    },

    showPrompt() {
      const modalElement = this.$refs.prompt.$el
      this.hidePrompt()

      modalElement.id = this.modalId
      modalElement.classList.remove('hidden')

      const input = modalElement.querySelector('input[type="text"]')
      const form = modalElement.querySelector('form')
      if (form) {
        form.addEventListener('submit', (event) => {
          event.stopPropagation()
          this.onTextPrompt(input?.value)
        })
      }

      const cancelBtn = modalElement.querySelector('.cancel-btn')
      if (cancelBtn) {
        cancelBtn.onclick = (event) => {
          this.hidePrompt()
          event.stopPropagation()
        }
      }

      modalElement.onclick = (event) => {
        const modalContent = modalElement.querySelector('.modal')
        if (modalContent?.contains(event.target)) {
          event.stopPropagation()
          return false
        }

        this.hidePrompt()
      }

      document.body.appendChild(modalElement)
      this.$nextTick(() => {
        modalElement.querySelector('input[type="text"]').focus()
      })
    },

    onHeadClick(event) {
      if (
        this.$refs.name.contains(event.target) ||
        this.$refs.icon.contains(event.target)
      ) {
        // Propagate the event upwards and let it open the entity modal
        return true
      }

      // Toggle the collapse state if the click is outside of the entity
      // name/icon
      this.collapsed = !this.collapsed
      event.stopPropagation()
    },

    async toggleMute() {
      await this.request('entities.execute', {
        id: this.value.id,
        action: 'toggle_mute',
      })
    },

    async startConversation() {
      await this.request('entities.execute', {
        id: this.value.id,
        action: 'start_conversation',
      })
    },

    async stopConversation() {
      await this.request('entities.execute', {
        id: this.value.id,
        action: 'stop_conversation',
      })
    },

    async onTextPrompt(query) {
      await this.request('entities.execute', {
        id: this.value.id,
        action: 'send_text_query',
        query: query,
      })

      this.hidePrompt()
    },
  }
}
</script>

<style lang="scss" scoped>
@import "common";

$icon-size: 2em;

.assistant-container {
  .body {
    padding: 0;
  }

  .row {
    margin: 0;
    padding: 1em 0.5em;
    display: flex;

    &:hover {
      background: $hover-bg;
    }

    &:not(:last-child) {
      border-bottom: 1px solid $border-color-1;
    }

    .icon {
      flex: 0 0 $icon-size;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .label {
      width: calc(100% - $icon-size);
    }
  }

  :deep(.entity-icon) {
    .active {
      color: $selected-fg;
    }
  }
}
</style>
