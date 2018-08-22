$(document).ready(function() {
    var $container = $('#sensors-container');

    var createPowerToggleElement = function(pin) {
        var $powerToggle = $('<div></div>').addClass('toggle toggle--push pin-ctrl-container');
        var $input = $('<input></input>').attr('type', 'checkbox')
            .data('number', pin.pin).attr('name', pin.name).addClass('toggle--checkbox pin-ctrl');

        var $label = $('<label></label>').attr('for', pin.name).addClass('toggle--btn');

        $input.appendTo($powerToggle);
        $label.appendTo($powerToggle);

        if (pin.value > 0) {
            $input.prop('checked', true);
        }

        return $powerToggle;
    };

    var initElements = function() {
        execute({ type: 'request', action: 'gpio.read_all' }, function(data) {
            var response = data.response.output;

            for (var pin of response) {
                var $pin = $('<div></div>')
                    .addClass('row gpio-pin')
                    .attr('data-pin-number', pin.pin);

                var $name = $('<div></div>')
                    .addClass('pin-name ten columns')
                    .text(pin.name);

                var $value = $('<div></div>')
                    .addClass('pin-value two columns');

                var $toggle = createPowerToggleElement(pin);

                $toggle.appendTo($value);
                $name.appendTo($pin);
                $value.appendTo($pin);
                $pin.appendTo($container);
            }
        });
    };

    var initBindings = function() {
        $container.on('click touch', '.pin-ctrl-container', function() {
            var $input = $(this).find('.pin-ctrl');
            var pinNumber = $input.data('number');
            var val = $input.prop('checked') ? 0 : 1;

            execute(
                {
                    type: 'request',
                    action: 'gpio.write',
                    args: {
                        pin: pinNumber,
                        val: val,
                    }
                },

                onSuccess = function(response) {
                    var val = response.response.output.val;
                    $input.prop('checked', val == 0 ? false : true);
                }
            );
        });
    };

    var init = function() {
        initElements();
        initBindings();
    };

    init();
});

