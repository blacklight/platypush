function enterFullScreen() {
    const body = document.getElementsByTagName('body')[0];
    if (body.requestFullscreen()) {
        return body.requestFullscreen();
    } else if (body.msRequestFullscreen()) {
        return body.msRequestFullscreen();
    } else if (body.mozRequestFullScreen()) {
        return body.mozRequestFullScreen();
    } else if (body.webkitRequestFullscreen()) {
        return body.webkitRequestFullscreen();
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

