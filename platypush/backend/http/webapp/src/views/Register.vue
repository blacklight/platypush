<template>
  <Login :register="true" />
</template>

<script>
import Login from "@/views/Login";

export default {
  name: "Register",
  mixins: [Login],
  components: {Login},
  props: {
    register: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
}
</script>
