$(document).ready(function() {
    var $container = $('#video-container'),
        $searchForm = $('#video-search'),
        $videoResults = $('#video-results'),
        $volumeCtrl = $('#video-volume-ctrl'),
        $ctrlForm = $('#video-ctrl'),
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
                    action: 'video.omxplayer.play',
                    args: { resource: resource }
                };
            } else {
                request = {
                    type: 'request',
                    action: 'video.omxplayer.search',
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

            execute(
                {
                    type: 'request',
                    action: 'video.omxplayer.' + action,
                }
            );
        });

        $volumeCtrl.on('mousedown touchstart', function(event) {
            prevVolume = $(this).val();
        });

        $volumeCtrl.on('mouseup touchend', function(event) {
            execute(
                {
                    type: 'request',
                    action: 'video.omxplayer.set_volume',
                    args: { volume: $(this).val() }
                },

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

            $videoResults.text('Loading video...');
            execute(
                {
                    type: 'request',
                    action: 'video.omxplayer.play',
                    args: { resource: $item.data('url') },
                },

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
    };

    var init = function() {
        initBindings();
    };

    init();
});

