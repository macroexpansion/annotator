<template>
  <button
    class="btn btn-info tool-input-button"
    @click="$emit('click')"
  >
    {{ name }}
  </button>
</template>

<script>
export default {
  name: "PanelButton",
  props: {
    name: {
      type: String,
      required: true
    }
  }
};
</script>

<style scoped>
.tool-input-button {
  height: 20px;
  padding: 0 5px 0 5px;
  font-size: 12px;
  /* margin: 0 0 3px 0; */
}

</style>
