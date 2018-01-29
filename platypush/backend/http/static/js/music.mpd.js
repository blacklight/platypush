$(document).ready(function() {
    var execute = function(request, onSuccess, onComplete) {
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
        var $curTrack = $('.track-info');

        if (status) {
            switch (status.state.toLowerCase()) {
                case 'stop':
                    $playbackControls.find('button[data-action=pause]').hide();
                    $playbackControls.find('button[data-action=play]').show();
                    $curTrack.find('.artist').hide();
                    $curTrack.find('.track').hide();
                    $curTrack.find('.no-track').show();
                    break;
                case 'pause':
                    $playbackControls.find('button[data-action=pause]').hide();
                    $playbackControls.find('button[data-action=play]').show();
                    $curTrack.find('.artist').show();
                    $curTrack.find('.track').show();
                    $curTrack.find('.no-track').hide();
                    break;
                case 'play':
                    $playbackControls.find('button[data-action=pause]').show();
                    $playbackControls.find('button[data-action=play]').hide();
                    $curTrack.find('.artist').show();
                    $curTrack.find('.track').show();
                    $curTrack.find('.no-track').hide();
                    break;
            }
        }

        if (track) {
            $curTrack.find('.artist').text(track.artist);
            $curTrack.find('.track').text(track.title);
        }
    };

    var onEvent = function(event) {
        if (
                event.args.type === 'platypush.message.event.music.MusicStopEvent' ||
                event.args.type === 'platypush.message.event.music.MusicPlayEvent' ||
                event.args.type === 'platypush.message.event.music.MusicPauseEvent' ||
                event.args.type === 'platypush.message.event.music.NewPlayingTrackEvent') {
            updateControls(status=event.args.status, track=event.args.track);
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

    var initPlaylist = function() {
        execute(
            {
                type: 'request',
                action: 'music.mpd.playlistinfo',
            },

            onSuccess = function(response) {
                var $playlistContent = $('#playlist-content');
                var tracks = response.response.output;

                for (var track of tracks) {
                    var $element = $('<div></div>')
                        .addClass('playlist-track')
                        .addClass('row').addClass('music-item')
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
                    $element.appendTo($playlistContent);
                }
            }
        );
    };

    var initBrowser = function() {
        execute(
            {
                type: 'request',
                action: 'music.mpd.lsinfo',
            },

            onSuccess = function(response) {
                var $browserContent = $('#music-browser');
                var items = response.response.output;
                var directories = [];
                var playlists = [];

                for (var item of items) {
                    if ('directory' in item) {
                        directories.push(item.directory);
                    } else if ('playlist' in item) {
                        playlists.push(item.playlist);
                    }
                }

                for (var directory of directories.sort()) {
                    var $element = $('<div></div>')
                        .addClass('browser-directory').addClass('music-item')
                        .addClass('browser-item').addClass('row')
                        .html('<i class="fa fa-folder-open-o"></i> &nbsp; ' + directory);

                    $element.appendTo($browserContent);
                }

                for (var playlist of playlists.sort()) {
                    var $element = $('<div></div>')
                        .addClass('browser-playlist').addClass('music-item')
                        .addClass('browser-item').addClass('row')
                        .html('<i class="fa fa-music"></i> &nbsp; ' + playlist);

                    $element.appendTo($browserContent);
                }
            }
        );
    };

    var initBindings = function() {
        window.registerEventListener(onEvent);
        var $playbackControls = $('.playback-controls').find('button');

        $playbackControls.on('click', function(evt) {
            var action = $(this).data('action');
            var $btn = $(this);
            $btn.attr('disabled', true);

            execute(
                {
                    type: 'request',
                    action: 'music.mpd.' + action,
                },

                onSuccess=undefined,
                onComplete = function() {
                    $btn.removeAttr('disabled');
                }
            );
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

