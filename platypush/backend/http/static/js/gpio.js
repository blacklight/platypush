$(document).ready(function() {
    var $container = $('#gpio-container');

    var initElements = function() {
        execute({ type: 'request', action: 'gpio.read_all' }, function(data) {
            var response = data.response.output;

            for (var pin of response) {
                var $pin = $('<div></div>').addClass('row gpio-pin').data('pin', pin.pin);
                var $name = $('<div></div>').addClass('pin-name ten columns').text(pin.name);
                var $value = $('<div></div>').addClass('pin-value two columns');
                var $select = $('<select></select>').data('pin', pin.pin).addClass('pin-ctrl');
                var $option0 = $('<option></option>').attr('name', '0').text('0');
                var $option1 = $('<option></option>').attr('name', '1').text('1');

                $option0.appendTo($select);
                $option1.appendTo($select);
                $select.appendTo($value);
                $name.appendTo($pin);
                $value.appendTo($pin);
                $pin.appendTo($container);
            }
        });
    };

    var initBindings = function() {
        $container.on('change', '.pin-ctrl', function() {
            var pin = $(this).data('pin');
            var val = parseInt($(this).val());

            execute(
                {
                    type: 'request',
                    action: 'gpio.write',
                    args: {
                        pin: pin,
                        val: val,
                    }
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

