Vue.component('execute', {
    template: '#tmpl-execute',
    props: ['config'],
    data: function() {
        return {
            loading: false,
            running: false,
            structuredInput: true,
            actionChanged: false,
            selectedDoc: undefined,
            selectedProcedure: {
                name: undefined,
                args: {},
            },

            response: undefined,
            error: undefined,
            htmlDoc: false,
            rawRequest: undefined,
            actions: {},
            plugins: {},
            procedures: {},
            action: {
                name: undefined,
                args: {},
                extraArgs: [],
                supportsExtraArgs: false,
            },
        };
    },

    methods: {
        refresh: async function() {
            this.loading = true;
            this.procedures = window.config.procedures;
            this.plugins = await request('inspect.get_all_plugins', {html_doc: true});

            for (const plugin of Object.values(this.plugins)) {
                if (plugin.html_doc)
                    this.htmlDoc = true;

                for (const action of Object.values(plugin.actions)) {
                    action.name = plugin.name + '.' + action.name;
                    action.supportsExtraArgs = !!action.has_kwargs;
                    delete action.has_kwargs;
                    this.actions[action.name] = action;
                }
            }

            const self = this;
            autocomplete(this.$refs.actionName, Object.keys(this.actions).sort(), (evt, value) => {
                this.action.name = value;
                self.updateAction();
            });

            this.loading = false;
        },

        updateAction: function() {
            if (!this.actionChanged || !(this.action.name in this.actions))
                return;

            this.loading = true;
            this.action = {
                ...this.actions[this.action.name],
                args: Object.entries(this.actions[this.action.name].args).reduce((args, entry) => {
                    args[entry[0]] = {
                        ...entry[1],
                        value: entry[1].default,
                    };

                    return args;
                }, {}),
                extraArgs: [],
            };

            this.selectedDoc = this.action.doc;
            this.actionChanged = false;
            this.response = undefined;
            this.error = undefined;
            this.loading = false;
        },

        updateProcedure: function(name) {
            if (event.target.getAttribute('type') === 'submit') {
                return;
            }

            if (this.selectedProcedure.name === name) {
                this.selectedProcedure = {
                    name: undefined,
                    args: {},
                };

                return;
            }

            if (!(name in this.procedures)) {
                console.warn('Procedure not found: ' + name);
                return;
            }

            this.selectedProcedure = {
                name: name,
                args: this.procedures[name].args.reduce((args, arg) => {
                    args[arg] = undefined;
                    return args;
                }, {}),
            };
        },

        addParameter: function() {
            this.action.extraArgs.push({
                name: undefined,
                value: undefined,
            })
        },

        removeParameter: function(i) {
            this.action.extraArgs.pop(i);
        },

        selectAttrDoc: function(name) {
            this.response = undefined;
            this.error = undefined;
            this.selectedDoc = this.action.args[name].doc;
        },

        resetDoc: function() {
            this.response = undefined;
            this.error = undefined;
            this.selectedDoc = this.action.doc;
        },

        onInputTypeChange: function(structuredInput) {
            this.structuredInput = structuredInput;
            this.response = undefined;
            this.error = undefined;
        },

        onResponse: function(response) {
            this.response = '<pre>' + JSON.stringify(response, null, 2) + '</pre>';
            this.error = undefined;
        },

        onError: function(error) {
            this.response = undefined;
            this.error = '<pre>' + error + '</pre>';
        },

        onDone: function() {
            this.running = false;
        },

        executeAction: function() {
            if (!this.action.name && !this.rawRequest || this.running)
                return;

            this.running = true;
            if (this.structuredInput) {
                const args = {
                    ...Object.entries(this.action.args).reduce((args, param) => {
                        if (param[1].value != null) {
                            let value = param[1].value;
                            try {value = JSON.parse(value);}
                            catch (e) {}
                            args[param[0]] = value;
                        }
                        return args;
                    }, {}),

                    ...this.action.extraArgs.reduce((args, param) => {
                        let value = args[param.value];
                        try {value = JSON.parse(value);}
                        catch (e) {}

                        args[param.name] = value;
                        return args;
                    }, {})
                };

                request(this.action.name, args).then(this.onResponse).catch(this.onError).finally(this.onDone);
            } else {
                execute(JSON.parse(this.rawRequest)).then(this.onResponse).catch(this.onError).finally(this.onDone);
            }
        },

        executeProcedure: function(event) {
            if (!this.selectedProcedure.name || this.running)
                return;

            event.stopPropagation();
            this.running = true;
            const args = {
                ...Object.entries(this.selectedProcedure.args).reduce((args, param) => {
                    if (param[1] != null) {
                        let value = param[1];
                        try {value = JSON.parse(value);}
                        catch (e) {}
                        args[param[0]] = value;
                    }
                    return args;
                }, {}),
            };

            request('procedure.' + this.selectedProcedure.name, args)
                .then(this.onResponse).catch(this.onError).finally(this.onDone);
        },
    },

    created: function() {
        this.refresh();
    },
});

