const Assistant = Vue.extend({
    template: `
        <modal v-model="visible" id="assistant-google-modal">
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
        </modal>
    `,

    data: function() {
        return {
            responseText: '',
            phrase: '',
            visible: false,
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
        reset: function() {
            this.state.listening = false;
            this.state.speechRecognized = false;
            this.state.responding = false;
            this.state.alerting = false;
            this.phrase = '';
            this.responseText = '';
        },

        conversationStart: function() {
            this.reset();
            this.state.listening = true;
            this.visible = true;

            if (this.hideTimeout) {
                clearTimeout(this.hideTimeout);
                this.hideTimeout = undefined;
            }
        },

        conversationEnd: function() {
            const self = this;

            this.hideTimeout = setTimeout(() => {
                this.reset();
                self.visible = false;
                self.hideTimeout = undefined;
            }, 4000);
        },

        speechRecognized: function(event) {
            this.reset();
            this.state.speechRecognized = true;
            this.phrase = event.phrase;
            this.visible = true;
        },

        response: function(event) {
            this.reset();
            this.state.responding = true;
            this.responseText = event.response_text;
            this.visible = true;
        },

        alertOn: function() {
            this.reset();
            this.state.alerting = true;
            this.visible = true;
        },

        alertOff: function() {
            this.reset();
            this.state.alerting = false;
            this.visible = false;
        },

        registerHandlers: function() {
            registerEventHandler(this.conversationStart, 'platypush.message.event.assistant.ConversationStartEvent');
            registerEventHandler(this.alertOn, 'platypush.message.event.assistant.AlertStartedEvent');
            registerEventHandler(this.alertOff, 'platypush.message.event.assistant.AlertEndEvent');
            registerEventHandler(this.speechRecognized, 'platypush.message.event.assistant.SpeechRecognizedEvent');
            registerEventHandler(this.response, 'platypush.message.event.assistant.ResponseEvent');
            registerEventHandler(this.conversationEnd, 'platypush.message.event.assistant.ConversationEndEvent');
            registerEventHandler(this.conversationEnd, 'platypush.message.event.assistant.NoResponseEvent');
            registerEventHandler(this.conversationEnd, 'platypush.message.event.assistant.ConversationTimeoutEvent');
        },
    },

    mounted: function() {
        this.registerHandlers();
    },
});

onReady(() => {
    const container = document.createElement('div');
    const containerId = 'assistant-google-container';

    container.setAttribute('id', containerId);
    document.querySelector('#app').appendChild(container);

    new Assistant().$mount('#' + containerId);
});

