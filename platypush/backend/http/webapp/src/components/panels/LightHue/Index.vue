<template>
  <Light plugin-name="light.hue" />
</template>

<script>
import Light from "@/components/panels/Light/Index";

export default {
  name: "LightHue",
  mixins: [Light],
  components: {Light},
}
</script>
