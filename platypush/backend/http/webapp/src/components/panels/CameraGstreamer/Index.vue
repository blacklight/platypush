<template>
  <Camera camera-plugin="gstreamer" />
</template>

<script>
import Camera from "@/components/panels/Camera/Index";

export default {
  name: "CameraGstreamer",
  components: {Camera},
}
</script>
