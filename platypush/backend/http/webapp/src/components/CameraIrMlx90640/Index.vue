<template>
  <Camera camera-plugin="ir.mlx90640" />
</template>

<script>
import Camera from "@/components/panels/Camera/Index";

export default {
  name: "CameraIrMlx90640",
  components: {Camera},
}
</script>
