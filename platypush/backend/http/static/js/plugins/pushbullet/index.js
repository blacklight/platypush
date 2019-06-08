const Pushbullet = {
    onMsg: function(event) {
        if (event.push_type === 'mirror') {
            createNotification({
                title: event.title,
                text: event.body,
                image: {
                    src: event.icon ? 'data:image/png;base64, ' + event.icon : undefined,
                    icon: event.icon ? undefined : 'bell',
                },
            });
        }
    },

    registerHandlers: function() {
        registerEventHandler(this.onMsg, 'platypush.message.event.pushbullet.PushbulletEvent');
    },
};

onReady(() => {
    Pushbullet.registerHandlers();
});

