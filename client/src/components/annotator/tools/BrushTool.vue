<script>
import paper from "paper";
import tool from "@/mixins/toolBar/tool";

export default {
  name: "BrushTool",
  mixins: [tool],
  props: {
    scale: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      icon: "fa-paint-brush",
      name: "Brush",
      // cursor: "none",
      scaleFactor: 3,
      brush: {
        path: null,
        pathOptions: {
          strokeColor: "white",
          strokeWidth: 1,
          sides: 40,
          minSides: 3,
          maxSides: 200,
          stepSides: 1,
          radius: 30,
          minRadius: 1,
          maxRadius: 500,
          stepRadius: 1
        }
      },
      selection: null
    };
  },
  methods: {
    removeBrush() {
      if (this.brush.path != null) {
        this.brush.path.remove();
        this.brush.path = null;
      }
    },
    removeSelection() {
      if (this.selection != null) {
        this.selection.remove();
        this.selection = null;
      }
    },
    moveBrush(point) {
      if (this.brush.path == null) this.createBrush(point);

      this.brush.path.bringToFront();
      this.brush.path.position = point;
    },
    createBrush(center) {
      let point = center || new paper.Point(0, 0);

      this.brush.path = new paper.Path.RegularPolygon({
        center: point,
        radius: this.brush.pathOptions.radius,
        sides: this.brush.pathOptions.sides,
        strokeColor: this.brush.pathOptions.strokeColor,
        strokeWidth: this.brush.pathOptions.strokeWidth
      });
    },
    createSelection(point) {
      this.selection = new paper.Path.RegularPolygon({
        center: point,
        radius: this.brush.pathOptions.radius,
        sides: this.brush.pathOptions.sides,
        strokeColor: this.brush.pathOptions.strokeColor,
        strokeWidth: this.brush.pathOptions.strokeWidth
      });
      this.selection.position = point;
    },
    onMouseMove(event) {
      this.moveBrush(event.point);
    },
    onMouseDown(event) {
      this.createSelection(event.point);
      this.draw();
    },
    onMouseUp() {
      this.merge();
      this.removeSelection();
    },
    onMouseDrag(event) {
      this.moveBrush(event.point);
      this.draw();
    },

    /**
     * Unites current brush with selection
     */
    draw() {
      let newSelection = this.selection.unite(this.brush.path);

      this.selection.remove();
      this.selection = newSelection;
    },
    /**
     * Unites current selection with selected annotation
     */
    merge() {
      this.$parent.uniteCurrentAnnotation(this.selection);
    },
    decreaseRadius() {
      if (!this.isActive) return;
      if (this.brush.pathOptions.radius > this.brush.pathOptions.minRadius ) {
        this.brush.pathOptions.radius -= this.brush.pathOptions.stepRadius;
      };
    },
    increaseRadius() {
      if (!this.isActive) return;
      if (this.brush.pathOptions.radius < this.brush.pathOptions.maxRadius) {
        this.brush.pathOptions.radius += this.brush.pathOptions.stepRadius;
      };
    },
    export() {
      return {
        sides: this.brush.pathOptions.sides,
        strokeColor: this.brush.pathOptions.strokeColor,
        radius: this.brush.pathOptions.radius
      };
    },
    setPreferences(pref) {
      this.brush.pathOptions.sides = pref.sides || this.brush.pathOptions.sides;
      this.brush.pathOptions.strokeColor =
        pref.strokeColor || this.brush.pathOptions.strokeColor;
      this.brush.pathOptions.radius =
        pref.radius || this.brush.pathOptions.radius;
    }
  },
  computed: {
    isDisabled() {
      return this.$parent.current.annotation == -1;
    }
  },
  watch: {
    "brush.pathOptions.radius"() {
      if (this.brush.path == null) return;

      let position = this.brush.path.position;
      this.brush.path.remove();
      this.createBrush(position);
    },
    "brush.pathOptions.sides"() {
      if (this.brush.path == null) return;

      let position = this.brush.path.position;
      this.brush.path.remove();
      this.createBrush(position);
    },
    "brush.pathOptions.strokeColor"(newColor) {
      if (this.brush.path == null) return;

      this.brush.path.strokeColor = newColor;
    },
    isActive(active) {
      if (this.brush.path != null) {
        this.brush.path.visible = active;
      }

      if (active) {
        this.tool.activate();
        localStorage.setItem("editorTool", this.name);
      }
    },
    /**
     * Change width of stroke based on zoom of image
     */
    scale(newScale) {
      this.brush.pathOptions.strokeWidth = newScale * this.scaleFactor;
      if (this.brush.path != null)
        this.brush.path.strokeWidth = newScale * this.scaleFactor;
    }
  },
  mounted() {}
};
</script>
