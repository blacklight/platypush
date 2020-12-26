<script>
export default {
  name: "Screen",
  methods: {
    isMobile() {
      return window.matchMedia("only screen and (max-width: 760px)").matches
    },

    isTablet() {
      return !this.isMobile() && window.matchMedia("only screen and (max-width: 960px)").matches
    },

    isDesktop() {
      return window.matchMedia("only screen and (min-width: 1152px)").matches
    },
  },
}
</script>
