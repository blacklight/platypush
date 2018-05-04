$(document).ready(function() {
    var onEvent = function(event) {
        switch (event.args.type) {
            case 'platypush.message.event.pushbullet.PushbulletEvent':
                if (event.args.push_type === 'mirror') {
                    createNotification({
                        'title': event.args.title,
                        'text': event.args.body,
                        'image': 'data:image/png;base64, ' + event.args.icon,
                    });
                }

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

