$(document).ready(function() {
    var switches,
        $wemoContainer = $('#wemo-container');

    var createPowerToggleElement = function(dev) {
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push switch-ctrl-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .attr('name', dev.name).addClass('toggle--checkbox switch-ctrl');

        var $label = $('<label></label>').attr('for', id).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if (dev.state == 1) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var updateDevices = function(devices) {
        for (var dev of devices) {
            var $dev = $('<div></div>').addClass('row wemo-device').data('name', dev.name);
            var $devName = $('<div></div>').addClass('ten columns name').text(dev.name);
            var $toggleContainer = $('<div></div>').addClass('two columns toggle-container');
            var $toggle = createPowerToggleElement(dev);

            $toggle.appendTo($toggleContainer);
            $devName.appendTo($dev);
            $toggleContainer.appendTo($dev);
            $dev.appendTo($wemoContainer);
        }
    };

    var initWidget = function() {
        execute(
            {
                type: 'request',
                action: 'switch.wemo.get_devices'
            },

            onSuccess = function(response) {
                updateDevices(response.response.output.devices);
            }
        );
    };

    var initBindings = function() {
        $wemoContainer.on('click touch', '.switch-ctrl-container', function() {
            var $input = $(this).find('.switch-ctrl');
            var devName = $input.attr('name');

            execute(
                {
                    type: 'request',
                    action: 'switch.wemo.toggle',
                    args: {
                        device: devName
                    }
                },

                onSuccess = function(response) {
                    var state = response.response.output.state;
                    $input.prop('checked', !!state);
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

