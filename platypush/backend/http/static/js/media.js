$(document).ready(function() {
    var $container = $('#video-container'),
        $searchForm = $('#video-search'),
        $videoResults = $('#video-results'),
        $volumeCtrl = $('#video-volume-ctrl'),
        $ctrlForm = $('#video-ctrl'),
        $devsPanel = $('#media-devices-panel'),
        $devsList = $devsPanel.find('.devices-list'),
        $devsBtn = $('button[data-panel="#media-devices-panel"]'),
        $devsBtnIcon = $('#media-devices-panel-icon'),
        $devsRefreshBtn = $devsPanel.find('.refresh-devices'),
        $searchBarContainer = $('#media-search-bar-container'),
        $mediaBtnsContainer = $('#media-btns-container'),
        $mediaItemPanel = $('#media-item-panel'),
        $mediaSubtitlesModal = $('#media-subtitles-modal'),
        $mediaSubtitlesResultsContainer = $mediaSubtitlesModal.find('.media-subtitles-results-container'),
        $mediaSubtitlesResults = $mediaSubtitlesModal.find('.media-subtitles-results'),
        $mediaSubtitlesMessage = $mediaSubtitlesModal.find('.media-subtitles-message'),
        $mediaSearchSubtitles = $ctrlForm.find('[data-modal="#media-subtitles-modal"]'),
        prevVolume = undefined,
        selectedResource = undefined,
        browserVideoWindow = undefined,
        browserVideoElement = undefined;

    const onEvent = (event) => {
        switch (event.args.type) {
            case 'platypush.message.event.media.MediaPlayRequestEvent':
                createNotification({
                    'icon': 'stream',
                    'html': 'Processing media' + ('resource' in event.args
                        ? ' ' + event.args.resource : ''),
                });
                break;

            case 'platypush.message.event.media.MediaPlayEvent':
                createNotification({
                    'icon': 'play',
                    'html': 'Starting media playback' + ('resource' in event.args
                        ? ' for ' + event.args.resource : ''),
                });
                break;

            case 'platypush.message.event.media.MediaPauseEvent':
                createNotification({
                    'icon': 'pause',
                    'html': 'Media playback paused',
                });
                break;

            case 'platypush.message.event.media.MediaStopEvent':
                createNotification({
                    'icon': 'stop',
                    'html': 'Media playback stopped',
                });
                $mediaSearchSubtitles.hide();
                break;
        }
    };

    const updateVideoResults = function(videos) {
        $videoResults.html('');
        for (var video of videos) {
            var $videoResult = $('<div></div>')
                .addClass('video-result')
                .attr('data-url', video['url'])
                .attr('data-panel', '#media-item-panel')
                .html('title' in video ? video['title'] : video['url']);

            var $icon = getVideoIconByUrl(video['url']);
            $icon.prependTo($videoResult);
            $videoResult.appendTo($videoResults);
        }
    };

    const getVideoIconByUrl = function(url) {
        var $icon = $('<i class="fa"></i>');

        if (url.startsWith('file://')) {
            $icon.addClass('fa-download');
        } else if (url.startsWith('https://www.youtube.com/')) {
            $icon.addClass('fa-youtube');
        } else if (url.startsWith('magnet:?')) {
            $icon.addClass('fa-film');
        } else {
            $icon.addClass('fa-video');
        }

        var $iconContainer = $('<span></span>').addClass('video-icon-container');
        $icon.appendTo($iconContainer);
        return $iconContainer;
    };

    const getSelectedDevice = function() {
        var device = { isBrowser: false, isRemote: false, name: undefined };
        var $remoteDevice = $devsPanel.find('.cast-device.selected')
            .filter((i, dev) => !$(dev).data('local') && !$(dev).data('browser')  && $(dev).data('name'));
        var $browserDevice = $devsPanel.find('.cast-device.selected')
            .filter((i, dev) => $(dev).data('browser'));

        if ($remoteDevice.length) {
            device.isRemote = true;
            device.name = $remoteDevice.data('name');
        } else if ($browserDevice.length) {
            device.isBrowser = true;
        }

        return device;
    };

    const startStreamingTorrent = function(torrent) {
        // TODO support for subtitles download on torrent metadata received
        return new Promise((resolve, reject) => {
            execute(
                {
                    type: 'request',
                    action: 'media.webtorrent.play',
                    args: {
                        resource: torrent,
                        download_only: true,
                    }
                },

                (response) => {
                    resolve(response.response.output.url);
                },

                (error) => {
                    reject(error);
                }
            );
        });
    };

    const startStreaming = function(media, subtitles, relativeURIs) {
        if (media.startsWith('magnet:?')) {
            return new Promise((resolve, reject) => {
                startStreamingTorrent(media)
                    .then((url) => { resolve({'url':url}); })
                    .catch((error) => { reject(error); });
            });
        }

        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'PUT',
                url: '/media',
                contentType: 'application/json',
                data: JSON.stringify({
                    'source': media,
                    'subtitles': subtitles,
                })
            }).done((response) => {
                var url = response.url;
                var subs;
                if ('subtitles_url' in response) {
                    subs = response.subtitles_url;
                }

                if (relativeURIs) {
                    url = url.match(/https?:\/\/[^\/]+(\/media\/.*)/)[1];
                    if (subs) {
                        subs = subs.match(/https?:\/\/[^\/]+(\/media\/.*)/)[1];
                    }
                }

                var ret = { 'url': url, 'subtitles': undefined };
                if (subs) {
                    ret.subtitles = subs;
                }

                resolve(ret);
            }).fail((xhr) => {
                reject(xhr.responseText);
            });
        });
    };

    const stopStreaming = function(media_id) {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: 'DELETE',
                url: '/media/' + media_id,
                contentType: 'application/json',
            });
        });
    };

    const getSubtitles = function(resource) {
        return new Promise((resolve, reject) => {
            if (!window.config.media.subtitles) {
                resolve();  // media.subtitles plugin not configured
            }

            run({
                action: 'media.subtitles.get_subtitles',
                args: { 'resource': resource }
            }).then((response) => {
                resolve(response.response.output);
            }).catch((error) => {
                reject(error.message);
            });
        });
    };

    const downloadSubtitles = function(link, mediaResource, vtt=false) {
        return new Promise((resolve, reject) => {
            run({
                action: 'media.subtitles.download',
                args: {
                    'link': link,
                    'media_resource': mediaResource,
                    'convert_to_vtt': vtt,
                }
            }).then((response) => {
                resolve(response.response.output.filename);
            }).catch((error) => {
                reject(error.message);
            });
        });
    };

    const setSubtitles = (filename) => {
        return new Promise((resolve, reject) => {
            run({
                action: 'media.set_subtitles',
                args: { 'filename': filename }
            }).then((response) => {
                resolve(response.response.output);
            }).catch((error) => {
                reject(error.message);
            });
        });
    };

    const playOnChromecast = (resource, device, subtitles) => {
        return new Promise((resolve, reject) => {
            var requestArgs = {
                action: 'media.chromecast.play',
                args: {
                    'chromecast': device,
                },
            };

            startStreaming(resource, subtitles).then((response) => {
                requestArgs.args.resource = response.url;
                // XXX subtitles currently break the Chromecast playback,
                // see https://github.com/balloob/pychromecast/issues/74
                // if (response.subtitles) {
                //     requestArgs.args.subtitles = response.subtitles;
                // }

                return run(requestArgs);
            }).then((response) => {
                if ('subtitles' in requestArgs) {
                    resolve(requestArgs.args.resource, requestArgs.args.subtitles);
                } else {
                    resolve(requestArgs.args.resource);
                }
            }).catch((error) => {
                reject(error);
            });
        });
    };

    const playInBrowser = (resource, subtitles) => {
        return new Promise((resolve, reject) => {
            startStreaming(resource, subtitles, true).then((response) => {
                browserVideoWindow = window.open(
                    response.url + '?webplayer', '_blank');

                browserVideoWindow.addEventListener('load', () => {
                    browserVideoElement = browserVideoWindow.document
                        .querySelector('#video-player');
                });

                resolve(response.url, response.subtitles);
            }).catch((error) => {
                reject(error);
            });
        });
    };

    const playOnServer = (resource, subtitles) => {
        return new Promise((resolve, reject) => {
            var requestArgs = {
                action: 'media.play',
                args: { 'resource': resource },
            };

            if (subtitles) {
                requestArgs.args.subtitles = subtitles;
            }

            run(requestArgs).then((response) => {
                resolve(resource);
            }).catch((error) => {
                reject(error.message);
            });
        });
    };

    const _play = (resource, subtitles) => {
        return new Promise((resolve, reject) => {
            var playHndl;
            var selectedDevice = getSelectedDevice();

            if (selectedDevice.isBrowser) {
                playHndl = playInBrowser(resource, subtitles);
            } else if (selectedDevice.isRemote) {
                playHndl = playOnChromecast(resource, selectedDevice.name, subtitles);
            } else {
                playHndl = playOnServer(resource, subtitles);
            }

            playHndl.then((response) => {
                resolve(resource);
            }).catch((error) => {
                showError('Playback error: ' + (error ? error : 'undefined'));
                reject(error);
            });
        });
    };

    const play = (resource) => {
        return new Promise((resolve, reject) => {
            var results = $videoResults.html();
            var onVideoLoading = () => { $videoResults.text('Loading video...'); };
            var onVideoReady = () => {
                $videoResults.html(results);
                resolve(resource);
            };

            var defaultPlay = () => { _play(resource).finally(onVideoReady); };
            $mediaSearchSubtitles.data('resource', resource);
            onVideoLoading();

            var subtitlesConf = window.config.media.subtitles;

            if (subtitlesConf) {
                populateSubtitlesModal(resource).then((subs) => {
                    if ('language' in subtitlesConf) {
                        if (subs) {
                            downloadSubtitles(subs[0].SubDownloadLink, resource).then((subtitles) => {
                                _play(resource, subtitles).finally(onVideoReady);
                                resolve(resource, subtitles);
                            }).catch((error) => {
                                defaultPlay();
                                resolve(resource);
                            });
                        } else {
                            defaultPlay();
                            resolve(resource);
                        }
                    } else {
                        defaultPlay();
                        resolve(resource);
                    }
                });
            } else {
                defaultPlay();
                resolve(resource);
            }
        });
    };

    const download = function(resource) {
        return new Promise((resolve, reject) => {
            var results = $videoResults.html();
            var onVideoLoading = function() {
                $videoResults.text('Loading video...');
            };

            var onVideoReady = function() {
                $videoResults.html(results);
            };

            onVideoLoading();
            startStreaming(resource, undefined, true)
                .then((response) => {
                    var url = response.url + '?download'
                    window.open(url, '_blank');
                    resolve(url);
                })
                .catch((error) => {
                    reject(error);
                })
                .finally(() => {
                    onVideoReady();
                });
        });
    };

    const populateSubtitlesModal = (resource) => {
        return new Promise((resolve, reject) => {
            $mediaSubtitlesMessage.text('Loading subtitles...');
            $mediaSubtitlesResults.text('');
            $mediaSubtitlesMessage.show();
            $mediaSubtitlesResultsContainer.hide();

            getSubtitles(resource).then((subs) => {
                if (!subs) {
                    $mediaSubtitlesMessage.text('No subtitles found');
                    resolve();
                }

                $mediaSearchSubtitles.show();
                for (var sub of subs) {
                    var flagCode;
                    if ('ISO639' in sub) {
                        switch(sub.ISO639) {
                            case 'en': flagCode = 'gb'; break;
                            default: flagCode = sub.ISO639; break;
                        }
                    }

                    var $subContainer = $('<div></div>').addClass('row media-subtitle-container')
                        .data('download-link', sub.SubDownloadLink)
                        .data('resource', resource);

                    var $subFlagIconContainer = $('<div></div>').addClass('one column');
                    var $subFlagIcon = $('<span></span>')
                        .addClass(flagCode ? 'flag-icon flag-icon-' + flagCode : (
                            sub.IsLocal ? 'fa fa-download' : ''))
                        .text(!(flagCode || sub.IsLocal) ? '?' : '');

                    var $subMovieName = $('<div></div>').addClass('five columns')
                        .text(sub.MovieName);

                    var $subFileName = $('<div></div>').addClass('six columns')
                        .text(sub.SubFileName);

                    $subFlagIcon.appendTo($subFlagIconContainer);
                    $subFlagIconContainer.appendTo($subContainer);
                    $subMovieName.appendTo($subContainer);
                    $subFileName.appendTo($subContainer);
                    $subContainer.appendTo($mediaSubtitlesResults);
                }

                $mediaSubtitlesMessage.hide();
                $mediaSubtitlesResultsContainer.show();
                resolve(subs);
            }).catch((error) => {
                $mediaSubtitlesMessage.text('Unable to load subtitles: ' + error.message);
                reject(error);
            });
        });
    };

    const setBrowserPlayerSubs = (resource, subtitles) => {
        var mediaId;
        if (!browserVideoElement) {
            showError('No video is currently playing in the browser');
            return;
        }

        return new Promise((resolve, reject) => {
            $.get('/media').then((media) => {
                for (var m of media) {
                    if (m.source === resource) {
                        mediaId = m.media_id;
                        break;
                    }
                }

                if (!mediaId) {
                    reject(resource + ' is not a registered media');
                    return;
                }

                return $.ajax({
                    type: 'POST',
                    url: '/media/subtitles/' + mediaId + '.vtt',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        'filename': subtitles,
                    }),
                });
            }).then(() => {
                resolve(resource, subtitles);
            }).catch((error) => {
                reject('Cannot set subtitles for ' + resource + ': ' + error);
            });
        });
    };

    const setLocalPlayerSubs = (resource, subtitles) => {
        return new Promise((resolve, reject) => {
            run({
                action: 'media.remove_subtitles'
            }).then((response) => {
                return setSubtitles(subtitles);
            }).then((response) => {
                resolve(response);
            }).catch((error) => {
                reject(error);
            });
        });
    };

    const initBindings = function() {
        window.registerEventListener(onEvent);
        $searchForm.on('submit', function(event) {
            var $input = $(this).find('input[name=video-search-text]');
            var resource = $input.val();
            var request = {}
            var onSuccess = function() {};
            var onError = function() {};
            var onComplete = function() {
                $input.prop('disabled', false);
            };

            $input.prop('disabled', true);
            $mediaItemPanel.find('[data-action]').removeClass('disabled');
            $videoResults.text('Searching...');

            if (resource.match(new RegExp('^https?://')) ||
                resource.match(new RegExp('^file://'))) {
                var videos = [{ url: resource }];
                updateVideoResults(videos);

                request = {
                    type: 'request',
                    action: 'media.play',
                    args: { resource: resource }
                };
            } else {
                request = {
                    type: 'request',
                    action: 'media.search',
                    args: { query: resource }
                };

                onSuccess = function(response) {
                    var videos = response.response.output;
                    updateVideoResults(videos);
                };
            }

            execute(request, onSuccess, onError, onComplete)
            return false;
        });

        $ctrlForm.on('submit', function() { return false; });
        $ctrlForm.find('button[data-action]').on('click touch', function(evt) {
            var action = $(this).data('action');
            var $btn = $(this);

            var requestArgs = {
                type: 'request',
                action: 'media.' + action,
            };

            var selectedDevice = getSelectedDevice();
            if (selectedDevice.isBrowser) {
                return;  // The in-browser player can be used to control media
            }

            if (selectedDevice.isRemote) {
                requestArgs.action = 'media.chromecast.' + action;
                requestArgs.args = { 'chromecast': selectedDevice.name };
            }

            execute(requestArgs);
        });

        $volumeCtrl.on('mousedown touchstart', function(event) {
            prevVolume = $(this).val();
        });

        $volumeCtrl.on('mouseup touchend', function(event) {
            var requestArgs = {
                type: 'request',
                action: 'media.set_volume',
                args: { volume: $(this).val() },
            };

            var selectedDevice = getSelectedDevice();
            if (selectedDevice.isRemote) {
                requestArgs.action = 'media.chromecast.set_volume',
                requestArgs.args.chromecast = selectedDevice.name;
            }

            execute(requestArgs,
                onSuccess=undefined,
                onError = function() {
                    $volumeCtrl.val(prevVolume);
                }
            );
        });

        $videoResults.on('mousedown touchstart', '.video-result', function() {
            selectedResource = $(this).data('url');
        });

        $videoResults.on('mouseup touchend', '.video-result', function(event) {
            var $item = $(this);
            var resource = $item.data('url');
            if (resource !== selectedResource) {
                return;  // Did not really click this item
            }

            $item.siblings().removeClass('selected');
            $item.addClass('selected');

            $mediaItemPanel.css('top', (event.clientY + $(window).scrollTop()) + 'px');
            $mediaItemPanel.css('left', (event.clientX + $(window).scrollLeft()) + 'px');
            $mediaItemPanel.data('resource', resource);
        });

        $devsBtn.on('click touch', function() {
            $(this).toggleClass('selected');
            $devsPanel.css('top', ($(this).position().top + $(this).outerHeight()) + 'px');
            $devsPanel.css('left', ($(this).position().left) + 'px');
            return false;
        });

        $devsPanel.on('mouseup touchend', '.cast-device', function() {
            if ($(this).hasClass('disabled')) {
                return;
            }

            var $devices = $devsPanel.find('.cast-device');
            var $curSelected = $devices.filter((i, d) => $(d).hasClass('selected'));

            if ($curSelected.data('name') !== $(this).data('name')) {
                $curSelected.removeClass('selected');
                $(this).addClass('selected');
                $devsBtnIcon.attr('class', $(this).find('.fa').attr('class'));

                if ($(this).data('browser') || $(this).data('local')) {
                    $devsBtn.removeClass('remote');
                } else {
                    $devsBtn.addClass('remote');
                }

                // TODO Logic for switching destination on the fly
            }

            $devsPanel.hide();
            $devsBtn.removeClass('selected');
        });

        $devsRefreshBtn.on('click', function() {
            if ($(this).hasClass('disabled')) {
                return;
            }

            $(this).addClass('disabled');
            initRemoteDevices();
        });

        $mediaItemPanel.on('click', '[data-action]', function() {
            var $action = $(this);
            if ($action.hasClass('disabled')) {
                return;
            }

            var action = $action.data('action');
            var resource = $mediaItemPanel.data('resource');
            if (!resource) {
                return;
            }

            $mediaItemPanel.hide();
            $mediaItemPanel.find('[data-action]').addClass('disabled');

            eval(action)($mediaItemPanel.data('resource'))
                .finally(() => {
                    $mediaItemPanel.find('[data-action]').removeClass('disabled');
                });
        });

        $mediaSubtitlesModal.on('mouseup touchend', '.media-subtitle-container', (event) => {
            var resource = $(event.currentTarget).data('resource');
            var link = $(event.currentTarget).data('downloadLink');
            var selectedDevice = getSelectedDevice();

            if (selectedDevice.isRemote) {
                showError('Changing subtitles at runtime on Chromecast is not yet supported');
                return;
            }

            var convertToVTT = selectedDevice.isBrowser;

            downloadSubtitles(link, resource, convertToVTT).then((subtitles) => {
                if (selectedDevice.isBrowser) {
                    return setBrowserPlayerSubs(resource, subtitles);
                } else {
                    return setLocalPlayerSubs(resource, subtitles);
                }
            }).catch((error) => {
                console.warning('Could not load subtitles ' + link +
                    ' to the player: ' + (error || 'undefined error'))
            });
        });
    };

    const initRemoteDevices = function() {
        $devsList.find('.cast-device[data-remote]').addClass('disabled');

        execute(
            {
                type: 'request',
                action: 'media.chromecast.get_chromecasts',
            },

            onSuccess = function(results) {
                $devsList.find('.cast-device[data-remote]').remove();
                $devsRefreshBtn.removeClass('disabled');

                if (!results || results.response.errors.length) {
                    return;
                }

                results = results.response.output;
                for (var cast of results) {
                    var $cast = $('<div></div>').addClass('row cast-device')
                        .addClass('cast-device-' + cast.type).attr('data-remote', true)
                        .data('name', cast.name);

                    var icon = 'question';
                    switch (cast.type) {
                        case 'cast': icon = 'tv'; break;
                        case 'audio': icon = 'volume-up'; break;
                    }

                    var $castIcon = $('<i></i>').addClass('fa fa-' + icon)
                        .addClass('cast-device-icon');
                    var $castName = $('<span></span>').addClass('cast-device-name')
                        .text(cast.name);

                    var $iconContainer = $('<div></div>').addClass('two columns');
                    var $nameContainer = $('<div></div>').addClass('ten columns');
                    $castIcon.appendTo($iconContainer);
                    $castName.appendTo($nameContainer);

                    $iconContainer.appendTo($cast);
                    $nameContainer.appendTo($cast);
                    $cast.appendTo($devsList);
                }
            },

            onComplete = function() {
                $devsRefreshBtn.removeClass('disabled');
            }
        );
    };

    const init = function() {
        initRemoteDevices();
        initBindings();
    };

    init();
});

