<template>
  <div v-show="polygon.isActive" class="flex-style">
    <div class="evenly-space">
      <PanelButton name="Complete Polygon" @click="polygon.complete" />
    </div>
    <div class="evenly-space">
      <PanelButton name="Delete Polygon" @click="polygon.deletePolygon" />
    </div>
    <!-- <div v-show="false">
      <PanelToggle name="Guidance" v-model="polygon.polygon.guidance" />
      <PanelToggle name="Auto Select Color" v-model="polygon.color.auto" />
      <PanelToggle
        v-show="polygon.color.auto"
        name="Only Black or White"
        v-model="polygon.color.blackOrWhite"
      />
      <PanelInputString
        name="Stroke Color"
        v-model="polygon.polygon.pathOptions.strokeColor"
      />
    </div> -->
    <!-- <PanelInputNumber
      class="evenly-space"
      name="Auto Complete"
      :min="polygon.polygon.minCompleteDist"
      :max="polygon.polygon.maxCompleteDist"
      :step="polygon.polygon.stepCompleteDist"
      v-model="polygon.polygon.completeDistance"
    /> -->
    <!-- <PanelInputNumber
      class="evenly-space"
      name="Min Distance"
      :min="polygon.polygon.minDist"
      :max="polygon.polygon.maxDist"
      :step="polygon.polygon.stepDist"
      v-model="polygon.polygon.minDistance"
    /> -->
  </div>
</template>

<script>
import PanelButton from "@/components/PanelButton";
import PanelToggle from "@/components/PanelToggle";
import PanelInputString from "@/components/PanelInputString";
import PanelInputNumber from "@/components/PanelInputNumber";

export default {
  name: "PolygonPanel",
  components: { PanelButton, PanelToggle, PanelInputString, PanelInputNumber },
  props: {
    polygon: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.flex-style {
  display: flex;
  white-space: nowrap;
  /* width: 50%; */
  align-items: center;
}

.evenly-space {
  padding: 0 4px 0 4px;
}
</style>
