$(document).ready(function() {
    var lights,
        groups,
        scenes,
        $roomsList = $('#rooms-list'),
        $lightsList = $('#lights-list'),
        $scenesList = $('#scenes-list');

    var execute = function(request, onSuccess, onError, onComplete) {
        request['target'] = 'localhost';
        return $.ajax({
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

    var createPowerToggleElement = function(data) {
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push light-ctrl-switch-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .attr('id', 'toggle--push').addClass('toggle--checkbox light-ctrl-switch');

        data = data || {};
        for (var attr of Object.keys(data)) {
            $input.data(attr, data[attr]);
        }

        var $label = $('<label></label>').attr('for', 'toggle--push').addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        return $powerToggle;
    };

    var updateRooms = function(rooms) {
        var roomByLight = {};
        var roomsByScene = {};

        $roomsList.html('');
        $lightsList.html('');
        $scenesList.html('');

        for (var room of Object.keys(rooms)) {
            var $room = $('<div></div>')
                .addClass('room-item')
                .data('id', room)
                .text(rooms[room].name);

            var $roomLights = $('<div></div>')
                .addClass('room-lights-item')
                .data('id', room);

            var $roomScenes = $('<div></div>')
                .addClass('room-scenes-item')
                .data('room-id', room)
                .data('room-name', rooms[room].name);

            $room.appendTo($roomsList);
            $roomLights.appendTo($lightsList);
            $roomScenes.appendTo($scenesList);

            for (var light of rooms[room].lights) {
                var $light = $('<div></div>')
                    .addClass('light-item')
                    .data('id', light)
                    .text(lights[light].name);

                var $powerToggle = createPowerToggleElement({
                    type: 'light',
                    id: light,
                });

                roomByLight[light] = room;
                $powerToggle.appendTo($light);
                $light.appendTo($roomLights);
            }
        }

        for (var scene of Object.keys(scenes)) {
            roomsByScene[scene] = new Set();
            for (var light of scenes[scene].lights) {
                var room = roomByLight[light];
                if (roomsByScene[scene].has(room)) {
                    continue;
                }

                roomsByScene[scene].add(room);

                var $roomScenes = $scenesList.find('.room-scenes-item')
                    .filter(function(i, item) {
                        return $(item).data('room-id') === room
                    });

                var $scene = $('<div></div>')
                    .addClass('scene-item')
                    .data('id', scene)
                    .data('name', scenes[scene].name)
                    .text(scenes[scene].name);

                $scene.appendTo($roomScenes);
            }
        }
    };

    var refreshStatus = function() {
        $.when(
            execute({ type: 'request', action: 'light.hue.get_lights' }),
            execute({ type: 'request', action: 'light.hue.get_groups' }),
            execute({ type: 'request', action: 'light.hue.get_scenes' })
        ).done(function(l, g, s) {
            lights = l[0].response.output;
            groups = g[0].response.output;
            scenes = s[0].response.output;

            for (var group of Object.keys(groups)) {
                if (groups[group].type.toLowerCase() !== 'room') {
                    delete groups[group];
                }
            }

            updateRooms(groups);
        });
    };

    var initBindings = function() {
        $roomsList.on('click touch', '.room-item', function() {
            $('.room-item').removeClass('selected');
            $('.room-lights-item').hide();
            $('.room-scenes-item').hide();

            var roomId = $(this).data('id');
            var $roomLights = $('.room-lights-item').filter(function(i, item) {
                return $(item).data('id') === roomId
            });

            var $roomScenes = $('.room-scenes-item').filter(function(i, item) {
                return $(item).data('room-id') === roomId
            });

            $(this).addClass('selected');
            $roomLights.show();
            $roomScenes.show();
        });

        $scenesList.on('click touch', '.scene-item', function() {
            $('.scene-item').removeClass('selected');
            $(this).addClass('selected');

            execute({
                type: 'request',
                action: 'light.hue.scene',
                args: {
                    name: $(this).data('name')
                }
            });
        });
    };

    var init = function() {
        refreshStatus();
        initBindings();
    };

    init();
});

