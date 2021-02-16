<template>
  <Camera camera-plugin="ir.mlx90640" ref="camera" />
</template>

<script>
import Camera from "@/components/panels/Camera/Index";

export default {
  name: "CameraIrMlx90640",
  components: {Camera},

  mounted() {
    console.log(this.$refs.camera.attrs.resolution)
    const config = this.$root.config[`camera.${this.cameraPlugin}`] || {}
    if (!config.resolution)
      this.$refs.camera.attrs.resolution = [32, 24]

    console.log(this.$refs.camera.attrs.resolution)
  },
}
</script>
