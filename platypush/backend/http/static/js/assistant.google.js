$(document).ready(function() {
    var onEvent = function(event) {
        console.log(event);

        switch (event.args.type) {
            case 'platypush.message.event.assistant.ConversationStartEvent':
                createNotification({
                    'text': 'Assistant listening',
                    'icon': 'microphone',
                });

                break;

            case 'platypush.message.event.assistant.SpeechRecognizedEvent':
                createNotification({
                    'title': 'Speech recognized',
                    'text': event.args.phrase,
                    'icon': 'microphone',
                });

                break;

            case 'platypush.message.event.assistant.ResponseEvent':
                createNotification({
                    'title': 'Assistant response',
                    'text': event.args.response_text,
                    'icon': 'volume-up',
                });

                break;

            case 'platypush.message.event.assistant.ConversationEndEvent':
                break;
        }
    };

    var initEvents = function() {
        window.registerEventListener(onEvent);
    };

    var init = function() {
        initEvents();
    };

    init();
});

