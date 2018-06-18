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
            .attr('id', id).addClass('toggle--checkbox');

        if (type === 'animation') {
            $input.addClass('animation-switch');
        } else {
            $input.addClass('light-ctrl-switch');
        }

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
        } else if (type === 'room' || type === 'animation') {
            element = groups[data.id];
        } else {
            throw "Unknown type: " + type;
        }

        var $colorSelector = $('<div></div>')
            .addClass('light-color-selector');

        if (type === 'animation') {
            // Animation type selector
            var $typeContainer = $('<div></div>')
                .addClass('animation-type-container').addClass('row');

            var $typeText = $('<div></div>').addClass('two columns').text('Type');

            // Color transition type
            var $transitionTypeContainer = $('<div></div>').addClass('five columns');

            var $transitionType = $('<input></input>').addClass('animation-type')
                .addClass('one column').data('type', 'color_transition')
                .attr('id', 'hue-animation-color-transition').data('name', element.name)
                .attr('type', 'radio').attr('name', 'animation-type');

            var $transitionTypeLabel = $('<label></label>').attr('for', 'hue-animation-color-transition')
                .addClass('four columns').text('Color transition');

            $typeText.appendTo($typeContainer);

            $transitionType.appendTo($transitionTypeContainer);
            $transitionTypeLabel.appendTo($transitionTypeContainer);
            $transitionTypeContainer.appendTo($typeContainer);

            // Blink type
            var $blinkTypeContainer = $('<div></div>').addClass('five columns');

            var $blinkType = $('<input></input>').addClass('animation-type')
                .addClass('one column').data('type', 'blink')
                .attr('id', 'hue-animation-blink').data('name', element.name)
                .attr('type', 'radio').attr('name', 'animation-type');

            var $blinkTypeLabel = $('<label></label>').attr('for', 'hue-animation-blink')
                .addClass('four columns').text('Blink');

            $blinkType.appendTo($blinkTypeContainer);
            $blinkTypeLabel.appendTo($blinkTypeContainer);
            $blinkTypeContainer.appendTo($typeContainer);

            $typeContainer.appendTo($colorSelector);

            // Color transition container
            var $animationContainer = $('<div></div>')
                .addClass('animation-container row').data('animation-type', 'color_transition');

            // Hue slider
            var $hueContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var defaultHueRange = [0, 65535];
            var $hueText = $('<div></div>').addClass('two columns').text('Hue range');
            var $hueSlider = $('<div></div>')
                .addClass('ten columns').data('animation-property', 'hue_range')
                .data('id', data.id).val(defaultHueRange).slider({
                    range: true,
                    min: 0,
                    max: 65535,
                    values: defaultHueRange,
                    slide: function(event, ui) {
                        var values = $(event.target).slider("option", "values");
                        $(this).val(values);
                    }
                });

            $hueText.appendTo($hueContainer);
            $hueSlider.appendTo($hueContainer);
            $hueContainer.appendTo($animationContainer);

            // Sat slider
            var $satContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var defaultSatRange = [155, 255];
            var $satText = $('<div></div>').addClass('two columns').text('Sat range');
            var $satSlider = $('<div></div>')
                .addClass('ten columns').data('animation-property', 'sat_range')
                .data('id', data.id).val(defaultSatRange).slider({
                    range: true,
                    min: 0,
                    max: 255,
                    values: defaultSatRange,
                    slide: function(event, ui) {
                        var values = $(event.target).slider("option", "values");
                        $(this).val(values);
                    }
                });

            $satText.appendTo($satContainer);
            $satSlider.appendTo($satContainer);
            $satContainer.appendTo($animationContainer);

            // Bri slider
            var $briContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var defaultBriRange = [240, 255];
            var $briText = $('<div></div>').addClass('two columns').text('Bri range');
            var $briSlider = $('<div></div>')
                .addClass('ten columns').data('animation-property', 'bri_range')
                .data('id', data.id).val(defaultBriRange).slider({
                    range: true,
                    min: 0,
                    max: 255,
                    values: defaultBriRange,
                    slide: function(event, ui) {
                        var values = $(event.target).slider("option", "values");
                        $(this).val(values);
                    }
                });

            $briText.appendTo($briContainer);
            $briSlider.appendTo($briContainer);
            $briContainer.appendTo($animationContainer);

            // Hue step
            var $hueStepContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var $hueStepText = $('<div></div>').addClass('two columns').text('Hue step');
            var $hueStepSlider = $('<input></input>').addClass('slider light-slider')
                .addClass('ten columns').addClass('hue').data('animation-property', 'hue_step')
                .attr('type', 'range').attr('min', 0).attr('max', 65535)
                .data('id', data.id).data('name', element.name).val(1000);

            $hueStepText.appendTo($hueStepContainer);
            $hueStepSlider.appendTo($hueStepContainer);
            $hueStepContainer.appendTo($animationContainer);

            // Sat step
            var $satStepContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var $satStepText = $('<div></div>').addClass('two columns').text('Sat step');
            var $satStepSlider = $('<input></input>').addClass('slider light-slider')
                .addClass('ten columns').addClass('sat').data('animation-property', 'sat_step')
                .attr('type', 'range').attr('min', 0).attr('max', 255)
                .data('id', data.id).data('name', element.name).val(2);

            $satStepText.appendTo($satStepContainer);
            $satStepSlider.appendTo($satStepContainer);
            $satStepContainer.appendTo($animationContainer);

            // Bri step
            var $briStepContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var $briStepText = $('<div></div>').addClass('two columns').text('Bri step');
            var $briStepSlider = $('<input></input>').addClass('slider light-slider')
                .addClass('ten columns').addClass('bri').data('animation-property', 'bri_step')
                .attr('type', 'range').attr('min', 0).attr('max', 255)
                .data('id', data.id).data('name', element.name).val(1);

            $briStepText.appendTo($briStepContainer);
            $briStepSlider.appendTo($briStepContainer);
            $briStepContainer.appendTo($animationContainer);

            // Transition seconds
            var $transitionContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var $transitionText = $('<div></div>').addClass('two columns').text('Transition seconds');
            var $transitionInput = $('<input></input>').data('animation-property', 'transition_seconds')
                .addClass('two columns pull-right').attr('type', 'text')
                .data('id', data.id).data('name', element.name).val(1);

            $transitionText.appendTo($transitionContainer);
            $transitionInput.appendTo($transitionContainer);
            $transitionContainer.appendTo($animationContainer);

            // Duration seconds
            var $durationContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            var $durationText = $('<div></div>').addClass('two columns').text('Duration seconds');
            var $durationInput = $('<input></input>').data('animation-property', 'duration')
                .addClass('two columns pull-right').attr('type', 'text')
                .data('id', data.id).data('name', element.name);

            $durationText.appendTo($durationContainer);
            $durationInput.appendTo($durationContainer);
            $durationContainer.appendTo($animationContainer);

            $animationContainer.appendTo($colorSelector);

            // Blink animation container
            $animationContainer = $('<div></div>')
                .addClass('animation-container row').data('animation-type', 'blink');

            // Transition seconds
            $transitionContainer = $('<div></div>')
                .addClass('slider-container').addClass('row');

            $transitionText = $('<div></div>').addClass('two columns').text('Transition seconds');
            $transitionInput = $('<input></input>').data('animation-property', 'transition_seconds')
                .addClass('two columns pull-right').attr('type', 'text')
                .data('id', data.id).data('name', element.name).val(1);

            $transitionText.appendTo($transitionContainer);
            $transitionInput.appendTo($transitionContainer);
            $transitionContainer.appendTo($animationContainer);

            // Duration seconds
            $durationContainer = $('<div></div>').data('animation-property', 'duration')
                .addClass('slider-container').addClass('row');

            $durationText = $('<div></div>').addClass('two columns').text('Duration seconds');
            $durationInput = $('<input></input>').data('animation-property', 'duration')
                .addClass('two columns pull-right').attr('type', 'text')
                .data('id', data.id).data('name', element.name);

            $durationText.appendTo($durationContainer);
            $durationInput.appendTo($durationContainer);
            $durationContainer.appendTo($animationContainer);

            $animationContainer.appendTo($colorSelector);
        } else {
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
        }

        return $colorSelector;
    };

    var createLightCtrlElement = function(type, id) {
        var element;

        if (type === 'light') {
            element = lights[id];
        } else if (type === 'room' || type === 'animation') {
            element = groups[id];
        } else {
            throw "Unknown type: " + type;
        }

        var on;
        if (type === 'light') {
            on = element.state.on;
        } else if (type === 'room') {
            on = element.state.any_on;
        } else {
            on = false;
        }

        var $light = $('<div></div>')
            .addClass('light-item')
            .data('type', type)
            .data('id', id)
            .data('name', element.name)
            .data('on', on);

        if (type === 'room') {
            $light.addClass('all-lights-item');
        } else if (type === 'animation') {
            $light.addClass('animation-item');
        }

        var $row1 = $('<div></div>').addClass('row');
        var $row2 = $('<div></div>').addClass('row');

        var lightName;
        switch(type) {
            case 'light': lightName = element.name; break;
            case 'room': lightName = 'All Lights'; break;
            case 'animation': lightName = 'Animate'; break;
        }

        var $lightName = $('<div></div>')
            .addClass('light-item-name')
            .text(lightName);

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

            var $animation = createLightCtrlElement(type='animation', id=room);
            $animation.prependTo($roomLights);

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

        $lightsList.on('click touch', '.animation-switch', function(e) {
            e.stopPropagation();

            var turnedOn = $(this).prop('checked');
            var args = {};
            args['groups'] = $(this).parents('.animation-item').data('name');
            args['animation'] = $(this).parents('.animation-item')
                .find('input.animation-type:checked').data('type');

            var $animationCtrl = $(this).parents('.animation-item')
                .find('.animation-container').filter(
                    (index, node) => $(node).data('animation-type') === args['animation']
                );

            var params = $animationCtrl.find('*').filter(
                (index, node) => $(node).data('animation-property'))
            .toArray().reduce(
                (map, input) => {
                    if ($(input).val().length) {
                        var val = $(input).val();
                        val = Array.isArray(val) ? val.map((i) => parseFloat(i)) : parseFloat(val);
                        map[$(input).data('animation-property')] = val;
                    }

                    return map
                }, {}
            );

            for (var p of Object.keys(params)) {
                args[p] = params[p];
            }

            if (turnedOn) {
                execute(
                    {
                        type: 'request',
                        action: 'light.hue.animate',
                        args: args,
                    },

                    onSuccess = function() {
                        $(this).prop('checked', true);
                    }
                );
            } else {
                execute(
                    {
                        type: 'request',
                        action: 'light.hue.stop_animation',
                    },

                    onSuccess = function() {
                        $(this).prop('checked', false);
                    }
                );
            }
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

        $lightsList.on('click touch', 'input.animation-type', function(e) {
            var type = $(this).data('type');
            var $animationContainers = $(this).parents('.animation-item').find('.animation-container')
            var $animationContainer = $(this).parents('.animation-item').find('.animation-container')
                .filter(function() { return $(this).data('animationType') === type })

            $animationContainers.hide();
            $animationContainer.show();
        });
    };

    var init = function() {
        initUi();
        initBindings();
    };

    init();
});

