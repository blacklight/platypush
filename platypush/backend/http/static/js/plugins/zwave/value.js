Vue.component('zwave-value', {
    template: '#tmpl-zwave-value',
    props: ['node','bus','selected','values'],
    data: function() {
        return {
        };
    },

    methods: {
        onNodeClicked: function() {
            this.bus.$emit('nodeClicked', {
                nodeId: this.node.node_id,
            });
        },

        disableForm: function(form) {
            form.querySelector('input,button').readOnly = true;
        },

        enableForm: function(form) {
            form.querySelector('input,button').readOnly = false;
        },

        onEditMode: function(mode) {
            Vue.set(this.editMode, mode, true);
            const form = this.$refs[mode + 'Form'];
            const input = form.querySelector('input[type=text]');

            setTimeout(() => {
                input.focus();
                input.select();
            }, 10);
        },

        editName: function(event) {
            const value = this.node.values[event.target.parentElement.dataset.idOnNetwork];
            const name = prompt('New name', value.label);

            if (!name || !name.length || name === value.label) {
                return;
            }

            request('zwave.set_value_label', {
                id_on_network: value.id_on_network,
                new_label: name,
            }).then(() => {
                this.bus.$emit('refreshNodes');
                createNotification({
                    text: 'Value successfully renamed',
                    image: { icon: 'check' }
                });
            });
        },

        onValueChanged: function(event) {
            const target = event.target ? event.target : event.event.target.parentElement;
            const value = this.node.values[target.dataset.idOnNetwork];
            const data = value.type === 'List' ? value.data_items[event.target.value] : (target.value || event.value);

            request('zwave.set_value', {
                id_on_network: value.id_on_network,
                data: data,
            }).then(() => {
                this.bus.$emit('refreshNodes');
                createNotification({
                    text: 'Value successfully modified',
                    image: { icon: 'check' }
                });
            });
        },
    },
});

