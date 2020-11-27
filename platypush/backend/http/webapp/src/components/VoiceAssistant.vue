<template>
  <div class="assistant-modal">
    <Modal ref="assistantModal">
      <div class="icon">
        <i class="fa fa-bell" v-if="state.alerting"></i>
        <i class="fa fa-volume-up" v-else-if="state.responding"></i>
        <i class="fa fa-comment-dots" v-else-if="state.speechRecognized"></i>
        <i class="fa fa-microphone" v-else></i>
      </div>

      <div class="text">
        <div class="listening" v-if="state.listening">
          <span>Assistant listening</span>
        </div>
        <div class="speech-recognized" v-else-if="state.speechRecognized">
          <span v-text="phrase"></span>
        </div>
        <div class="responding" v-else-if="state.responding">
          <span v-text="responseText"></span>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import Utils from "@/Utils";

export default {
  name: "VoiceAssistant",
  components: {Modal},
  mixins: [Utils],

  data() {
    return {
      responseText: '',
      phrase: '',
      hideTimeout: undefined,

      state: {
        listening: false,
        speechRecognized: false,
        responding: false,
        alerting: false,
      },
    };
  },

  methods: {
    reset() {
      this.state.listening = false
      this.state.speechRecognized = false
      this.state.responding = false
      this.state.alerting = false
      this.phrase = ''
      this.responseText = ''
    },

    conversationStart() {
      this.reset()
      this.state.listening = true
      this.$refs.assistantModal.show()

      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout)
        this.hideTimeout = undefined
      }
    },

    conversationEnd() {
      const self = this

      this.hideTimeout = setTimeout(() => {
        this.reset()
        self.$refs.assistantModal.close()
        self.hideTimeout = undefined
      }, 4000)
    },

    speechRecognized(event) {
      this.reset()
      this.state.speechRecognized = true
      this.phrase = event.phrase
      this.$refs.assistantModal.show()
    },

    response(event) {
      this.reset()
      this.state.responding = true
      this.responseText = event.response_text
      this.$refs.assistantModal.show()
    },

    alertOn() {
      this.reset()
      this.state.alerting = true
      this.$refs.assistantModal.show()
    },

    alertOff() {
      this.reset()
      this.state.alerting = false
      this.$refs.assistantModal.close()
    },

    registerHandlers() {
      this.subscribe(this.conversationStart, 'platypush.message.event.assistant.ConversationStartEvent')
      this.subscribe(this.alertOn, 'platypush.message.event.assistant.AlertStartedEvent')
      this.subscribe(this.alertOff, 'platypush.message.event.assistant.AlertEndEvent')
      this.subscribe(this.speechRecognized, 'platypush.message.event.assistant.SpeechRecognizedEvent')
      this.subscribe(this.response, 'platypush.message.event.assistant.ResponseEvent')
      this.subscribe(this.conversationEnd,
          'platypush.message.event.assistant.ConversationEndEvent',
          'platypush.message.event.assistant.NoResponseEvent',
          'platypush.message.event.assistant.ConversationTimeoutEvent')
    },
  },

  mounted() {
    setTimeout(this.registerHandlers, 10000)
  },
}
</script>

<style lang="scss">
$icon-color: #7e8;
$icon-border: 1px solid #ccc;
$icon-shadow: 2px 2px 2px #ccc;

.assistant-modal {
  .modal {
    .body {
      width: 50vw;
      height: 50vh;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      text-align: center;

      .icon {
        font-size: 3em;
        color: $icon-color;
        box-shadow: $icon-shadow;
        border: $icon-border;
        border-radius: 3em;
        padding: 1em;
      }

      .text {
        margin-top: 2.5em;
      }
    }
  }
}
</style>
