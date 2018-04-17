$(document).ready(function() {
    var lights,
        groups,
        scenes,
        $roomsList = $('#rooms-list'),
        $lightsList = $('#lights-list'),
        $scenesList = $('#scenes-list');

    var createPowerToggleElement = function(data) {
        var id = data['type'] + '_' + data['id'];
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push light-ctrl-switch-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .attr('id', id).addClass('toggle--checkbox light-ctrl-switch');

        data = data || {};
        for (var attr of Object.keys(data)) {
            $input.data(attr, data[attr]);
        }

        var $label = $('<label></label>').attr('for', id).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if ('on' in data && data['on']) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var createColorSelector = function(data) {
        var type = data.type;
        var element;

        if (type === 'light') {
            element = lights[data.id];
        } else if (type === 'room') {
            element = groups[data.id];
        } else {
            throw "Unknown type: " + type;
        }

        var $colorSelector = $('<div></div>')
            .addClass('light-color-selector');

        // Hue slider
        var $hueContainer = $('<div></div>')
            .addClass('slider-container').addClass('row');

        var $hueText = $('<div></div>').addClass('two columns').text('Hue');
        var $hueSlider = $('<input></input>').addClass('slider light-slider')
            .addClass('ten columns').addClass('hue').data('type', type)
            .attr('type', 'range').attr('min', 0).attr('max', 65535).data('property', 'hue')
            .data('id', data.id).data('name', element.name).val(type === 'light' ? element.state.hue : 0);

        $hueText.appendTo($hueContainer);
        $hueSlider.appendTo($hueContainer);
        $hueContainer.appendTo($colorSelector);

        // Saturation slider
        var $satContainer = $('<div></div>')
            .addClass('slider-container').addClass('row');

        var $satText = $('<div></div>').addClass('two columns').text('Saturation');
        var $satSlider = $('<input></input>').addClass('slider light-slider')
            .addClass('ten columns').addClass('sat').data('type', type)
            .attr('type', 'range').attr('min', 0).attr('max', 255).data('property', 'sat')
            .data('id', data.id).data('name', element.name).val(type === 'light' ? element.state.sat : 0);

        $satText.appendTo($satContainer);
        $satSlider.appendTo($satContainer);
        $satContainer.appendTo($colorSelector);

        // Brightness slider
        var $briContainer = $('<div></div>')
            .addClass('slider-container').addClass('row');

        var $briText = $('<div></div>').addClass('two columns').text('Brightness');
        var $briSlider = $('<input></input>').addClass('slider light-slider')
            .addClass('ten columns').addClass('bri').data('type', type)
            .attr('type', 'range').attr('min', 0).attr('max', 255).data('property', 'bri')
            .data('id', data.id).data('name', element.name).val(type === 'light' ? element.state.bri : 0);

        $briText.appendTo($briContainer);
        $briSlider.appendTo($briContainer);
        $briContainer.appendTo($colorSelector);

        return $colorSelector;
    };

    var createLightCtrlElement = function(type, id) {
        var element;

        if (type === 'light') {
            element = lights[id];
        } else if (type === 'room') {
            element = groups[id];
        } else {
            throw "Unknown type: " + type;
        }

        var on = type === 'light' ? element.state.on : element.state.any_on;
        var $light = $('<div></div>')
            .addClass('light-item')
            .data('type', type)
            .data('id', id)
            .data('name', element.name)
            .data('on', on);

        if (type === 'room') {
            $light.addClass('all-lights-item');
        }

        var $row1 = $('<div></div>').addClass('row');
        var $row2 = $('<div></div>').addClass('row');

        var $lightName = $('<div></div>')
            .addClass('light-item-name')
            .text(type === 'light' ? element.name : 'All Lights');

        var $powerToggle = createPowerToggleElement({
            type: type,
            id: id,
            on: on,
        });

        var $colorSelector = createColorSelector({
            type: type,
            id: id,
        });

        $lightName.appendTo($row1);
        $powerToggle.appendTo($row1);
        $colorSelector.appendTo($row2);

        $row1.appendTo($light);
        $row2.appendTo($light);

        return $light;
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
                var $light = createLightCtrlElement(type='light', id=light);
                $light.appendTo($roomLights);
                roomByLight[light] = room;
            }

            roomByLight[light] = room;

            var $allLights = createLightCtrlElement(type='room', id=room);
            $allLights.prependTo($roomLights);
        }

        for (var scene of Object.keys(scenes)) {
            if (scenes[scene].name.match(/(on|off) \d+$/)) {
                // Old 1.0 scenes are saved as "scene_name on <timestamp>" but aren't visible
                // not settable through the app - ignore them
                continue;
            }

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

    var initUi = function() {
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

    var refreshStatus = function() {
        var onResponse = function(data) {
            var response = data.response.output;
            for (var light of Object.keys(response)) {
                var $element = $('.light-item').filter(function(i, item) {
                    return $(item).data('type') === 'light' && $(item).data('id') === light
                });

                $element.find('input.light-ctrl-switch').prop('checked', response[light].state.on);
                $element.find('input.hue').val(response[light].state.hue);
                $element.find('input.sat').val(response[light].state.sat);
                $element.find('input.bri').val(response[light].state.bri);
            }
        };

        execute({ type: 'request', action: 'light.hue.get_lights' }, onResponse);
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
            }, refreshStatus);
        });

        $lightsList.on('click touch', '.light-item-name', function() {
            var $lightItem = $(this).parents('.light-item');
            var $colorSelector = $lightItem.find('.light-color-selector');

            $('.light-color-selector').hide();
            $colorSelector.toggle();

            $('.light-item').removeClass('selected');
            $lightItem.addClass('selected');
        });

        $lightsList.on('click touch', '.light-ctrl-switch', function(e) {
            e.stopPropagation();

            var $lightItem = $($(this).parents('.light-item'));
            var type = $lightItem.data('type');
            var name = $lightItem.data('name');
            var isOn = $lightItem.data('on');
            var action = 'light.hue.' + (isOn ? 'off' : 'on');
            var key = (type == 'light' ? 'lights' : 'groups');
            var args = {
                type: 'request',
                action: action,
                args: {}
            };

            args['args'][key] = [name];
            execute(args, function() {
                $lightItem.data('on', !isOn);
                refreshStatus();
            });
        });

        $lightsList.on('mouseup touchend', '.light-slider', function() {
            var property = $(this).data('property');
            var type = $(this).data('type');
            var name = $(this).data('name');
            var args = {
                type: 'request',
                action: 'light.hue.' + property,
                args: { value: $(this).val() }
            };

            if (type === 'light') {
                args.args.lights = [name];
            } else {
                args.args.groups = [name];
            }

            execute(args, refreshStatus);
        });
    };

    var init = function() {
        initUi();
        initBindings();
    };

    init();
});

