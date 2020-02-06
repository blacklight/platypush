const websocket = {
    ws: undefined,
    instance: undefined,
    pending: false,
    opened: false,
    timeout: undefined,
    reconnectMsecs: 30000,
    handlers: {},
};

function initEvents() {
    try {
        const url_prefix = window.config.has_ssl ? 'wss://' : 'ws://';
        websocket.ws = new WebSocket(url_prefix  + window.location.hostname + ':' + window.config.websocket_port);
    } catch (err) {
        console.error("Websocket initialization error");
        console.log(err);
        return;
    }

    websocket.pending = true;

    const onWebsocketTimeout = function(self) {
        return function() {
            console.log('Websocket reconnection timed out, retrying');
            websocket.pending = false;
            self.close();
            self.onclose();
        };
    };

    websocket.timeout = setTimeout(
        onWebsocketTimeout(websocket.ws), websocket.reconnectMsecs);

    websocket.ws.onmessage = function(event) {
        const handlers = [];
        event = event.data;

        if (typeof event === 'string') {
            try {
                event = JSON.parse(event);
            } catch (e) {
                console.warn('Received invalid non-JSON event');
                console.warn(event);
            }
        }

        console.debug(event);
        if (event.type !== 'event') {
            // Discard non-event messages
            return;
        }

        if (null in websocket.handlers) {
            handlers.push(websocket.handlers[null]);
        }

        if (event.args.type in websocket.handlers) {
            handlers.push(...websocket.handlers[event.args.type]);
        }

        for (const handler of handlers) {
            handler(event.args);
        }
    };

    websocket.ws.onopen = function(event) {
        if (websocket.instance) {
            console.log("There's already an opened websocket connection, closing the newly opened one");
            this.onclose = function() {};
            this.close();
        }

        console.log('Websocket connection successful');
        websocket.instance = this;

        if (websocket.pending) {
            websocket.pending = false;
        }

        if (websocket.timeout) {
            clearTimeout(websocket.timeout);
            websocket.timeout = undefined;
        }
    };

    websocket.ws.onerror = function(event) {
        console.error(event);
    };

    websocket.ws.onclose = function(event) {
        if (event) {
            console.log('Websocket closed - code: ' + event.code + ' - reason: ' + event.reason);
        }

        websocket.instance = undefined;

        if (!websocket.pending) {
            websocket.pending = true;
            initEvents();
        }
    };
}

function registerEventHandler(handler, ...events) {
    if (events.length) {
        // Event type filter specified
        for (const event of events) {
            if (!(event in websocket.handlers)) {
                websocket.handlers[event] = [];
            }

            websocket.handlers[event].push(handler);
        }
    } else {
        // No event type specified, listen to all events
        if (!(null in websocket.handlers)) {
            websocket.handlers[null] = [];
        }

        websocket.handlers[null].push(handler);
    }
}

function onReady(handler) {
    if (document.readyState === "complete" || document.readyState === "loaded") {
        handler();
    } else {
        document.addEventListener("DOMContentLoaded", () => {
            handler();
        }, false);
    }
}

