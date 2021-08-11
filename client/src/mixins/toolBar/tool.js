import paper from "paper";

export default {
  model: {
    prop: "selected",
    event: "update"
  },
  props: {
    selected: {
      type: String,
      required: true
    }
  },
  template:
    `<div style='padding: 2px 0 2px 0' @click='click'>
      <i class='fa fa-lg' :class='icon' :style='{ color: iconColor }' @click='click'></i>
      <div class='text-nowrap' :style="{ color: iconColor, 'font-size': '13px' }">
        {{ this.name }}
      </div>
    </div>`,
  data() {
    return {
      tool: null,
      enabled: false,
      cursor: "default",
      color: {
        enabled: "white",
        active: "#2ecc71",
        disabled: "gray",
        toggle: "red"
      }
    };
  },
  methods: {
    onMouseMove() {},
    onMouseDown() {},
    onMouseDrag() {},
    onMouseUp() {},
    click() {
      this.update();
    },
    update() {
      if (this.isDisabled) return;

      this.$emit("update", this.name);
    },
    setPreferences() {}
  },
  computed: {
    isActive() {
      if (this.selected == this.name) {
        this.$emit("setcursor", this.cursor);
        return true;
      }
      return false;
    },
    iconColor() {
      if (this.isDisabled) return this.color.disabled;

      if (this.isToggled) return this.color.toggle;
      if (this.isActive) return this.color.active;

      return this.color.enabled;
    },
    textColor() {
      if (this.isToggled) return this.color.toggle;
      if (this.isActive) return this.color.active;

      return this.color.enabled;
    },
    isDisabled() {
      return false;
    }
  },
  watch: {
    isActive(active) {
      if (active) {
        this.tool.activate();
      }
    },
    isDisabled(disabled) {
      if (disabled && this.isActive) {
        this.$emit("update", "Select");
      }
    }
  },
  mounted() {
    this.tool = new paper.Tool();

    this.tool.onMouseDown = this.onMouseDown;
    this.tool.onMouseDrag = this.onMouseDrag;
    this.tool.onMouseMove = this.onMouseMove;
    this.tool.onMouseUp = this.onMouseUp;
  }
};
