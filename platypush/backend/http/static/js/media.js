$(document).ready(function() {
    var $container = $('#video-container'),
        $searchForm = $('#video-search'),
        $videoResults = $('#video-results'),
        $volumeCtrl = $('#video-volume-ctrl'),
        $ctrlForm = $('#video-ctrl'),
        $devsPanel = $('#media-devices-panel'),
        $devsBtn = $('button[data-toggle="#media-devices-panel"]'),
        $searchBarContainer = $('#media-search-bar-container'),
        $mediaBtnsContainer = $('#media-btns-container'),
        prevVolume = undefined;

    var updateVideoResults = function(videos) {
        $videoResults.html('');
        for (var video of videos) {
            var $videoResult = $('<div></div>')
                .addClass('video-result')
                .attr('data-url', video['url'])
                .html('title' in video ? video['title'] : video['url']);

            var $icon = getVideoIconByUrl(video['url']);
            $icon.prependTo($videoResult);
            $videoResult.appendTo($videoResults);
        }
    };

    var getVideoIconByUrl = function(url) {
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

    var getSelectedDevice = function() {
        var device = { isRemote: false, name: undefined };
        var $remoteDevice = $devsPanel.find('.cast-device.selected')
            .filter((i, dev) => !$(dev).data('local') && $(dev).data('name'));

        if ($remoteDevice.length) {
            device.isRemote = true;
            device.name = $remoteDevice.data('name');
        }

        return device;
    };

    var initBindings = function() {
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

        $videoResults.on('click touch', '.video-result', function(evt) {
            var results = $videoResults.html();
            var $item = $(this);
            if (!$item.hasClass('selected')) {
                $item.siblings().removeClass('selected');
                $item.addClass('selected');
                return false;
            }

            var requestArgs = {
                type: 'request',
                action: 'media.play',
                args: { resource: $item.data('url') },
            };

            var selectedDevice = getSelectedDevice();
            if (selectedDevice.isRemote) {
                requestArgs.action = 'media.chromecast.play';
                requestArgs.args.chromecast = selectedDevice.name;
            }

            $videoResults.text('Loading video...');
            execute(
                requestArgs,
                function() {
                    $videoResults.html(results);
                    $item.siblings().removeClass('active');
                    $item.addClass('active');
                },

                function() {
                    $videoResults.html(results);
                }
            );
        });

        $devsBtn.on('click touch', function() {
            $(this).toggleClass('selected');
            $devsPanel.css('top', ($(this).position().top + $(this).outerHeight()) + 'px');
            $devsPanel.css('left', ($(this).position().left) + 'px');
            $devsPanel.toggle();
            return false;
        });

        $devsPanel.on('mouseup touchend', '.cast-device', function() {
            var $devices = $devsPanel.find('.cast-device');
            var $curSelected = $devices.filter((i, d) => $(d).hasClass('selected'));

            if ($curSelected.data('name') !== $(this).data('name')) {
                $curSelected.removeClass('selected');
                $(this).addClass('selected');

                if (!$(this).data('local')) {
                    $devsBtn.addClass('remote');
                } else {
                    $devsBtn.removeClass('remote');
                }
            }

            $devsPanel.hide();
            $devsBtn.removeClass('selected');
        });
    };

    var initRemoteDevices = function() {
        execute(
            {
                type: 'request',
                action: 'media.chromecast.get_chromecasts',
            },

            function(results) {
                if (!results || results.response.errors.length) {
                    return;
                }

                $searchBarContainer.removeClass('eleven').addClass('nine');
                $mediaBtnsContainer.removeClass('one').addClass('three');
                $devsBtn.show();

                results = results.response.output;
                for (var cast of results) {
                    var $cast = $('<div></div>').addClass('row cast-device')
                        .addClass('cast-device-' + cast.type).data('name', cast.name);

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
                    $cast.appendTo($devsPanel);
                }
            }
        );
    };

    var init = function() {
        initRemoteDevices();
        initBindings();
    };

    init();
});

