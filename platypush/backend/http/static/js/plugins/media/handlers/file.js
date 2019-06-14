mediaHandlers.file = {
    icon: 'hdd',

    matchesUrl: function(url) {
        return url.startsWith('file:///') || url.startsWith('/');
    },
};

