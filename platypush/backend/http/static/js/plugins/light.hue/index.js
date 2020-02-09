Vue.component('light-hue', {
    template: '#tmpl-light-hue',
    props: ['config'],
    data: function() {
        return {
            groups: {},
            lights: {},
            scenes: {},
            animations: {},
            selectedGroup: undefined,
            selectedScene: undefined,
            selectedProperties: {
                type: undefined,
                id: undefined,
            },
        };
    },

    methods: {
        _prepareGroups: function() {
            for (const [groupId, group] of Object.entries(this.groups)) {
                if (group.type !== 'Room' || group.recycle) {
                    delete this.groups[groupId];
                    continue;
                }

                this.groups[groupId].scenes = {};
                let lights = {};

                for (const lightId of this.groups[groupId].lights) {
                    lights[lightId] = this.lights[lightId];
                }

                this.groups[groupId].lights = lights;
            }
        },

        _prepareScenes: function() {
            for (const [sceneId, scene] of Object.entries(this.scenes)) {
                if (scene.recycle) {
                    delete this.scenes[sceneId];
                    continue;
                }

                this.scenes[sceneId].groups = {};
            }
        },

        _linkLights: function() {
            // Special group for lights with no group
            this.groups[-1] = {
                type: undefined,
                lights: {},
                scenes: {},
                name: "[No Group]",
                recycle: false,
            };

            for (const [lightId, light] of Object.entries(this.lights)) {
                this.lights[lightId].groups = {};

                for (const [groupId, group] of Object.entries(this.groups)) {
                    if (lightId in group.lights) {
                        this.lights[lightId].groups[groupId] = group;
                    }
                }

                if (!light.groups.length) {
                    this.groups[-1].lights[lightId] = light;
                }
            }

            if (!this.groups[-1].lights.length) {
                delete this.groups[-1];
            }
        },

        _linkScenes: function() {
            for (const [sceneId, scene] of Object.entries(this.scenes)) {
                for (const lightId of scene.lights) {
                    for (const [groupId, group] of Object.entries(this.lights[lightId].groups)) {
                        this.scenes[sceneId].groups[groupId] = group;
                        this.groups[groupId].scenes[sceneId] = scene;
                    }
                }
            }
        },

        refresh: async function() {
            const getLights = request('light.hue.get_lights');
            const getGroups = request('light.hue.get_groups');
            const getScenes = request('light.hue.get_scenes');
            const getAnimations = request('light.hue.get_animations');

            [this.lights, this.groups, this.scenes, this.animations] = await Promise.all(
                [getLights, getGroups, getScenes, getAnimations]);

            this._prepareGroups();
            this._prepareScenes();
            this._linkLights();
            this._linkScenes();
        },

        updatedGroup: function(event) {
            for (const light of Object.values(this.groups[this.selectedGroup].lights)) {
                if (event.state.any_on === event.state.all_on) {
                    light.state.on = event.state.all_on;
                }

                for (const attr in ['hue', 'sat', 'bri', 'xy', 'ct']) {
                    if (attr in event.state) {
                        light.state[attr] = event.state[attr];
                    }
                }
            }
        },

        startedAnimation: function(value) {
            this.animations.groups[this.selectedGroup] = value;
        },

        stoppedAnimation: function() {
            this.animations.groups[this.selectedGroup] = undefined;
        },

        selectScene: async function(event) {
            await request(
                'light.hue.scene', {
                    name: event.name,
                    groups: [this.groups[this.selectedGroup].name],
                },
            );

            this.selectedScene = event.id;
            const groups = {};

            for (const lightId of Object.values(this.scenes[this.selectedScene].lights)) {
                this.lights[lightId].state.on = true;

                for (const [groupId, group] of Object.entries(this.lights[lightId].groups)) {
                    if (!(group.id in groups)) {
                        groups[groupId] = {
                            any_on: true,
                            all_on: group.state.all_on,
                            lights: [],
                        }
                    }

                    groups[groupId].lights.push(lightId);

                    if (groups[groupId].lights.length === Object.values(group.lights).length) {
                        groups[groupId].all_on = true;
                    }
                }
            }

            for (const [id, group] of Object.entries(groups)) {
                this.groups[id].state = {
                    ...group.state,
                    any_on: group.any_on,
                    any_off: group.any_off,
                }
            }
        },

        collapsedToggled: function(event) {
            if (event.type === this.selectedProperties.type
                    && event.id === this.selectedProperties.id) {
                this.selectedProperties = {
                    type: undefined,
                    id: undefined,
                };
            } else {
                this.selectedProperties = {
                    type: event.type,
                    id: event.id,
                };
            }
        },

        onUnitInput: function(event) {
            for (let attr of ['on', 'hue', 'sat', 'bri', 'xy', 'ct']) {
                if (attr in event) {
                    this.lights[event.id].state[attr] = event[attr];
                }
            }

            let groups = this.lights[event.id].groups;
            for (const [groupId, group] of Object.entries(groups)) {
                if (event.on === true) {
                    this.groups[groupId].state.any_on = true;
                    this.groups[groupId].state.all_on = Object.values(group.lights).filter((l) => l.state.on).length === Object.values(group.lights).length;
                } else if (event.on === false) {
                    this.groups[groupId].state.all_on = false;
                    this.groups[groupId].state.any_on = Object.values(group.lights).filter((l) => l.state.on).length > 0;
                }
            }
        },

        eventHandler: function(event) {
            if ('light_id' in event) {
                this.onUnitInput({
                    ...event,
                    id: event.light_id,
                });
            } else if ('group_id' in event) {
                let args = {
                    id: event.group_id,
                    state: {
                        ...event,
                    },
                };

                if ('on' in event) {
                    args.state.any_on = event.on;
                    args.state.all_on = event.on;
                }

                this.updatedGroup(args);
            }
        },
    },

    created: function() {
        this.refresh();
        registerEventHandler(this.eventHandler, 'platypush.message.event.light.LightStatusChangeEvent');
    },
});

