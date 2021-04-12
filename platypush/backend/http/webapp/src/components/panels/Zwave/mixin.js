import Utils from "@/Utils";

export default {
    mixins: [Utils],
    props: {
        pluginName: {
            type: String,
            required: true,
        },
    },

    methods: {
        async zrequest(method, args) {
            return await this.request(`${this.pluginName}.${method}`, args)
        },
    }
}
