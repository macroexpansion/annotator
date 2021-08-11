<template>
  <div class="input-group tool-input-group">
    <!-- <div > -->
      <span class="input-group-text tool-option-font">{{ name }}</span>
    <!-- </div> -->
    <input
      v-model.number="localValue"
      type="number"
      :min="min"
      :max="max"
      :step="step"
      class="tool-option-input form-control"
    />
  </div>
</template>

<script>
export default {
  name: "PanelInputNumber",
  model: {
    prop: "value",
    event: "update"
  },
  props: {
    name: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      required: true
    },
    max: {
      type: Number,
      default: 10
    },
    min: {
      type: Number,
      default: 1
    },
    step: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      localValue: this.value
    };
  },
  watch: {
    localValue() {
      if (this.localValue < this.min)
        this.localValue = this.min;
      if (this.localValue > this.max)
        this.localValue = this.max;

      this.$emit("update", this.localValue);
    },
    value(newValue) {
      let temp = newValue
      if (newValue < this.min) 
        temp = this.min;
      if (newValue > this.max)
        temp = this.max;

      this.localValue = temp;
    }
  }
};
</script>

<style scoped>
/* .tool-input-group {
  padding-top: 3px;
} */

.tool-option-pre {
  background-color: #383c4a;
}

.tool-option-font {
  border-color: #4b5162;
  background-color: #383c4a;
  color: white;
  font-size: 12px;
  height: 24px;
}

.tool-option-input {
  display: table-cell;
  border-color: #4b5162;
  color: white;
  padding: 0 0 0 3px;
  background-color: #383c4a;
  height: 24px;
  font-size: 12px;
  width: 30px;
}

</style>
