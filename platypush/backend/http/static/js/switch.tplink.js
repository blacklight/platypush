$(document).ready(function() {
    var switches,
        $tplinkContainer = $('#tplink-container');

    var createPowerToggleElement = function(dev) {
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push switch-ctrl-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .data('name', dev.host).attr('name', dev.alias).addClass('toggle--checkbox switch-ctrl');

        var $label = $('<label></label>').attr('for', dev.alias).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if (dev.on) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var updateDevices = function(devices) {
        for (var dev of devices) {
            var $dev = $('<div></div>').addClass('row tplink-device').data('name', dev.alias);
            var $devName = $('<div></div>').addClass('ten columns name').text(dev.alias);
            var $toggleContainer = $('<div></div>').addClass('two columns toggle-container');
            var $toggle = createPowerToggleElement(dev);

            $toggle.appendTo($toggleContainer);
            $devName.appendTo($dev);
            $toggleContainer.appendTo($dev);
            $dev.appendTo($tplinkContainer);
        }
    };

    var initWidget = function() {
        execute(
            {
                type: 'request',
                action: 'switch.tplink.status'
            },

            onSuccess = function(response) {
                updateDevices(Object.values(response.response.output.devices));
            }
        );
    };

    var initBindings = function() {
        $tplinkContainer.on('click touch', '.switch-ctrl-container', function() {
            var $input = $(this).find('.switch-ctrl');
            var devAddr = $input.data('name');
            var action = $input.prop('checked') ? 'off' : 'on';

            execute(
                {
                    type: 'request',
                    action: 'switch.tplink.' + action,
                    args: { device: devAddr }
                },

                onSuccess = function(response) {
                    var status = response.response.output.status;
                    $input.prop('checked', status == 'on' ? true : false);
                }
            );
        });
    };

    var init = function() {
        initWidget();
        initBindings();
    };

    init();
});

