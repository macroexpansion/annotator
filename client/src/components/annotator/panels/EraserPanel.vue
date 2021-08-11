<template>
  <div v-show="eraser.isActive" class="flex-style" style="width: 15%">
    <PanelInputNumber
      class="evenly-space"
      name="Radius"
      :min="eraser.eraser.pathOptions.minRadius"
      :max="eraser.eraser.pathOptions.maxRadius"
      :step="eraser.eraser.pathOptions.stepRadius"
      v-model="eraser.eraser.pathOptions.radius"
    />
    <!-- <PanelInputString
      class="evenly-space"
      name="Stroke Color"
      v-model="eraser.eraser.pathOptions.strokeColor"
    /> -->
  </div>
</template>

<script>
// import PanelInputString from "@/components/PanelInputString";
import PanelInputNumber from "@/components/PanelInputNumber";

export default {
  name: "EraserPanel",
  components: {
    // PanelInputString,
    PanelInputNumber
  },
  props: {
    eraser: {
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
  padding: 0 4px 0 4px;
}
</style>

