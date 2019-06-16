mediaHandlers.file = {
    iconClass: 'fa fa-hdd',

    actions: [
        {
            text: 'Play',
            icon: 'play',
            action: 'play',
        },

        {
            text: 'Download',
            icon: 'download',
            action: function(item, bus) {
                bus.$emit('download', item);
            },
        },

        {
            text: 'View info',
            icon: 'info',
            action: 'info',
        },
    ],
};

