$(document).ready(function() {
    var $container = $('#sensors-container');

    var onEvent = function(event) {
        switch (event.args.type) {
            case 'platypush.message.event.sensor.SensorDataChangeEvent':
                var data = event.args.data;

                for (var sensor of Object.keys(data)) {
                    var $sensor = $container.find('[data-sensor-type=' + sensor + ']');
                    var $value;

                    if ($sensor.length === 0) {
                        $sensor = $('<div></div>')
                            .addClass('row sensor-data')
                            .attr('data-sensor-type', sensor);

                        var $name = $('<div></div>')
                            .addClass('sensor-name six columns')
                            .text(sensor);

                        $value = $('<div></div>')
                            .addClass('sensor-value six columns');

                        $name.appendTo($sensor);
                        $value.appendTo($sensor);
                        $sensor.appendTo($container);
                    } else {
                        $value = $sensor.find('.sensor-value');
                    }

                    $value.text(data[sensor]);
                }

                break;
        }
    };

    var initEvents = function() {
        window.registerEventListener(onEvent);
    };

    var init = function() {
        initEvents();
    };

    init();
});

