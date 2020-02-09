Vue.component('zwave-node', {
    template: '#tmpl-zwave-node',
    props: ['node','bus','selected'],
    data: function() {
        return {
            editMode: {
                name: false,
            },
        };
    },

    methods: {
        onNodeClicked: function() {
            this.bus.$emit('nodeClicked', {
                nodeId: this.node.node_id,
            });
        },

        removeFailedNode: async function() {
            if (!confirm('Are you sure that you want to remove this node?')) {
                return;
            }

            await request('zwave.remove_node', {
                node_id: this.node.node_id,
            });
        },

        replaceFailedNode: async function() {
            if (!confirm('Are you sure that you want to replace this node?')) {
                return;
            }

            await request('zwave.replace_node', {
                node_id: this.node.node_id,
            });
        },

        replicationSend: async function() {
            await request('zwave.replication_send', {
                node_id: this.node.node_id,
            });
        },

        requestNetworkUpdate: async function() {
            await request('zwave.request_network_update', {
                node_id: this.node.node_id,
            });
        },

        requestNeighbourUpdate: async function() {
            await request('zwave.request_node_neighbour_update', {
                node_id: this.node.node_id,
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

        editName: async function(event) {
            this.disableForm(event.target);
            const name = event.target.querySelector('input[name=name]').value;

            await request('zwave.set_node_name', {
                node_id: this.node.node_id,
                new_name: name,
            });

            this.editMode.name = false;
            this.enableForm(event.target);
        },

        heal: async function(event) {
            await request('zwave.node_heal', {
                node_id: this.node.node_id,
            });
        },
    },
});

