Vue.component('image-carousel', {
    template: '#tmpl-widget-image-carousel',
    props: ['config'],

    data: function() {
        return {
            images: [],
            currentImage: undefined,
        };
    },

    methods: {
        refresh: async function() {
            if (!this.images.length) {
                this.images = await request('utils.search_web_directory', {
                    directory: this.config.images_path,
                    extensions: ['.jpg', '.jpeg', '.png'],
                });

                this.shuffleImages();
            }

            this.currentImage = this.images.pop();
        },

        onNewImage: function() {
            this.$refs.background.style['background-image'] = 'url(' + this.currentImage + ')';
            this.$refs.img.style.width = 'auto';

            if (this.$refs.img.width > this.$refs.img.height) {
                if ((this.$refs.img.width / this.$refs.img.height) >= 1.25) {
                    this.$refs.img.style.width = '100%';
                }

                if ((this.$refs.img.width / this.$refs.img.height) <= 16/9) {
                    this.$refs.img.style.height = '100%';
                }
            }
        },

        shuffleImages: function() {
            for (var i=this.images.length-1; i > 0; i--) {
                let j = Math.floor(Math.random() * (i+1));
                let x = this.images[i];
                Vue.set(this.images, i, this.images[j]);
                Vue.set(this.images, j, x);
            }
        },
    },

    mounted: function() {
        this.$refs.img.addEventListener('load', this.onNewImage);
        this.$refs.img.addEventListener('error', this.refresh);

        this.refresh();
        setInterval(this.refresh, 'refresh_seconds' in this.config ? this.config.refresh_seconds*1000 : 15000);
    },
});

