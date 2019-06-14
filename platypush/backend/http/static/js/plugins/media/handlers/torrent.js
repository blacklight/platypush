mediaHandlers.torrent = {
    icon: 'magnet',

    matchesUrl: function(url) {
        return url.startsWith('magnet:?') || url.endsWith('.torrent');
    },
};

