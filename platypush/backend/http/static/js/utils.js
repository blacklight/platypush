function enterFullScreen() {
    return document.getElementsByTagName('body')[0].requestFullscreen();
}

function exitFullScreen() {
    const self = this;
    return document.exitFullscreen();
}

