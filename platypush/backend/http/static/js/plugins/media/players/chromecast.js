mediaPlayers.chromecast = {
    iconClass: function(item) {
        if (item.type === 'audio') {
            return 'fa fa-volume-up';
        } else {
            return 'fab fa-chromecast';
        }
    },

    scan: async function() {
        return await request('media.chromecast.get_chromecasts');
    },

    status: function(device) {
    },

    play: function(item) {
    },

    stop: function() {
    },
};

