$(document).ready(function() {
    var statuses = [],
        $container = $('#snapcast-container');

    var createPowerToggleElement = function(data) {
        data = data || {};

        var $powerToggle = $('<div></div>').addClass('toggle toggle--push switch-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .attr('id', data.id).addClass('toggle--checkbox');

        for (var attr of Object.keys(data)) {
            $input.data(attr, data[attr]);
        }

        var $label = $('<label></label>').attr('for', data.id).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if ('on' in data && data['on']) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var update = function(statuses) {
        $container.html('');

        var networkNames = Object.keys(window.config.snapcast_hosts);
        for (var i=0; i < networkNames.length; i++) {
            var status = statuses[i];
            var networkName = networkNames[i];
            var name = status.server.host.name || status.server.host.ip;

            var $host = $('<div></div>')
                .addClass('snapcast-host-container')
                .data('name', name)
                .data('network-name', networkName);

            var $header = $('<div></div>').addClass('row')
                .addClass('snapcast-host-header');

            var $title = $('<h1></h1>').text(name);

            $title.appendTo($header);
            $header.appendTo($host);

            for (var group of status.groups) {
                var groupName = group.name || group.stream_id;
                var $group = $('<div></div>')
                    .addClass('snapcast-group-container')
                    .data('name', groupName)
                    .data('id', group.id);

                var $groupHeader = $('<div></div>').addClass('row')
                    .addClass('snapcast-group-header');

                var $groupTitle = $('<h2></h2>')
                    .addClass('ten columns');

                var $groupSettings = $('<i></i>')
                    .addClass('snapcast-group-settings')
                    .addClass('fa fa-cog')
                    .data('name', groupName)
                    .data('id', group.id);

                var $groupName = $('<span></span>')
                    .html('&nbsp; ' + groupName);

                var $groupMuteToggle = createPowerToggleElement({
                    id: group.id,
                    on: !group.muted,
                }).addClass('two columns').addClass('snapcast-group-mute-toggle');

                $groupSettings.appendTo($groupTitle);
                $groupName.appendTo($groupTitle);
                $groupTitle.appendTo($groupHeader);
                $groupMuteToggle.appendTo($groupHeader);
                $groupHeader.appendTo($group);

                for (var client of group.clients) {
                    var clientName = client.config.name || client.host.name || client.host.ip;
                    var $client = $('<div></div>')
                        .addClass('snapcast-client-container')
                        .data('name', clientName)
                        .data('id', client.id);

                    var $clientRow = $('<div></div>').addClass('row')
                        .addClass('snapcast-client-header');

                    var $clientTitle = $('<h3></h3>')
                        .addClass('three columns')
                        .data('connected', client.connected)
                        .text(clientName);

                    var $volumeSlider = $('<input></input>')
                        .addClass('slider snapcast-volume-slider')
                        .addClass('eight columns')
                        .data('id', client.id)
                        .attr('type', 'range')
                        .attr('min', 0).attr('max', 100)
                        .val(client.config.volume.percent);

                    var $clientMuteToggle = createPowerToggleElement({
                        id: client.id,
                        on: !client.config.volume.muted,
                    })
                        .addClass('one column')
                        .addClass('snapcast-client-mute-toggle');

                    $clientTitle.appendTo($clientRow);
                    $volumeSlider.appendTo($clientRow);
                    $clientMuteToggle.appendTo($clientRow);
                    $clientRow.appendTo($client);
                    $client.appendTo($group);
                }

                $group.appendTo($host);
            }

            $host.appendTo($container);
        }
    };

    var redraw = function() {
        var promises = [];

        for (var host of Object.keys(window.config.snapcast_hosts)) {
            promises.push(
                execute({
                    type: 'request',
                    action: 'music.snapcast.status',
                    args: {
                        host: host,
                        port: window.config.snapcast_hosts[host],
                    }
                })
            );
        }

        $.when.apply($, promises)
        .done(function() {
            statuses = [];
            for (var status of arguments) {
                statuses.push(status[0].response.output);
            }

            update(statuses);
        }).then(function() {
            initBindings();
        });
    };

    var initBindings = function() {
        // $roomsList.on('click touch', '.room-item', function() {
        //     $('.room-item').removeClass('selected');
        //     $('.room-lights-item').hide();
        //     $('.room-scenes-item').hide();

        //     var roomId = $(this).data('id');
        //     var $roomLights = $('.room-lights-item').filter(function(i, item) {
        //         return $(item).data('id') === roomId
        //     });

        //     var $roomScenes = $('.room-scenes-item').filter(function(i, item) {
        //         return $(item).data('room-id') === roomId
        //     });

        //     $(this).addClass('selected');
        //     $roomLights.show();
        //     $roomScenes.show();
        // });

        // $scenesList.on('click touch', '.scene-item', function() {
        //     $('.scene-item').removeClass('selected');
        //     $(this).addClass('selected');

        //     execute({
        //         type: 'request',
        //         action: 'light.hue.scene',
        //         args: {
        //             name: $(this).data('name')
        //         }
        //     }, refreshStatus);
        // });

        // $lightsList.on('click touch', '.light-item-name', function() {
        //     var $lightItem = $(this).parents('.light-item');
        //     var $colorSelector = $lightItem.find('.light-color-selector');

        //     $('.light-color-selector').hide();
        //     $colorSelector.toggle();

        //     $('.light-item').removeClass('selected');
        //     $lightItem.addClass('selected');
        // });

        // $lightsList.on('click touch', '.light-ctrl-switch', function(e) {
        //     e.stopPropagation();

        //     var $lightItem = $($(this).parents('.light-item'));
        //     var type = $lightItem.data('type');
        //     var name = $lightItem.data('name');
        //     var isOn = $lightItem.data('on');
        //     var action = 'light.hue.' + (isOn ? 'off' : 'on');
        //     var key = (type == 'light' ? 'lights' : 'groups');
        //     var args = {
        //         type: 'request',
        //         action: action,
        //         args: {}
        //     };

        //     args['args'][key] = [name];
        //     execute(args, function() {
        //         $lightItem.data('on', !isOn);
        //         refreshStatus();
        //     });
        // });

        // $lightsList.on('click touch', '.animation-switch', function(e) {
        //     e.stopPropagation();

        //     var turnedOn = $(this).prop('checked');
        //     var args = {};
        //     args['groups'] = $(this).parents('.animation-item').data('name');
        //     args['animation'] = $(this).parents('.animation-item')
        //         .find('input.animation-type:checked').data('type');

        //     var $animationCtrl = $(this).parents('.animation-item')
        //         .find('.animation-container').filter(
        //             (index, node) => $(node).data('animation-type') === args['animation']
        //         );

        //     var params = $animationCtrl.find('*').filter(
        //         (index, node) => $(node).data('animation-property'))
        //     .toArray().reduce(
        //         (map, input) => {
        //             if ($(input).val().length) {
        //                 var val = $(input).val();
        //                 val = Array.isArray(val) ? val.map((i) => parseFloat(i)) : parseFloat(val);
        //                 map[$(input).data('animation-property')] = val;
        //             }

        //             return map
        //         }, {}
        //     );

        //     for (var p of Object.keys(params)) {
        //         args[p] = params[p];
        //     }

        //     if (turnedOn) {
        //         execute(
        //             {
        //                 type: 'request',
        //                 action: 'light.hue.animate',
        //                 args: args,
        //             },

        //             onSuccess = function() {
        //                 $(this).prop('checked', true);
        //             }
        //         );
        //     } else {
        //         execute(
        //             {
        //                 type: 'request',
        //                 action: 'light.hue.stop_animation',
        //             },

        //             onSuccess = function() {
        //                 $(this).prop('checked', false);
        //             }
        //         );
        //     }
        // });

        // $lightsList.on('mouseup touchend', '.light-slider', function() {
        //     var property = $(this).data('property');
        //     var type = $(this).data('type');
        //     var name = $(this).data('name');
        //     var args = {
        //         type: 'request',
        //         action: 'light.hue.' + property,
        //         args: { value: $(this).val() }
        //     };

        //     if (type === 'light') {
        //         args.args.lights = [name];
        //     } else {
        //         args.args.groups = [name];
        //     }

        //     execute(args, refreshStatus);
        // });

        // $lightsList.on('click touch', 'input.animation-type', function(e) {
        //     var type = $(this).data('type');
        //     var $animationContainers = $(this).parents('.animation-item').find('.animation-container')
        //     var $animationContainer = $(this).parents('.animation-item').find('.animation-container')
        //         .filter(function() { return $(this).data('animationType') === type })

        //     $animationContainers.hide();
        //     $animationContainer.show();
        // });

        // if (window.config.light.hue.default_group) {
        //     var $defaultRoomItem = $roomsList.find('.room-item').filter(
        //         (i, r) => $(r).data('name') == window.config.light.hue.default_group);

        //     $defaultRoomItem.click();
        // }
    };

    var init = function() {
        redraw();
    };

    init();
});

