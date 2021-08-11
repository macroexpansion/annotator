<template>
  <div>
    <div v-if="shortcut.title != null" style="font-size: 13px">
      {{ shortcut.title }}
    </div>
    <div class="row" style="cell">
      <div class="col-sm">
        {{ shortcut.name }}
        <!-- <p v-show="readonly" class="mute">(readonly)</p> -->
      </div>

      <div class="col-sm">
        <input
          :id="_uid"
          :value="keys.join('+').toUpperCase()"
          type="text"
          class="input"
          :readonly="readonly"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CustomShortcut",
  props: {
    shortcut: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      keys: this.shortcut.default,
      keysDown: [],
      readonly: this.shortcut.readonly == null ? false : this.shortcut.readonly
    };
  },
  methods: {
    export() {
      return {
        name: this.shortcut.name,
        keys: this.keys
      };
    },
    function(event) {
      let target = event.target.tagName.toLowerCase();

      if (target === "input") return;
      if (target === "textarea") return;

      event.preventDefault();
      this.shortcut.function();
    },
    onkeydown(event) {
      if (this.readonly) {
        return;
      }

      let key = this.keyCorrections(event.key.toLowerCase());

      if (this.keysDown.indexOf(key) === -1) {
        this.keysDown.push(key);
      }

      if (parseInt(event.target.id) === this._uid) {
        event.preventDefault();
        this.keys = this.keysDown;
      } else if (this.$route.name === "annotate") {
        if (this.keysDown.sort().join(",") === this.keys.sort().join(",")) {
          this.function(event);
        }
      }
    },
    onkeyup(event) {
      let key = this.keyCorrections(event.key.toLowerCase());
      
      if (key === "shift") {
        let event = this.$parent.$parent.$refs.select.currentEvent;
        this.$parent.$parent.activeTool = this.$parent.$parent.lastTool;
        
        if (["Brush", "Eraser"].includes(this.$parent.$parent.activeTool)) {
          this.$parent.$parent.$refs[this.$parent.$parent.activeTool.toLowerCase()].onMouseMove(event);
        }
      }

      if (key === " ") {
        key = "space";
      }
      this.keysDown = this.keysDown.filter(a => a !== key);
    },
    keyCorrections(key) {
      if (key == " ") return "space";
      return key;
    }
  },
  computed: {
    toggleKey() {
      return this.keysDown.toString().replace(/,/g, "+");
    }
  },
  created() {
    if (this.$route.name === "annotate") {
      window.addEventListener("keyup", (this.onKeyup = this.onkeyup.bind(this)));
      window.addEventListener(
        "keydown",
        (this.onKeydown = this.onkeydown.bind(this))
      );
    }
  },
  destroyed() {
    window.removeEventListener("keydown", this.onKeydown);
    window.removeEventListener("keydup", this.onKeyup);
  }
};
</script>

<style scoped>
.input {
  padding: 3px;
  background-color: inherit;
  width: 100%;
  height: 100%;
  border: none;
  text-align: center;
}
.mute {
  color: gray;
  font-size: 11px;
  display: inline;
}
</style>
