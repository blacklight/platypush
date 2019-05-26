Vue.component('range-slider', {
    template: '#tmpl-range-slider',
    props: ['min','max','value'],

    mounted: function() {
        var input = this.$el.querySelector('input[type=range]');
        var supportsMultiple = self.HTMLInputElement && "valueLow" in HTMLInputElement.prototype;
        var descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");

        if (supportsMultiple || input.classList.contains("multirange")) {
            return;
        }

        var values = [];
        if (Array.isArray(this.value)) {
            values = this.value;
        } else if (this.value !== null) {
            values = this.value.split(",");
        }

        var min = +(this.min || 0);
        var max = +(this.max || 100);
        var ghost = input.cloneNode();

        input.classList.add("multirange", "original");
        ghost.classList.add("multirange", "ghost");

        input.value = values[0] !== undefined ? values[0] : min + (max - min) / 2;
        ghost.value = values[1] !== undefined ? values[1] : min + (max - min) / 2;

        input.parentNode.insertBefore(ghost, input.nextSibling);

        Object.defineProperty(input, "originalValue", descriptor.get ? descriptor : {
            // Fuck you Safari >:(
            get: function() { return this.value; },
            set: function(v) { this.value = v; }
        });

        Object.defineProperties(input, {
            valueLow: {
                get: function() { return Math.min(this.originalValue, ghost.value); },
                set: function(v) { this.originalValue = v; },
                enumerable: true
            },
            valueHigh: {
                get: function() { return Math.max(this.originalValue, ghost.value); },
                set: function(v) { ghost.value = v; },
                enumerable: true
            }
        });

        if (descriptor.get) {
            // Again, fuck you Safari
            Object.defineProperty(input, "value", {
                get: function() { return this.valueLow + "," + this.valueHigh; },
                set: function(v) {
                    var values = v.split(",");
                    this.valueLow = values[0];
                    this.valueHigh = values[1];
                    update();
                },
                enumerable: true
            });
        }

        input.oninput = this.changed;
        ghost.oninput = this.changed;

        function update() {
            ghost.style.setProperty("--low", 100 * ((input.valueLow - min) / (max - min)) + 1 + "%");
            ghost.style.setProperty("--high", 100 * ((input.valueHigh - min) / (max - min)) - 1 + "%");
        }

        input.addEventListener("input", update);
        ghost.addEventListener("input", update);

        update();
    },

    methods: {
        changed: function(event) {
            const value = this.$el.querySelectorAll('input[type=range]')[0].value
                .split(',').map(_ => parseFloat(_));

            this.$emit('changed', value);
        },
    },
});

