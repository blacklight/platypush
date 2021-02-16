<template>
  <Camera camera-plugin="ir.mlx90640" ref="camera" />
</template>

<script>
import Camera from "@/components/panels/Camera/Index";

export default {
  name: "CameraIrMlx90640",
  components: {Camera},

  mounted() {
    const config = this.$root.config[`camera.${this.cameraPlugin}`] || {}
    if (!config.resolution)
      this.$refs.camera.attrs.resolution = [32, 24]
    if (!config.scale_x)
      this.$refs.camera.attrs.scale_x = 15
    if (!config.scale_y)
      this.$refs.camera.attrs.scale_y = 15
  },
}
</script>
