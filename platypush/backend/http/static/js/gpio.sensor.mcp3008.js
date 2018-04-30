$(document).ready(function() {
    var $container = $('#sensors-container');

    var onEvent = function(event) {
        switch (event.args.type) {
            case 'platypush.message.event.sensor.SensorDataChangeEvent':
                var data = event.args.sensors;

                for (var sensor of Object.keys(data)) {
                    var $sensor = $container.find('[data-sensor-type=' + sensor + ']');
                    var $sensorValue;

                    if ($sensor.length === 0) {
                        $sensor = $('<div></div>')
                            .addClass('row sensor-data')
                            .attr('data-sensor-type', sensor);

                        var $name = $('<div></div>')
                            .addClass('sensor-name six columns')
                            .text(sensor);

                        $sensorValue = $('<div></div>')
                            .addClass('sensor-value six columns');

                        $sensor.appendTo($container);
                    } else {
                        $sensorValue = $sensor.find('.sensor-value');
                    }

                    $sensorValue.text(data[sensor]);
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

