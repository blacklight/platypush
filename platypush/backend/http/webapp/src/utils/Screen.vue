<script>
export default {
  name: "Screen",
  methods: {
    isMobile() {
      return window.matchMedia("only screen and (max-width: 768px)").matches
    },

    isTablet() {
      return (
        !this.isMobile() &&
        window.matchMedia("only screen and (max-width: 1023px)").matches
      )
    },

    isDesktop() {
      return window.matchMedia("only screen and (min-width: 1024px)").matches
    },
  },
}
</script>
