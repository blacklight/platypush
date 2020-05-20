function enterFullScreen() {
    const app = document.documentElement;
    if (app.requestFullscreen()) {
        return app.requestFullscreen();
    } else if (app.msRequestFullscreen()) {
        return app.msRequestFullscreen();
    } else if (app.mozRequestFullScreen()) {
        return app.mozRequestFullScreen();
    } else if (app.webkitRequestFullscreen()) {
        return app.webkitRequestFullscreen();
    } else {
        console.warn('This browser does not support fullscreen mode');
    }

    // The day will come when browser developers will have to pay web developers
    // back for all the time wasted to write such crappy portable code. A two-lines
    // function becomes a 10-lines function just because they can't talk to
    // one another before implementing sh*t.
}

function exitFullScreen() {
    if (document.exitFullscreen()) {
        return document.exitFullscreen();
    } else if (document.msExitFullscreen()) {
        return document.msExitFullscreen();
    } else if (document.mozCancelFullScreen()) {
        return document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen()) {
        return document.webkitExitFullscreen();
    } else {
        console.warn('This browser does not support fullscreen mode');
    }
}

function toggleFullScreen() {
    const elem = document.fullscreenElement
            || document.webkitFullscreenElement
            || document.msFullscreenElement
            || document.mozFullScreenElement;

    if (elem) {
        exitFullScreen();
    } else {
        enterFullScreen();
    }
}

