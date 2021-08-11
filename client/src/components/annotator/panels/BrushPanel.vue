<template>
  <div v-show="brush.isActive" class="flex-style" style="width: 40%">
    <PanelInputNumber
      class="evenly-space"
      name="Sides"
      :min="brush.brush.pathOptions.minSides"
      :max="brush.brush.pathOptions.maxSides"
      :step="brush.brush.pathOptions.stepSides"
      v-model="brush.brush.pathOptions.sides"
    />
    <PanelInputNumber
      class="evenly-space"
      name="Radius"
      :min="brush.brush.pathOptions.minRadius"
      :max="brush.brush.pathOptions.maxRadius"
      :step="brush.brush.pathOptions.stepRadius"
      v-model="brush.brush.pathOptions.radius"
    />
    <!-- <PanelInputString
      class="evenly-space"
      name="Stroke Color"
      v-model="brush.brush.pathOptions.strokeColor"
    /> -->
  </div>
</template>

<script>
// import PanelInputString from "@/components/PanelInputString";
import PanelInputNumber from "@/components/PanelInputNumber";

export default {
  name: "BrushPanel",
  components: { 
    // PanelInputString,
    PanelInputNumber
  },
  props: {
    brush: {
      type: Object,
      required: true
    }
  }
};
</script>

<style scoped>
.flex-style {
  display: flex;
}

.evenly-space {
  width: 80%;
  padding: 0 4px 0 4px;
}
</style>

