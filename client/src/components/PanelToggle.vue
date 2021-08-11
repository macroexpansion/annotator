<template>
  <div class="form-check text-left">
    <input
      type="checkbox"
      class="form-check-input"
      :id="slugify(name)"
      v-model="checked"
    />
    <label class="form-check-label" :for="slugify(name)">{{ name }}</label>
  </div>
</template>

<script>
export default {
  name: "ToggleButton",
  model: {
    prop: "value",
    event: "update",
  },
  props: {
    name: {
      type: String,
      required: true,
    },
    value: {
      type: Boolean,
      required: true,
    },
    filterToggle: {
      type: Boolean,
      required: false,
    },
  },
  data() {
    return {
      checked: this.value,
    };
  },
  methods: {
    slugify(name) {
      return name.trim().replace(/ /g, "-").toLowerCase();
    },
  },
  watch: {
    checked() {
      if (this.filterToggle) {
        localStorage.setItem("pagination/page", 1);
        this.$emit("update", this.checked);
      } else {
        this.$emit("update", this.checked);
      }
    },
  },
};
</script>

<style scoped>
.tool-input-button {
  height: 20px;
  border-color: #4b5162;
  padding: 0 0 0 11px;
  font-size: 12px;
  width: 100%;
}

.tool-input-button:hover {
  background-color: transparent;
  color: white;
}
</style>
