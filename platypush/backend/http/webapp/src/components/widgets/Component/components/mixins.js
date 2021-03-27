import Utils from "@/Utils";

export default {
    mixins: [Utils],
    props: {
        // Actions to run upon interaction with the widget. Format:
        //
        // [
        //   {
        //     "action": "light.hue.toggle",
        //     "args": {
        //       "lights": ["Bulb 1", "Bulb 2"]
        //     }
        //   },
        //   {
        //     "action": "music.mpd.pause"
        //   }
        // ]
        actions: {
            type: Array,
            default: () => { return [] },
        },

        // Map of variables used by this component, in the form
        // of variable_name -> variable_value.
        _vars: {
            type: Object,
            default: () => { return {} },
        },

        // Map of handlers, in the form of event_type -> functions.
        // Supported event handler types:
        //
        //   - mounted: Function to execute when the component is mounted.
        //   - beforeActions: Function to execute before the component action is run.
        //   - afterActions: Function to execute after the component action is run.
        //   - refresh: Function to be called at startup (if mounted is also specified
        //              then refresh will be called after mounted when the component is
        //              first mounted) and at regular intervals defined on the
        //              interval property (default: 10 seconds).
        //   - events: This is a mapping of functions that react to Platypush
        //             platform events published on the websocket (e.g. lights or
        //             switches toggles, media events etc.). The form is
        //             platypush_event_type -> function.
        handlers: {
            type: Object,
            default: () => { return {} },
        },

        // Event bus
        bus: {
            type: Object,
        },
    },

    data() {
        return {
            vars: {...(this._vars || {})},
            _interval: undefined,
            refresh: null,
            refreshInterval: null,
            value: null,
        }
    },

    methods: {
        async run() {
            if (this.handlers.input)
                return this.handlers.input(this)(this.value)

            if (this.handlers.beforeActions)
                await this.handlers.beforeActions(this)
            for (const action of this.actions)
                await this.request_(action)
            if (this.handlers.afterActions) {
                await this.handlers.afterActions(this)
            }
        },

        async request_(action) {
            const args = Object.entries(action.args).reduce((args, [key, value]) => {
                if (value.trim) {
                    value = value.trim()
                    const m = value.match(/^{{\s*(.*)\s*}}/)
                    if (m) {
                        value = eval(`// noinspection JSUnusedLocalSymbols
                        (function (self) {
                            return ${m[1]}
                        })`)(this)
                    }
                }

                args[key] = value
                return args
            }, {})

            await this.request(action.action, args)
        },

        async processEvent(event) {
            const hndl = (this.handlers.events || {})[event.type]
            if (hndl)
                await hndl(this)(event)
        },
    },

    async mounted() {
        this.$root.bus.on('event', this.processEvent)

        if (this.handlers.mounted)
            await this.handlers.mounted(this)

        if (this.handlers.refresh) {
            this.refreshInterval = (this.handlers.refresh?.interval || 0) * 1000
            this.refresh = () => {
                this.handlers.refresh.handler(this)
            }

            await this.refresh()
            if (this.refreshInterval) {
                const self = this
                const wrapper = () => { return self.refresh() }
                this._interval = setInterval(wrapper, this.refreshInterval)
            }
        }
    },

    unmounted() {
        if (this._interval)
            clearInterval(this._interval)
    }
}
