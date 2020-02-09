Vue.component('zwave-group', {
    template: '#tmpl-zwave-group',
    props: ['group','nodes','bus','selected'],

    methods: {
        onGroupClicked: function() {
            this.bus.$emit('groupClicked', {
                groupId: this.group.index,
            });
        },

        removeFromGroup: async function(nodeId) {
            if (!confirm('Are you sure that you want to remove this node from ' + this.group.label + '?')) {
                return;
            }

            await request('zwave.remove_node_from_group', {
                node_id: nodeId,
                group_index: this.group.index,
            });
        },
    },
});

