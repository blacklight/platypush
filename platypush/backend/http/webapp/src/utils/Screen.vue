<script>
export default {
  name: "Screen",
  methods: {
    isMobile() {
      return window.matchMedia("only screen and (max-width: 760px)").matches
    },
  },
}
</script>
