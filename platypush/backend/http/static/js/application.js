$(document).ready(function() {
    var websocket;
    var eventListeners = [];

    var initWebsocket = function() {
        websocket = new WebSocket('ws://' + window.location.hostname + ':' + window.websocket_port);
        websocket.onmessage = function(event) {
            for (var listener of eventListeners) {
                data = event.data;
                if (typeof event.data === 'string') {
                    data = JSON.parse(data);
                }

                listener(data);
            }
        };
    };

    var registerEventListener = function(listener) {
        eventListeners.push(listener);
    };

    var init = function() {
        initWebsocket();
    };

    window.registerEventListener = registerEventListener;
    init();
});

