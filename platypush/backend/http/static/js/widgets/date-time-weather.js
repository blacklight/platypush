$(document).ready(function() {
    var $widget = $('.widget.date-time-weather'),
        $dateElement = $widget.find('[data-bind=date]'),
        $timeElement = $widget.find('[data-bind=time]'),
        $sensorTempElement = $widget.find('[data-bind=sensor-temperature]'),
        $sensorHumidityElement = $widget.find('[data-bind=sensor-humidity]'),
        $forecastElement = $widget.find('[data-bind=forecast]'),
        $tempElement = $widget.find('[data-bind=temperature]'),
        currentIcon = undefined;

    var onEvent = function(event) {
        if (event.args.type == 'platypush.message.event.weather.NewWeatherConditionEvent') {
            updateTemperature(event.args.temperature);
            updateWeatherIcon(event.args.icon);
        } else if (event.args.type == 'platypush.message.event.sensor.SensorDataChangeEvent') {
            if ('temperature' in event.args.data) {
                updateSensorTemperature(event.args.data.temperature);
            }

            if ('humidity' in event.args.data) {
                updateSensorHumidity(event.args.data.humidity);
            }
        }
    };

    var updateTemperature = function(temperature) {
        $tempElement.text(Math.round(temperature));
    };

    var updateWeatherIcon = function(icon) {
        var skycons = new Skycons({
            'color':'#333', 'resizeClear':'true'
        });

        if (currentIcon) {
            skycons.remove('weather-icon');
        }

        skycons.add('weather-icon', icon);
        currentIcon = icon;
    };

    var updateSensorTemperature = function(temperature) {
        $sensorTempElement.text(Math.round(temperature*10)/10);
        $sensorTempElement.parent().show();
    };

    var updateSensorHumidity = function(humidity) {
        $sensorHumidityElement.text(Math.round(humidity));
        $sensorHumidityElement.parent().show();
    };

    var initEvents = function() {
        window.registerEventListener(onEvent);
    };

    var refreshDateTime = function() {
        var now = new Date();
        $dateElement.text(now.toDateString());
        $timeElement.text(now.getHours() + ':' +
            (now.getMinutes() < 10 ? '0' : '') + now.getMinutes() + ':' +
            (now.getSeconds() < 10 ? '0' : '') + now.getSeconds());
    };


    var initWeather = function() {
        execute(
            {
                type: 'request',
                action: 'weather.forecast.get_current_weather',
            },

            onSuccess = function(response) {
                updateTemperature(status=response.response.output.temperature);
                updateWeatherIcon(response.response.output.icon);
            }
        );
    };

    var refreshForecast = function() {
        execute(
            {
                type: 'request',
                action: 'weather.forecast.get_hourly_forecast',
            },

            onSuccess = function(response) {
                $forecastElement.text(response.response.output.summary);
            }
        );
    };

    var initWidget = function() {
        refreshDateTime();
        setInterval(refreshDateTime, 500);
        refreshForecast();
        setInterval(refreshForecast, 1200000);
        initWeather();
    };

    var init = function() {
        initEvents();
        initWidget();
    };

    init();
});

