$(document).ready(function() {
    var seekInterval,
        longPressTimeout,
        curPath = [],
        curTrackUpdateHandler,
        curTrackElapsed = {
            timestamp: null,
            elapsed: null,
        };

    var execute = function(request, onSuccess, onError, onComplete) {
        request['target'] = 'localhost';
        $.ajax({
            type: 'POST',
            url: '/execute',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(request),
            complete: function() {
                if (onComplete) {
                    onComplete();
                }
            },
            error: function(xhr, status, error) {
                if (onError) {
                    onError(xhr, status, error);
                }
            },
            success: function(response, status, xhr) {
                if (onSuccess) {
                    onSuccess(response, status, xhr);
                }
            },
            beforeSend: function(xhr) {
                if (window.token) {
                    xhr.setRequestHeader('X-Token', window.token);
                }
            },
        });
    };

    var updateControls = function(status, track) {
        var $playbackControls = $('.playback-controls');
        var $playlistContent = $('#playlist-content');
        var $curTrack = $('.track-info');
        var $volumeCtrl = $('#volume-ctrl');
        var $trackSeeker = $('#track-seeker');
        var $randomBtn = $playbackControls.find('[data-action=random]');
        var $repeatBtn = $playbackControls.find('[data-action=repeat]');
        var elapsed; var length;

        if (status) {
            if (seekInterval) {
                clearInterval(seekInterval);
            }

            if ('time' in status) {
                var time = status.time.split(':');
                elapsed = parseInt(parseInt(time[0])/60) + ':'
                    + (parseInt(time[0])%60 < 10 ? '0' : '') + (parseInt(time[0])%60);

                if (time.length > 1) {
                    length = parseInt(parseInt(time[1])/60) + ':'
                        + (parseInt(time[1])%60 < 10 ? '0' : '') + (parseInt(time[1])%60);
                }

                $trackSeeker.val(parseInt(time[0]));
                $trackSeeker.attr('max', parseInt(time[1]));
                curTrackElapsed = {
                    timestamp: new Date().getTime(),
                    elapsed: parseInt(time[0]),
                };
            }

            switch (status.state.toLowerCase()) {
                case 'stop':
                    $playbackControls.find('button[data-action=pause]').hide();
                    $playbackControls.find('button[data-action=play]').show();
                    $curTrack.find('.artist').hide();
                    $curTrack.find('.track').hide();
                    $curTrack.find('.no-track').show();

                    $trackSeeker.attr('disabled', true);
                    $('.seek-time').text('-:--');
                    break;

                case 'pause':
                    $playbackControls.find('button[data-action=pause]').hide();
                    $playbackControls.find('button[data-action=play]').show();
                    $curTrack.find('.artist').show();
                    $curTrack.find('.track').show();
                    $curTrack.find('.no-track').hide();

                    $trackSeeker.removeAttr('disabled');
                    $('#seek-time-elapsed').text(elapsed ? elapsed : '-:--');
                    $('#seek-time-length').text(length ? length : '-:--');
                    break;

                case 'play':
                    $playbackControls.find('button[data-action=pause]').show();
                    $playbackControls.find('button[data-action=play]').hide();
                    $curTrack.find('.artist').show();
                    $curTrack.find('.track').show();
                    $curTrack.find('.no-track').hide();

                    $trackSeeker.removeAttr('disabled');
                    $('#seek-time-elapsed').text(elapsed ? elapsed : '-:--');
                    $('#seek-time-length').text(length ? length : '-:--');

                    seekInterval = setInterval(function() {
                        var length = parseInt($trackSeeker.attr('max'));
                        var value = parseInt((new Date().getTime() - curTrackElapsed.timestamp)/1000)
                            + curTrackElapsed.elapsed;

                        if (value < length) {
                            $trackSeeker.val(value);
                            elapsed = parseInt(value/60) + ':' + (value%60 < 10 ? '0' : '') + (value%60);
                            $('#seek-time-elapsed').text(elapsed);
                        }
                    }, 1000);
                    break;
            }

            $volumeCtrl.val(parseInt(status.volume));

            var repeat = parseInt(status.repeat);
            if (repeat) {
                $repeatBtn.addClass('enabled');
            } else {
                $repeatBtn.removeClass('enabled');
            }

            var random = parseInt(status.random);
            if (random) {
                $randomBtn.addClass('enabled');
            } else {
                $randomBtn.removeClass('enabled');
            }
        }

        if (track) {
            $curTrack.find('.artist').text(track.artist);
            $curTrack.find('.track').text(track.title);

            var updatePlayingTrack = function(track) {
                return function() {
                    var $curTrack = $playlistContent.find('.playlist-track').filter(
                        function() { return $(this).data('pos') == track.pos });

                    if ($curTrack.length === 0) {
                        return;
                    }

                    var offset = $curTrack.offset().top
                        - $playlistContent.offset().top
                        + $playlistContent.scrollTop() - 10;

                    $playlistContent.find('.playlist-track').removeClass('active');
                    $curTrack.addClass('active');
                    $playlistContent.animate({ scrollTop: offset }, 500)
                };
            };

            if ($playlistContent.find('.playlist-track').length === 0) {
                // Playlist viewer hasn't loaded yet
                curTrackUpdateHandler = updatePlayingTrack(track);
            } else {
                updatePlayingTrack(track)();
            }
        }
    };

    var onEvent = function(event) {
        switch (event.args.type) {
            case 'platypush.message.event.music.MusicStopEvent':
            case 'platypush.message.event.music.MusicPlayEvent':
            case 'platypush.message.event.music.MusicPauseEvent':
            case 'platypush.message.event.music.NewPlayingTrackEvent':
                updateControls(status=event.args.status, track=event.args.track);
                break;

            case 'platypush.message.event.music.PlaylistChangeEvent':
                updatePlaylist(tracks=event.args.changes);
                break;
        }

        console.log(event);
    };

    var initStatus = function() {
        execute(
            {
                type: 'request',
                action: 'music.mpd.status',
            },

            onSuccess = function(response) {
                updateControls(status=response.response.output);
            }
        );

        execute(
            {
                type: 'request',
                action: 'music.mpd.currentsong',
            },

            onSuccess = function(response) {
                updateControls(status=undefined, track=response.response.output);
            }
        );
    };

    var onTrackTouchDown = function(event) {
        var $track = $(this);
        longPressTimeout = setTimeout(function() {
            $track.addClass('selected');
            clearTimeout(longPressTimeout);
            longPressTimeout = undefined;
        }, 1000);
    };

    var onTrackTouchUp = function(event) {
        var $track = $(this);
        if (longPressTimeout) {
            execute({
                type: 'request',
                action: 'music.mpd.playid',
                args: { track_id: $track.data('track-id') }
            });
        }

        clearTimeout(longPressTimeout);
        longPressTimeout = undefined;
    };

    var updatePlaylist = function(tracks) {
        var $playlistContent = $('#playlist-content');
        $playlistContent.find('.playlist-track').remove();

        for (var track of tracks) {
            var $element = $('<div></div>')
                .addClass('playlist-track')
                .addClass('row').addClass('music-item')
                .data('name', (track.artist || '') + ' ' + (track.title || ''))
                .data('track-id', parseInt(track.id))
                .data('pos', parseInt(track.pos))
                .data('file', track.file);

            var $artist = $('<div></div>')
                .addClass('four').addClass('columns')
                .addClass('track-artist').text(track.artist);

            var $title = $('<div></div>')
                .addClass('six').addClass('columns')
                .addClass('track-title').text(track.title);

            var $time = $('<div></div>')
                .addClass('two').addClass('columns')
                .addClass('track-time').text(
                    '' + parseInt(parseInt(track.time)/60) +
                    ':' + (parseInt(track.time)%60 < 10 ? '0' : '') +
                    parseInt(track.time)%60);

            $artist.appendTo($element);
            $title.appendTo($element);
            $time.appendTo($element);

            $element.on('mousedown touchstart', onTrackTouchDown);
            $element.on('mouseup touchend', onTrackTouchUp);
            $element.appendTo($playlistContent);
        }

        if (curTrackUpdateHandler) {
            curTrackUpdateHandler();
            curTrackUpdateHandler = undefined;
        }
    }

    var initPlaylist = function() {
        execute(
            {
                type: 'request',
                action: 'music.mpd.playlistinfo',
            },

            onSuccess = function(response) {
                updatePlaylist(response.response.output);
            }
        );
    };

    var onPlaylistTouchDown = function(event) {
        var $playlist = $(this);
        $playlist.addClass('selected');

        longPressTimeout = setTimeout(function() {
            clearTimeout(longPressTimeout);
            longPressTimeout = undefined;
        }, 1000);
    };

    var onPlaylistTouchUp = function(event) {
        var $playlist = $(this);
        if (longPressTimeout) {
            execute(
                {
                    type: 'request',
                    action: 'music.mpd.clear'
                },

                onSuccess = function() {
                    execute(
                        {
                            type: 'request',
                            action: 'music.mpd.load',
                            args: { playlist: $playlist.data('name') }
                        }
                    );
                }
            );
        }

        clearTimeout(longPressTimeout);
        longPressTimeout = undefined;
    };

    var onFileTouchDown = function(event) {
        var $file = $(this);
        $file.addClass('selected');

        longPressTimeout = setTimeout(function() {
            clearTimeout(longPressTimeout);
            longPressTimeout = undefined;
        }, 1000);
    };

    var onFileTouchUp = function(event) {
        var $file = $(this);
        if (longPressTimeout) {
            execute(
                {
                    type: 'request',
                    action: 'music.mpd.playlistinfo'
                },

                onSuccess = function(response) {
                    var pos = 0;
                    if (response.response.output.length > 0) {
                        pos = parseInt(response.response.output.slice(-1)[0].pos) + 1;
                    }

                    execute(
                        {
                            type: 'request',
                            action: 'music.mpd.add',
                            args: { resource: $file.data('file') }
                        },

                        onSuccess = function() {
                            execute(
                                {
                                    type: 'request',
                                    action: 'music.mpd.play_pos',
                                    args: { pos: pos }
                                }
                            );
                        }
                    )
                }
            );

            $file.removeClass('selected');
        }

        clearTimeout(longPressTimeout);
        longPressTimeout = undefined;
    };

    var onDirectorySelect = function(event) {
        var $directory = $(this);
        execute(
            {
                type: 'request',
                action: 'music.mpd.lsinfo',
                args: { uri: $directory.data('name') }
            },

            onSuccess = function(response) {
                curPath = $directory.data('name').split('/')
                    .filter(function(term) { return term.length > 0 });

                updateBrowser(response.response.output);
            }
        );
    };

    var updateBrowser = function(items) {
        var $browserContent = $('#music-browser');
        var $browserFilter = $('#browser-filter');
        var $addButton = $('#browser-controls').find('button[data-action="add"]');
        var directories = [];
        var playlists = [];
        var files = [];

        $browserContent.find('.music-item').remove();
        $browserFilter.text('');

        for (var item of items) {
            if ('directory' in item) {
                directories.push(item.directory);
            } else if ('playlist' in item) {
                playlists.push(item.playlist);
            } else if ('file' in item) {
                files.push(item);
            }
        }

        if (curPath.length > 0) {
            var $parentElement = $('<div></div>')
                .addClass('browser-directory').addClass('music-item')
                .addClass('browser-item').addClass('row').data('name', curPath.slice(0, -1).join('/'))
                .html('<i class="fa fa-folder-open-o"></i> &nbsp; ..');

            $parentElement.on('click touch', onDirectorySelect);
            $parentElement.appendTo($browserContent);
            $addButton.removeAttr('disabled');
        } else {
            $addButton.attr('disabled', 'disabled');
        }

        for (var directory of directories.sort()) {
            var $element = $('<div></div>')
                .addClass('browser-directory').addClass('music-item')
                .addClass('browser-item').addClass('row').data('name', directory)
                .html('<i class="fa fa-folder-open-o"></i> &nbsp; ' + directory.split('/').slice(-1)[0]);

            $element.on('click touch', onDirectorySelect);
            $element.appendTo($browserContent);
        }

        for (var playlist of playlists.sort()) {
            var $element = $('<div></div>')
                .addClass('browser-playlist').addClass('music-item')
                .addClass('browser-item').addClass('row').data('name', playlist)
                .html('<i class="fa fa-list"></i> &nbsp; ' + playlist);

            $element.on('mousedown touchstart', onPlaylistTouchDown);
            $element.on('mouseup touchend', onPlaylistTouchUp);
            $element.appendTo($browserContent);
        }

        files = files.sort(function(a, b) {
            if (a.artist === b.artist) {
                if (a.album === b.album) {
                    return parseInt(a.track) < parseInt(b.track) ? -1 : 1;
                } else {
                    return a.album.localeCompare(b.album);
                }
            } else {
                return a.artist.localeCompare(b.artist);
            }
        });

        for (var file of files) {
            var $element = $('<div></div>')
                .addClass('browser-file').addClass('music-item')
                .addClass('browser-item').addClass('row')
                .html('<i class="fa fa-music"></i> &nbsp; ' + file.title);

            for (var prop of Object.keys(file)) {
                $element.data(prop, file[prop]);
            }

            $element.on('mousedown touchstart', onFileTouchDown);
            $element.on('mouseup touchend', onFileTouchUp);
            $element.appendTo($browserContent);
        }
    };

    var initBrowser = function() {
        execute(
            {
                type: 'request',
                action: 'music.mpd.lsinfo',
            },

            onSuccess = function(response) {
                updateBrowser(response.response.output);
            }
        );
    };

    var initBindings = function() {
        window.registerEventListener(onEvent);
        var $playbackControls = $('.playback-controls, #playlist-controls').find('button');
        var $playlistContent = $('#playlist-content');
        var $playlistFilter = $('#playlist-filter');
        var $browserContent = $('#music-browser');
        var $browserFilter = $('#browser-filter');
        var $browserAddBtn = $('#browser-controls').find('button[data-action="add"]');
        var $volumeCtrl = $('#volume-ctrl');
        var $trackSeeker = $('#track-seeker');
        var prevVolume;

        $playbackControls.on('click', function(evt) {
            var action = $(this).data('action');
            var $btn = $(this);
            $btn.attr('disabled', true);

            execute(
                {
                    type: 'request',
                    action: 'music.mpd.' + action,
                },

                onSuccess = function(response) {
                    updateControls(status=response.response.output);
                },

                onError=undefined,
                onComplete = function() {
                    $btn.removeAttr('disabled');
                }
            );
        });

        $volumeCtrl.on('mousedown', function(event) {
            prevVolume = $(this).val();
        });

        $volumeCtrl.on('mouseup', function(event) {
            execute(
                {
                    type: 'request',
                    action: 'music.mpd.setvol',
                    args: { vol: $(this).val() }
                },

                onSuccess=undefined,
                onError = function() {
                    $volumeCtrl.val(prevVolume);
                }
            );
        });

        $volumeCtrl.on('mouseup', function(event) {
            execute(
                {
                    type: 'request',
                    action: 'music.mpd.setvol',
                    args: { vol: $(this).val() }
                },

                onSuccess=undefined,
                onError = function() {
                    $volumeCtrl.val(prevVolume);
                }
            );
        });

        $trackSeeker.on('mouseup', function(event) {
            execute(
                {
                    type: 'request',
                    action: 'music.mpd.seekcur',
                    args: { value: $(this).val() }
                },

                onSuccess = function(response) {
                    var elapsed = parseInt(response.response.output.time.split(':')[0]);
                    curTrackElapsed.elapsed = elapsed;
                }
            );
        });

        $browserAddBtn.on('click touch', function(event) {
            var $items = $browserContent.find('.music-item').slice(1, -1);
            var $selectedItems = $browserContent.find('.music-item.selected');

            if ($selectedItems.length == 0) {
                $selectedItems = $items;
            }

            for (var item of $selectedItems) {
                execute(
                    {
                        type: 'request',
                        action: 'music.mpd.add',
                        args: { resource: $(item).data('file') }
                    }
                );
            }
        });

        $browserFilter.on('keyup', function(event) {
            var filterText = $(this).val().trim().toLowerCase();
            var $browserItems = $browserContent.find('.browser-item');
            $browserItems.hide();

            var matchedItems = $.grep($browserItems, function(item) {
                return $(item).data('name').toLowerCase().indexOf(filterText) >= 0;
            });

            $(matchedItems).show();
        });

        $playlistFilter.on('keyup', function(event) {
            var filterText = $(this).val().trim().toLowerCase();
            var $playlistItems = $playlistContent.find('.playlist-track');
            $playlistItems.hide();

            var matchedItems = $.grep($playlistItems, function(item) {
                return $(item).data('name').toLowerCase().indexOf(filterText) >= 0;
            });

            $(matchedItems).show();
        });
    };

    var init = function() {
        initStatus();
        initPlaylist();
        initBrowser();
        initBindings();
    };

    init();
});

