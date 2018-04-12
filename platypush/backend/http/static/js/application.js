$(document).ready(function() {
    var websocket,
        pendingConnection = false,
        openedWebsocket,
        dateTimeInterval,
        websocketTimeoutId,
        websocketReconnectMsecs = 5000,
        eventListeners = [];

    var initWebsocket = function() {
        try {
            websocket = new WebSocket('ws://' + window.location.hostname + ':' + window.websocket_port);
        } catch (err) {
            websocket = undefined;
            return;
        }

        pendingConnection = true;

        var onWebsocketTimeout = function(self) {
            return function() {
                console.log('Websocket reconnection timed out, retrying');
                pendingConnection = false;
                self.close();
                self.onclose();
            };
        };

        websocketTimeoutId = setTimeout(
            onWebsocketTimeout(websocket), websocketReconnectMsecs);

        websocket.onmessage = function(event) {
            for (var listener of eventListeners) {
                data = event.data;
                if (typeof event.data === 'string') {
                    data = JSON.parse(data);
                }

                listener(data);
            }
        };

        websocket.onopen = function(event) {
            if (openedWebsocket) {
                console.log("There's already an opened websocket connection, closing the newly opened one");
                this.onclose = function() {};
                this.close();
            }

            console.log('Websocket connection successful');
            openedWebsocket = this;

            if (pendingConnection) {
                pendingConnection = false;
            }

            if (websocketTimeoutId) {
                clearInterval(websocketTimeoutId);
                websocketTimeoutId = undefined;
            }
        };

        websocket.onerror = function(event) {
            console.error(event);
        };

        websocket.onclose = function(event) {
            if (event) {
                console.log('Websocket closed - code: ' + event.code + ' - reason: ' + event.reason);
            }

            openedWebsocket = undefined;

            if (!pendingConnection) {
                pendingConnection = true;
                initWebsocket();
            }
        };
    };

    var initDateTime = function() {
        var getDateString = function(t) {
            var s = '';
            switch (t.getDay()) {
                case 1: s += 'Mon '; break; case 2: s += 'Tue '; break; case 3: s += 'Wed '; break;
                case 4: s += 'Thu '; break; case 5: s += 'Fri '; break; case 6: s += 'Sat '; break;
                case 7: s += 'Sun '; break;
            }

            s += (t.getDate() < 10 ? '0' : '') + t.getDate() + ' ';
            switch (t.getMonth()) {
                case 0: s += 'Jan '; break; case 1: s += 'Feb '; break; case 2: s += 'Mar '; break;
                case 3: s += 'Apr '; break; case 4: s += 'May '; break; case 5: s += 'Jun '; break;
                case 6: s += 'Jul '; break; case 7: s += 'Ago '; break; case 8: s += 'Sep '; break;
                case 9: s += 'Oct '; break; case 10: s += 'Nov '; break; case 11: s += 'Dec '; break;
            }

            s += t.getFullYear();
            return s;
        };

        var setDateTime = function() {
            var $dateTime = $('#date-time');
            var $date = $dateTime.find('.date');
            var $time = $dateTime.find('.time');
            var now = new Date();

            $date.text(getDateString(now));
            $time.text((now.getHours() < 10 ? '0' : '') + now.getHours() + ':' +
                (now.getMinutes() < 10 ? '0' : '') + now.getMinutes());
        };

        if (dateTimeInterval) {
            clearInterval(dateTimeInterval);
        }

        setDateTime();
        dateTimeInterval = setInterval(setDateTime, 1000);
    };

    var registerEventListener = function(listener) {
        eventListeners.push(listener);
    };

    var initElements = function() {
        var $tabItems = $('main').find('.plugin-tab-item');
        var $tabContents = $('main').find('.plugin-tab-content');

        // Set the active tag on the first plugin tab
        $tabContents.removeClass('active');
        $tabContents.first().addClass('active');

        $tabItems.removeClass('active');
        $tabItems.first().addClass('active');

        $tabItems.on('click', function() {
            var pluginId = $(this).attr('href').substr(1);

            $tabContents.removeClass('active');
            $tabContents.filter(function(i, content) {
                return $(content).attr('id') === pluginId
            }).addClass('active');

        });
    };

    var initModalOpenBindings = function() {
        $('body').on('click touch', '[data-modal]', function(event) {
            var $source = $(event.target);
            var $modal = $($source.data('modal'));
            $modal.fadeIn();
        });
    };

    var initModalCloseBindings = function() {
        $('body').on('click touch', '[data-dismiss-modal]', function(event) {
            var $source = $(event.target);
            var $modal = $($source.data('dismiss-modal'));
            $modal.fadeOut();
        });
    };

    var initModals = function() {
        initModalOpenBindings();
        initModalCloseBindings();
    };

    var init = function() {
        initWebsocket();
        initElements();
        initDateTime();
        initModals();
    };

    window.registerEventListener = registerEventListener;
    init();
});

