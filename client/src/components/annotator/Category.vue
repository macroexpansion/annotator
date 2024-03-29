<template>
  <div
    class="card"
    v-show="showCategory"
    :style="{
      'background-color': backgroundColor,
      'border-top': `0.5px solid ${borderColor}`,
      'border-right': `0.5px solid ${borderColor}`,
      'border-bottom': `0.5px solid ${borderColor}`,
      'border-left': `7px solid ${color}`,
      'margin-bottom': `4px`
    }"
  >
    <div class="card-header" :id="'heading' + category.id">
      <div :style="{ color: textColor }">
        <div @click="onEyeClick">
          <i
            v-if="isVisible"
            class="hover-btn fa fa-lg fa-eye category-icon"
            style="color: inherit"
            aria-hidden="true"
          />
          <i v-else style="color: inherit" class="hover-btn fa fa-lg fa-eye-slash category-icon" aria-hidden="true" />
        </div>

        <button
          class="btn btn-link btn-primary collapsed category-text"
          style="color: inherit"
          aria-expanded="false"
          :aria-controls="'collapse' + category.id"
          @click="onClick"
        >
          {{ category.name }} ({{ category.annotations.length }})
        </button>

        <!-- <i
          v-if="annotateMode === 'annotate' || editMode"
          class="fa fa-lg fa-gear category-icon"
          data-toggle="modal"
          :data-target="'#categorySettings' + category.id"
          style="float: right; color: white"
          aria-hidden="true"
        /> -->

        <i
          v-if="annotateMode === 'annotate' || editMode"
          @click="createAnnotation"
          class="fa fa-lg fa-plus category-icon"
          style="float: right; color: white; padding-right: 10px"
          aria-hidden="true"
        />
      </div>
    </div>

    <ul v-show="showAnnotations" ref="collapse" class="list-group">
      <!-- <li -->
        <!-- v-show="this.category.annotations.length > 1" -->
        <!-- class="list-group-item btn btn-link btn-sm text-left" -->
        <!-- :style="{ 'background-color': backgroundColor, color: 'white' }" -->
      <!-- > -->
        <!-- <input -->
          <!-- v-model="search" -->
          <!-- class="annotation-search" -->
          <!-- placeholder="Search" -->
        <!-- /> -->
      <!-- </li> -->

      <Annotation
        v-for="(annotation, listIndex) in category.annotations"
        :search="search"
        :key="annotation.id"
        :simplify="simplify"
        :annotation="annotation"
        :current="current.annotation"
        @click="onAnnotationClick(listIndex)"
        @keypoint-click="onKeypointClick(listIndex, $event)"
        @keypoints-complete="$emit('keypoints-complete')"
        :opacity="opacity"
        :index="listIndex"
        :keypoint-edges="keypoint.edges"
        :keypoint-labels="keypoint.labels"
        :keypoint-colors="keypoint.colors"
        ref="annotation"
        :hover="hover.annotation"
        :active-tool="activeTool"
        :scale="scale"
        @deleted="annotationDeleted"
        :all-categories="getCategoriesList"
      />
    </ul>

    <div
      class="modal fade"
      tabindex="-1"
      role="dialog"
      ref="category_settings"
      :id="'categorySettings' + category.id"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ category.name }}</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div v-show="false" class="form-group">
                <label>Supercategory</label>
                <input
                  type="text"
                  class="form-control"
                  :value="supercategory"
                  @input="supercategory = $event.target.value"
                />
              </div>

              <div class="form-group row">
                <label class="col-sm-2 col-form-label">Color</label>
                <div class="col-sm-9">
                  <input v-model="color" type="color" class="form-control" />
                </div>
              </div>

              <div v-show="false" class="form-group">
                <KeypointsDefinition
                  ref="keypoints"
                  v-model="keypoint"
                  element-id="keypointLabels"
                ></KeypointsDefinition>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-success"
              @click="onUpdateClick"
              :disabled="!isFormValid"
              :class="{ disabled: !isFormValid }"
              data-dismiss="modal"
            >
              Update
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import paper from "paper";

import Annotations from "@/models/annotations";
import Annotation from "@/components/annotator/Annotation";
import KeypointsDefinition from "@/components/KeypointsDefinition";
import JQuery from "jquery";

let $ = JQuery;

export default {
  name: "Category",
  components: { Annotation, KeypointsDefinition },
  props: {
    category: {
      type: Object,
      required: true
    },
    index: {
      type: Number,
      required: true
    },
    current: {
      type: Object,
      required: true
    },
    hover: {
      type: Object,
      required: true
    },
    opacity: {
      type: Number,
      required: true
    },
    scale: {
      type: Number,
      default: 1
    },
    categorysearch: {
      type: String,
      required: true
    },
    simplify: {
      type: Number,
      default: 1
    },
    activeTool: {
      type: String,
      required: true
    },
    allCategories: {
      type: Array,
      required: true
    }
  },
  data: function() {
    return {
      group: null,
      supercategory: this.category.supercategory,
      color: this.category.color,
      keypoint: {
        labels: [...this.category.keypoint_labels],
        edges: [...this.category.keypoint_edges],
        colors: [...this.category.keypoint_colors]
      },
      selectedAnnotation: -1,
      showAnnotations: false,
      isVisible: false,
      search: "",
      isMounted: false
    };
  },
  methods: {
    show(index) {
      if (this.search.length === 0) return true;
      return this.filterFound.indexOf(index) > -1;
    },

    resetCategorySettings() {
      this.supercategory = this.category.supercategory;
      this.color = this.category.color;
      this.keypoint = {
        labels: [...this.category.keypoint_labels],
        edges: [...this.category.keypoint_edges],
        colors: [...this.category.keypoint_colors]
      };
    },
    /**
     * Created
     */
    createAnnotation() {
      let parent = this.$parent;
      let annotationId = this.category.annotations.length;

      Annotations.create({
        image_id: parent.image.id,
        category_id: this.category.id,
        creator: this.$parent.user
      }).then(response => {
        this.$socket.emit("annotation", {
          action: "create",
          category_id: this.category.id,
          annotation: response.data
        });

        this.category.annotations.push(response.data);

        this.selectedAnnotation = annotationId;
        this.$nextTick(() => {
          this.$parent.selectLastEditorTool();
          this.$emit("click", {
            annotation: annotationId,
            category: this.index,
            keypoint: -1
          });
        });

        this.isVisible = true;
        this.showAnnotations = true;

        let annotations = this.$refs.annotation;
        if (annotations == null) return;

        let annotation = annotations[annotationId - 1];
        if (annotation == null) {
          this.$parent.scrollElement(this.$el);
        } else {
          this.$parent.scrollElement(annotation.$el);
        }
      });
    },

    onUpdateClick() {
      this.category.keypoint_labels = [...this.keypoint.labels];
      this.category.keypoint_edges = [...this.keypoint.edges];
      this.category.keypoint_colors = [...this.keypoint.colors];
      this.category.supercategory = this.supercategory;
    },
    /**
     * Exports data for send to backend
     * @returns {json} Annotation data, and settings
     */
    export() {
      let refs = this.$refs;
      let categoryData = {
        // Category Identification
        id: this.category.id,
        name: this.category.name,
        // Show in side bar
        show: this.category.show,
        // Show groups on canvas
        visualize: this.isVisible,
        color: this.color,
        metadata: [],
        annotations: [],
        supercategory: this.category.supercategory,
        // keypoint_labels: this.category.keypoint_labels,
        // keypoint_edges: this.category.keypoint_edges,
        // keypoint_colors: this.category.keypoint_colors
      };

      if (refs.hasOwnProperty("annotation")) {
        refs.annotation.forEach(annotation => {
          categoryData.annotations.push(annotation.export());
        });
      }

      return categoryData;
    },

    // addKeypointEdge(edge) {
    //   this.keypoint.edges.push(edge);
    // },

    // removeKeypointEdge(edge) {
    //   let index = this.keypoint.edges.findIndex(e => {
    //     let i1 = Math.min(edge[0], edge[1]) == Math.min(e[0], e[1]);
    //     let i2 = Math.max(edge[0], edge[1]) == Math.max(e[0], e[1]);

    //     return i1 && i2;
    //   });

    //   if (index !== -1) {
    //     let edge = this.keypoint.edges[index];
    //     this.keypoint.edges.splice(index, 1);
    //     let annotations = this.$refs.annotation;
    //     if (annotations) {
    //       annotations.forEach(a => a.keypoints.removeLine(edge));
    //     }
    //   }
    // },

    /**
     * Event handler for visibility button
     */
    onEyeClick() {
      this.isVisible = !this.isVisible;

      if (this.showAnnotations && !this.isVisible) {
        this.showAnnotations = false;
      }

      if (this.showAnnotations)
        if (this.isCurrent) {
          this.$emit("click", {
            annotation: this.selectedAnnotation,
            category: this.index,
            keypoint: -1
          });
        }
    },
    /**
     * Event handler for keypoint click
     */
    onKeypointClick(annotation_index, keypoint_index) {
      let indices = {
        annotation: annotation_index,
        category: this.index,
        keypoint: keypoint_index
      };
      this.selectedAnnotation = annotation_index;
      this.showAnnotations = true;

      this.$emit("click", indices);
    },
    /**
     * Event handler for annotation click
     */
    onAnnotationClick(index) {
      let indices = {
        annotation: index,
        category: this.index,
        keypoint: -1
      };
      this.selectedAnnotation = index;
      this.showAnnotations = true;

      this.$emit("click", indices);
    },
    /**
     * Event Handler for category click
     */
    onClick() {
      let indices = {
        annotation: this.selectedAnnotation,
        category: this.index,
        keypoint: -1
      };
      this.$emit("click", indices);

      if (this.category.annotations.length === 0) return;
      this.showAnnotations = !this.showAnnotations;

      if (this.showAnnotations && !this.isVisible) {
        this.isVisible = true;
      }
    },
    /**
     * Creates paperjs group
     */
    initCategory() {
      this.setColor();
    },
    /**
     * @returns {Annotation} returns annotation and provided index
     */
    getAnnotation(index) {
      let ref = this.$refs.annotation;
      if (ref == null) return null;
      return this.$refs.annotation[index];
    },
    /**
     * Sets color of current group depending on state.
     * Show annotation colors if showAnnotations is true,
     * Show as group color if showAnnotations is false
     */
    setColor() {
      let annotations = this.$refs.annotation;
      if (annotations == null) return;
      if (!this.isVisible) return;

      if (this.showAnnotations) {
        annotations.forEach(a => a.setColor());
      } else {
        annotations.forEach(a => {
          a.compoundPath.fillColor = this.color;
          a.keypoints.color = this.darkHSL;
          a.keypoints.bringToFront();
        });
      }
    },
    annotationDeleted(index) {
      if (this.selectedAnnotation >= index) {
        this.selectedAnnotation--;
      }

      let indices = {
        annotation: this.selectedAnnotation,
        category: this.index,
        keypoint: -1
      };
      this.$emit("click", indices);

      if (this.category.annotations.length === 0) this.isVisible = false;
    }
  },
  computed: {
    showCategory() {
      let search = this.categorysearch.toLowerCase();
      if (search.length === 0) return true;
      return this.category.name.toLowerCase().includes(search);
    },
    getCategoriesList() {
      return this.allCategories.map(category => ({
        value: category.id,
        text: category.name
      }));
    },
    isCurrent() {
      return this.current.category === this.index;
    },
    isHover() {
      return this.hover.category === this.index;
    },
    backgroundColor() {
      if (this.isHover && !this.showAnnotations) {
        return "#646c82";
      }
      return "inherit";
    },
    borderColor() {
      if (this.isCurrent) return this.color;
      return "#404552";
    },
    darkHSL() {
      let color = new paper.Color(this.color);
      let h = Math.round(color.hue);
      let l = Math.round(color.lightness * 50);
      let s = Math.round(color.saturation * 100);
      return "hsl(" + h + "," + s + "%," + l + "%)";
    },
    isFormValid() {
      return (
        this.isMounted &&
        this.$refs &&
        this.$refs.keypoints &&
        this.$refs.keypoints.valid
      );
    },
    annotateMode() {
      return this.$store.getters['review/annotateMode'];
    },
    editMode() {
      return this.$parent.edit;
    },
    textColor() {
      if (this.annotateMode === 'annotate' || this.editMode)
        return 'white';
      else
        return 'darkgray';
    }
  },
  watch: {
    color() {
      this.setColor();
    },
    opacity() {
      let annotations = this.$refs.annotation;
      if (annotations == null) return;

      annotations.forEach(a => (a.compoundPath.opacity = this.opacity));
    },
    isVisible(newVisible) {
      let annotations = this.$refs.annotation;
      if (annotations == null) return;

      annotations.forEach(a => {
        a.keypoints.visible = newVisible;
        a.isVisible = newVisible;
      });
      this.setColor();
    },
    showAnnotations(showing) {
      if (!showing) {
        this.$emit("click", {
          annotation: -1,
          keypoint: -1,
          category: this.index
        });
      }
      this.setColor();
    },
    category() {
      this.initCategory();
    }
  },
  sockets: {
    annotation(data) {
      let action = data.action;
      let annotation = data.annotation;

      if (annotation.image_id != this.$parent.image.id) return;
      if (annotation.category_id != this.category.id) return;

      let found = this.category.annotations.findIndex(
        a => a.id == annotation.id
      );

      if (found == -1) {
        if (action == "create") {
          this.category.annotations.push(annotation);
        }
      }
    }
  },
  mounted() {
    this.initCategory();
    $(this.$refs.category_settings).on(
      "hidden.bs.modal",
      this.resetCategorySettings
    );
    this.isMounted = true;
  }
};
</script>

<style scoped>
.list-group-item {
  height: 44px;
  font-size: 13px;
  padding: 3px;
  /* background-color: #4b5162; */
  /* background-color: white; */
}

.category-icon {
  display: block;
  float: left;
  margin: 0;
  padding: 5px 10px 5px 10px;
}

.btn-link {
  margin: 0;
  padding: 0;
}

.annotation-icon {
  margin: 0;
  padding: 3px;
}

.card-header {
  display: block;
  margin: 0;
  padding: 0;
}

.card {
  background-color: #404552;
}

.btn-primary {
  border: none;
  background-color: inherit;
}

.annotation-search {
  width: 100%;
  height: 18px;
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  border: none;
  text-align: center;
  border-radius: 4px;
}

.hover-btn {
  cursor: pointer;
}

::-webkit-input-placeholder {
  /* WebKit, Blink, Edge */
  color: lightgray;
}
:-moz-placeholder {
  /* Mozilla Firefox 4 to 18 */
  color: lightgray;
  opacity: 1;
}
::-moz-placeholder {
  /* Mozilla Firefox 19+ */
  color: lightgray;
  opacity: 1;
}
:-ms-input-placeholder {
  /* Internet Explorer 10-11 */
  color: lightgray;
}
::-ms-input-placeholder {
  /* Microsoft Edge */
  color: lightgray;
}
::placeholder {
  /* Most modern browsers support this now. */
  color: lightgray;
}
</style>
