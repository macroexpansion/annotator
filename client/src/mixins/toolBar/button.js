export default {
  template:
    `<div style='padding: 2px 0 2px 0'>
      <i class='fa fa-lg' :class='icon' :style='{ color: iconColor }' @click='click'></i>
      <div class='text-wrap' :style="{ color: iconColor, 'font-size': '13px', cursor: 'default'}">
        {{ this.name }}
      </div>
    </div>`,
  data() {
    return {
      color: {
        enabled: "white",
        active: "#2ecc71",
        disabled: "gray"
      },
      iconColor: "",
      delay: 400
    };
  },
  methods: {
    click() {
      if (!this.disabled) {
        this.toggleAnimation();
        this.execute();
      }
    },
    toggleAnimation() {
      this.iconColor = this.color.active;
      setTimeout(() => {
        this.iconColor = this.color.enabled;
      }, this.delay);
    }
  },
  created() {
    this.iconColor = this.color.enabled;
  }
};
