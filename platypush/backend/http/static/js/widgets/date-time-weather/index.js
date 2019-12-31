Vue.component('date-time-weather', {
    template: '#tmpl-widget-date-time-weather',
    props: ['config'],

    data: function() {
        return {
            weather: undefined,
            sensors: {},
            now: new Date(),
            weatherIcon: undefined,
        };
    },

    methods: {
        refresh: async function() {
            let weather = (await request('weather.darksky.get_hourly_forecast')).data[0];
            this.onWeatherChange(weather);
        },

        refreshTime: function() {
            this.now = new Date();
        },

        formatDate: function(date) {
            return date.toDateString().substring(0, 10);
        },

        formatTime: function(date) {
            return date.toTimeString().substring(0, 8);
        },

        onWeatherChange: function(event) {
            if (!this.weather)
                this.weather = {};

            Vue.set(this, 'weather', {...this.weather, ...event});

            var skycons = new Skycons({
                'color':'#333', 'resizeClear':'true'
            });

            if (this.weatherIcon) {
                skycons.remove('weather-icon');
            }

            skycons.add('weather-icon', this.weather.icon);
            this.weatherIcon = this.weather.icon;
        },

        onSensorData: function(event) {
            if ('temperature' in event.data)
                this.sensors.temperature = event.data.temperature;

            if ('humidity' in event.data)
                this.sensors.temperature = event.data.humidity;
        },
    },

    mounted: function() {
        this.refresh();
        setInterval(this.refresh, 900000);
        setInterval(this.refreshTime, 1000);

        registerEventHandler(this.onWeatherChange, 'platypush.message.event.weather.NewWeatherConditionEvent');
        registerEventHandler(this.onSensorData, 'platypush.message.event.sensor.SensorDataChangeEvent');
    },
});

