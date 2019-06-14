mediaHandlers.youtube = {
    icon: 'youtube',

    matchesUrl: function(url) {
        return url.startsWith('https://youtube.com/watch?v=') ||
            url.startsWith('https://www.youtube.com/watch?v=') ||
            url.startsWith('https://youtu.be/');
    },
};

