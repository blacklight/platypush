$(document).ready(function() {
    var websocket,
        dateTimeInterval,
        websocketReconnectTimeout,
        eventListeners = [];

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

        websocket.onerror = function(event) {
            console.error(event);
        };

        websocket.onclose = function(event) {
            console.log('Websocket closed, code: ' + event.code);
            websocketReconnectTimeout = setTimeout(function() {
                initWebsocket();
            }, 5000);
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

    var init = function() {
        initWebsocket();
        initDateTime();
    };

    window.registerEventListener = registerEventListener;
    init();
});

