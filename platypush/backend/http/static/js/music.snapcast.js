$(document).ready(function() {
    var serverInfo = {},
        clientInfo = {},
        serverStreams = {},
        groupStreams = {},
        $container = $('#snapcast-container');

    var createPowerToggleElement = function(data) {
        data = data || {};

        var inputId = data.id + '_' + parseInt(Math.random()*100000);
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push switch-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .attr('id', inputId).data('id', data.id).addClass('toggle--checkbox');

        for (var attr of Object.keys(data)) {
            $input.data(attr, data[attr]);
        }

        var $label = $('<label></label>').attr('for', inputId).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if ('on' in data && data['on']) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var onEvent = function(event) {
        switch (event.args.type) {
            case 'platypush.message.event.music.snapcast.ClientConnectedEvent':
            case 'platypush.message.event.music.snapcast.ClientDisconnectedEvent':
            case 'platypush.message.event.music.snapcast.ClientNameChangeEvent':
            case 'platypush.message.event.music.snapcast.GroupStreamChangeEvent':
            case 'platypush.message.event.music.snapcast.ServerUpdateEvent':
                redraw();
                break;

            case 'platypush.message.event.music.snapcast.ClientVolumeChangeEvent':
                var $host = $($container.find('.snapcast-host-container').filter(
                    (i, hostDiv) => $(hostDiv).data('host') === event.args.host
                ));

                var $client = $($host.find('.snapcast-client-container').filter(
                    (i, clientDiv) => $(clientDiv).data('id') === event.args.client
                ));

                $client.find('.snapcast-volume-slider').val(event.args.volume);
                $client.find('.snapcast-mute-toggle').find('input.toggle--checkbox')
                    .prop('checked', !event.args.muted);

                break;

            case 'platypush.message.event.music.snapcast.GroupMuteChangeEvent':
                var $host = $($container.find('.snapcast-host-container').filter(
                    (i, hostDiv) => $(hostDiv).data('host') === event.args.host
                ));

                var $group = $($host.find('.snapcast-group-container').filter(
                    (i, groupDiv) => $(groupDiv).data('id') === event.args.group
                ));

                $group.find('.snapcast-group-mute-toggle').find('input.toggle--checkbox')
                    .prop('checked', !event.args.muted);

                break;
        }
    };

    var update = function(statuses) {
        $container.html('');
        serverInfo = {};
        clientInfo = {};
        serverStreams = {};
        groupStreams = {};

        var hosts = Object.keys(window.config.snapcast_hosts);

        for (var i=0; i < hosts.length; i++) {
            var status = statuses[i];
            var host = hosts[i];
            var name = status.server.host.name || status.server.host.ip;

            serverStreams[host] = status.streams;
            serverInfo[host] = status.server.host;
            serverInfo[host].serverName = status.server.snapserver.serverName;
            serverInfo[host].version = status.server.snapserver.version;
            serverInfo[host].protocolVersion = status.server.snapserver.protocolVersion;
            serverInfo[host].controlProtocolVersion = status.server.snapserver.controlProtocolVersion;

            var $host = $('<div></div>')
                .addClass('snapcast-host-container')
                .addClass('snapcast-settings-btn')
                .attr('data-modal', '#snapcast-host-modal')
                .data('name', name)
                .data('host', host);

            var $hostHeader = $('<div></div>').addClass('row')
                .addClass('snapcast-host-header');

            var $hostTitle = $('<h1></h1>')
                .addClass('snapcast-host-settings')
                .addClass('snapcast-settings-btn')
                .attr('data-modal', '#snapcast-host-modal');

            var $hostSettings = $('<i></i>')
                .attr('data-modal', '#snapcast-host-modal')
                .addClass('fa fa-ellipsis-v');

            var $hostName = $('<span></span>')
                .attr('data-modal', '#snapcast-host-modal')
                .html('&nbsp; ' + name);

            $hostSettings.appendTo($hostTitle);
            $hostName.appendTo($hostTitle);
            $hostTitle.appendTo($hostHeader);
            $hostHeader.appendTo($host);

            for (var group of status.groups) {
                var groupName = group.name || group.stream_id;
                groupStreams[group.id] = group.stream_id;

                var $group = $('<div></div>')
                    .addClass('snapcast-group-container')
                    .data('name', groupName)
                    .data('id', group.id);

                var $groupHeader = $('<div></div>').addClass('row')
                    .addClass('snapcast-group-header');

                var $groupTitle = $('<h2></h2>')
                    .addClass('snapcast-group-settings')
                    .addClass('snapcast-settings-btn')
                    .attr('data-modal', '#snapcast-group-modal')
                    .addClass('eleven columns');

                var $groupSettings = $('<i></i>')
                    .attr('data-modal', '#snapcast-group-modal')
                    .addClass('fa fa-ellipsis-v');

                var $groupName = $('<span></span>')
                    .attr('data-modal', '#snapcast-group-modal')
                    .html('&nbsp; ' + groupName);

                var $groupMuteToggle = createPowerToggleElement({
                    id: group.id,
                    on: !group.muted,
                }).addClass('one column')
                    .addClass('snapcast-mute-toggle')
                    .addClass('snapcast-group-mute-toggle');

                $groupSettings.appendTo($groupTitle);
                $groupName.appendTo($groupTitle);
                $groupTitle.appendTo($groupHeader);
                $groupMuteToggle.appendTo($groupHeader);
                $groupHeader.appendTo($group);

                for (var client of group.clients) {
                    var clientName = client.config.name || client.host.name || client.host.ip;
                    clientInfo[client.id] = client.host;
                    clientInfo[client.id].clientName = client.snapclient.name;
                    clientInfo[client.id].clientVersion = client.snapclient.version;
                    clientInfo[client.id].protocolVersion = client.snapclient.protocolVersion;

                    var $client = $('<div></div>')
                        .addClass('snapcast-client-container')
                        .data('name', clientName)
                        .data('id', client.id)
                        .data('connected', client.connected);

                    if (!client.connected) {
                        $client.addClass('snapcast-client-disconnected');
                    }

                    var $clientRow = $('<div></div>').addClass('row')
                        .addClass('snapcast-client-row');

                    var $clientTitle = $('<h3></h3>')
                        .addClass('snapcast-settings-btn')
                        .addClass('snapcast-client-settings')
                        .attr('data-modal', '#snapcast-client-modal')
                        .addClass('two columns');

                    var $clientSettings = $('<i></i>')
                        .attr('data-modal', '#snapcast-client-modal')
                        .addClass('fa fa-ellipsis-v');

                    var $clientName = $('<span></span>')
                        .attr('data-modal', '#snapcast-client-modal')
                        .html('&nbsp; ' + clientName);

                    var $volumeSlider = $('<input></input>')
                        .addClass('slider snapcast-volume-slider')
                        .addClass('nine columns')
                        .data('id', client.id)
                        .attr('type', 'range')
                        .attr('min', 0).attr('max', 100)
                        .val(client.config.volume.percent);

                    var $clientMuteToggle = createPowerToggleElement({
                        id: client.id,
                        on: !client.config.volume.muted,
                    })
                        .addClass('one column')
                        .addClass('snapcast-mute-toggle')
                        .addClass('snapcast-client-mute-toggle');

                    $clientSettings.appendTo($clientTitle);
                    $clientName.appendTo($clientTitle);
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
        execute(
            {
                type: 'request',
                action: 'music.snapcast.get_backend_hosts',
            },

            (response) => {
                window.config = window.config || {};
                window.config.snapcast_hosts = response.response.output;
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
                    var statuses = [];
                    for (var status of arguments) {
                        statuses.push(status[0].response.output);
                    }

                    update(statuses);
                }).then(function() {
                    initBindings();
                });
            }
        );
    };

    var initBindings = function() {
        $container.on('click touch', '.toggle--checkbox', function(evt) {
            evt.stopPropagation();
            var id = $(this).data('id');
            var host = $(this).parents('.snapcast-host-container').data('host');
            var args = {
                host: host,
                port: window.config.snapcast_hosts[host],
                mute: !$(this).prop('checked'),
            };

            if ($(this).parents('.snapcast-mute-toggle').hasClass('snapcast-client-mute-toggle')) {
                args.client = id;
            } else if ($(this).parents('.snapcast-mute-toggle').hasClass('snapcast-group-mute-toggle')) {
                args.group = id;
            } else {
                return;
            }

            execute({
                type: 'request',
                action: 'music.snapcast.mute',
                args: args,
            });
        });

        $container.on('mouseup touchend', '.snapcast-volume-slider', function(evt) {
            evt.stopPropagation();
            var id = $(this).data('id');
            var host = $(this).parents('.snapcast-host-container').data('host');
            var args = {
                host: host,
                port: window.config.snapcast_hosts[host],
                client: id,
                volume: $(this).val(),
            };

            execute({
                type: 'request',
                action: 'music.snapcast.volume',
                args: args,
            });
        });

        $container.on('click touch', '.snapcast-host-settings', function(evt) {
            var host = $(this).parents('.snapcast-host-container').data('host');
            var hostName = $(this).parents('.snapcast-host-container').data('name');
            var $modal = $($(this).data('modal'));

            $modal.find('.modal-header').text(hostName);

            var info = serverInfo[host];
            var $form = $modal.find('#snapcast-host-form');
            var $info = $form.find('.snapcast-host-info');

            for (var attr in info) {
                $info.find('[data-bind=' + attr + ']').text(info[attr]);
            }
        });

        $container.on('click touch', '.snapcast-group-settings', function(evt) {
            var host = $(this).parents('.snapcast-host-container').data('host');
            var groupId = $(this).parents('.snapcast-group-container').data('id');
            var groupName = $(this).parents('.snapcast-group-container').data('name');
            var $modal = $($(this).data('modal'));
            var $form = $modal.find('#snapcast-group-form');
            var $clients = $(this).parents('.snapcast-host-container')
                .find('.snapcast-client-container');

            var groupClients = $(this).parents('.snapcast-group-container')
                .find('.snapcast-client-container')
                .map((i, client) => $(client).data('id'));

            var $clientsList = $modal.find('.snapcast-group-clients');
            $clientsList.html('');
            $form.data('host', host);
            $form.data('group', groupId);
            $modal.find('.modal-header').text(groupName);

            for (var client of $clients) {
                var $row = $('<div></div>').addClass('row');
                var $input = $('<input></input>').attr('type', 'checkbox')
                    .attr('name', $(client).data('id'))
                    .prop('checked', $.inArray($(client).data('id'), groupClients) >= 0);
                var $label = $('<label></label>')
                    .attr('for', $(client).data('id'))
                    .text($(client).data('name'));

                $input.appendTo($row);
                $label.appendTo($row);
                $row.appendTo($clientsList);
            }

            var $streams = $form.find('.snapcast-group-stream').find('select[name=stream]');
            $streams.html('');

            for (var stream of serverStreams[host]) {
                var $option = $('<option></option>').val(stream.id)
                    .text(stream.id);

                if (stream.id === groupStreams[groupId]) {
                    $option.prop('selected', true);
                }

                $option.appendTo($streams);
            }

            $form.find('.snapcast-group-stream')
                .find('select[name=stream]').html($streams.html());
        });

        $container.on('click touch', '.snapcast-client-settings', function(evt) {
            var host = $(this).parents('.snapcast-host-container').data('host');
            var clientId = $(this).parents('.snapcast-client-container').data('id');
            var clientName = $(this).parents('.snapcast-client-container').data('name');
            var info = clientInfo[clientId];
            var $modal = $($(this).data('modal'));
            var $form = $modal.find('#snapcast-client-form');
            var $info = $form.find('.snapcast-client-info');

            $form.data('host', host);
            $form.data('client', clientId);
            $modal.find('.modal-header').text(clientName);
            $form.find('input[name=name]').val(clientName);

            for (var attr in info) {
                $info.find('[data-bind=' + attr + ']').text(info[attr]);
            }
        });

        $('.snapcast-form').on('click touch', '[data-dismiss-modal]', function(evt) {
            var $modal = $(this).parents($(this).data('dismiss-modal'));

            var clearModal = function() {
                $modal.find('form').find('input').prop('disabled', false);
                $modal.find('form').find('[name=delete]').prop('checked', false);
            };

            clearModal();
        });

        $('#snapcast-client-form').on('submit', function(evt) {
            var $form = $(this);
            var host = $form.data('host');
            var clientId = $form.data('client');

            var clearModal = function() {
                $form.parents('.modal').fadeOut();
                $form.find('input').prop('disabled', false);
                $form.find('[name=delete]').prop('checked', false);
            };

            var request = {
                type: 'request',
                args: {
                    host: host,
                    port: window.config.snapcast_hosts[host],
                    client: clientId,
                },
            };

            if ($form.find('[name=delete]').prop('checked')) {
                if (!confirm('Are you sure you want to remove this client?')) {
                    return false;
                }

                request.action = 'music.snapcast.delete_client';
            } else {
                request.action = 'music.snapcast.set_client_name';
                request.args.name = $form.find('input[name=name]').val().trim();
            }

            $form.find('input').prop('disabled', true);

            execute(
                request,
                (response) => {},
                (xhr, status, error) => {
                    createNotification({
                        'icon': 'exclamation',
                        'text': status + ': ' + error,
                    });
                },
                () => {
                    clearModal();
                }
            );

            return false;
        });

        $('#snapcast-group-form').on('submit', function(evt) {
            var $form = $(this);
            var $modal = $form.parents('.modal');
            var $clientsList = $form.find('.snapcast-group-clients');
            var $clients = $clientsList.find('input[type=checkbox]:checked');
            var host = $form.data('host');
            var groupId = $form.data('group');
            var clients = [];

            for (var c of $clients) {
                clients.push($(c).attr('name'));
            }

            var streamId = $form.find('.snapcast-group-stream')
                .find('select[name=stream]').val();

            var promises = [
                execute({
                    type: 'request',
                    action: 'music.snapcast.group_set_clients',
                    args: {
                        host: host,
                        port: window.config.snapcast_hosts[host],
                        group: groupId,
                        clients: clients,
                    }
                }),
                execute({
                    type: 'request',
                    action: 'music.snapcast.group_set_stream',
                    args: {
                        host: host,
                        port: window.config.snapcast_hosts[host],
                        group: groupId,
                        stream_id: streamId,
                    }
                }),
            ];

            $.when.apply($, promises)
            .fail(
                (xhr, status, error) => {
                    createNotification({
                        'icon': 'exclamation',
                        'text': status + ': ' + error,
                    });
                }
            ).always(
                () => {
                    $form.find('input').prop('disabled', false);
                    $modal.fadeOut();
                }
            );

            $form.find('input').prop('disabled', true);
            return false;
        });
    };

    var initEvents = function() {
        window.registerEventListener(onEvent);
    };

    var init = function() {
        redraw();
        initEvents();
    };

    init();
});

