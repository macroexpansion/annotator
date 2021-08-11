<template>
  <div
    style="
       {
        display: block;
        height: inherit;
      }
    "
  >
    <!-- Left Panel -->
    <aside v-show="panels.show.left" class="left-panel">
      <div>
        <hr />
        <SelectTool
          v-model="activeTool"
          :scale="image.scale"
          @setcursor="setCursor"
          ref="select"
        />

        <div v-show="annotateMode === 'annotate' || edit">
          <hr class="hr-line" />
          <BBoxTool
            v-model="activeTool"
            :scale="image.scale"
            @setcursor="setCursor"
            ref="bbox"
          />

          <PolygonTool
            v-model="activeTool"
            :scale="image.scale"
            @setcursor="setCursor"
            ref="polygon"
          />

          <BrushTool
            v-model="activeTool"
            :scale="image.scale"
            @setcursor="setCursor"
            ref="brush"
          />

          <EraserTool
            v-model="activeTool"
            :scale="image.scale"
            @setcursor="setCursor"
            ref="eraser"
          />
        </div>
      </div>

      <hr class="hr-line" />
      <SaveButton />
      <hr class="hr-line" />
      <UndoButton />
      <!-- <hr class="hr-line"/>
      <DownloadButton :image="image" /> -->
      <hr class="hr-line" />
      <SettingsButton
        :metadata="image.metadata"
        :commands="commands"
        ref="settings"
      />
    </aside>

    <!-- Right Panel -->
    <aside v-show="panels.show.right" class="right-panel">
      <hr />
      <FileTitle
        :previousimage="image.previous"
        :nextimage="image.next"
        :filename="image.filename"
        ref="filetitle"
      />

      <div v-if="categories.length > 5">
        <div style="padding: 0px 5px">
          <input
            v-model="search"
            class="search"
            placeholder="Category Search"
          />
        </div>
      </div>

      <div
        class="sidebar-section"
        :style="{ 'max-height': annotateMode === 'annotate' ? '87%' : '75%' }"
      >
        <p
          v-if="categories.length == 0"
          style="color: lightgray; font-size: 12px"
        >
          No categories have been enabled for this image.
        </p>

        <div
          v-if="segmentCategories.length > 0"
          style="overflow: auto; max-height: 100%"
        >
          <hr />
          <p style="color: white">Segmentation</p>
          <Category
            v-for="(category, index) in segmentCategories"
            :key="category.id + '-category'"
            :simplify="simplify"
            :categorysearch="search"
            :category="category"
            :all-categories="categories"
            :opacity="shapeOpacity"
            :hover="hover"
            :index="index"
            @click="onCategoryClick"
            @keypoints-complete="onKeypointsComplete"
            :current="current"
            :active-tool="activeTool"
            :scale="image.scale"
            ref="segmentCategory"
          />
        </div>

        <div
          v-if="classifyCategories.length > 0"
          style="overflow: auto; max-height: 100%"
        >
          <div v-for="(group, idx) in categoryGroup" :key="idx">
            <hr />
            <p style="color: white">{{ group }}</p>
            <ClassificationLabel
              v-for="category in classifyCategoriesEachGroup(group)"
              v-model="image.categoryIds"
              :key="category.id + '-label'"
              :category="category"
              :search="search"
              ref="classifyCategory"
            />
          </div>
        </div>
      </div>

      <div
        v-if="
          annotateMode === 'review' &&
          !edit &&
          classifyCategories.length + segmentCategories.length > 0
        "
        style="margin-top: 20%"
      >
        <button
          type="button"
          class="btn btn-success btn-custom text-nowrap"
          style="margin-right: 6px"
          @click="acceptAnnotation"
        >
          <i class="fa fa-check" aria-hidden="true"></i>
        </button>
        <button
          type="button"
          class="btn btn-primary btn-custom text-nowrap"
          @click="editAnnotation"
        >
          <i class="fa fa-pencil" aria-hidden="true"></i>
        </button>
      </div>

      <div v-if="annotateMode === 'review' && edit" style="margin-top: 20%">
        <button
          type="button"
          class="btn btn-success btn-custom text-nowrap"
          style="margin-right: 6px"
          @click="saveAnnotation"
        >
          <i class="fa fa-floppy-o" aria-hidden="true"></i></button
        ><button
          type="button"
          class="btn btn-danger btn-custom text-nowrap"
          @click="cancelAnnotation"
        >
          <i class="fa fa-times" aria-hidden="true"></i>
        </button>
      </div>
    </aside>

    <!-- Top Panel -->
    <div class="top-panel">
      <nav class="navbar navbar-dark">
        <!-- <BBoxPanel :bbox="$refs.bbox" /> -->
        <PolygonPanel :polygon="$refs.polygon" v-if="$refs.polygon" />
        <!-- <SelectPanel :select="$refs.select" /> -->
        <BrushPanel :brush="$refs.brush" v-if="$refs.brush" />
        <EraserPanel :eraser="$refs.eraser" v-if="$refs.eraser" />
      </nav>
    </div>

    <!--  Middle Panel -->
    <div class="middle-panel" :style="{ cursor: cursor }">
      <v-touch @pinch="onpinch" @pinchstart="onpinchstart">
        <div id="frame" class="frame" @wheel="onwheel">
          <canvas class="canvas" id="editor" ref="image" resize />
        </div>
      </v-touch>
    </div>

    <div
      v-show="annotating.length > 0"
      class="fixed-bottom alert alert-warning alert-dismissible fade show"
    >
      <span>
        This image is being annotated by <b>{{ annotating.join(", ") }}</b
        >.
      </span>

      <button
        type="button"
        class="close"
        data-dismiss="alert"
        aria-label="Close"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  </div>
</template>

<script>
import paper from "paper";
import axios from "axios";

import toastrs from "@/mixins/toastrs";
import shortcuts from "@/mixins/shortcuts";

import FileTitle from "@/components/annotator/FileTitle";
import Category from "@/components/annotator/Category";
import Label from "@/components/annotator/Label";

import Annotations from "@/models/annotations";

import PolygonTool from "@/components/annotator/tools/PolygonTool";
import BBoxTool from "@/components/annotator/tools/BBoxTool";
import SelectTool from "@/components/annotator/tools/SelectTool";
import MagicWandTool from "@/components/annotator/tools/MagicWandTool";
import EraserTool from "@/components/annotator/tools/EraserTool";
import BrushTool from "@/components/annotator/tools/BrushTool";
import KeypointTool from "@/components/annotator/tools/KeypointTool";
import DEXTRTool from "@/components/annotator/tools/DEXTRTool";

// import CopyAnnotationsButton from "@/components/annotator/tools/CopyAnnotationsButton";
import CenterButton from "@/components/annotator/tools/CenterButton";
// import DownloadButton from "@/components/annotator/tools/DownloadButton";
import SaveButton from "@/components/annotator/tools/SaveButton";
import SettingsButton from "@/components/annotator/tools/SettingsButton";
import ModeButton from "@/components/annotator/tools/ModeButton";
import DeleteButton from "@/components/annotator/tools/DeleteButton";
import UndoButton from "@/components/annotator/tools/UndoButton";
import ShowAllButton from "@/components/annotator/tools/ShowAllButton";
import HideAllButton from "@/components/annotator/tools/HideAllButton";
// import AnnotateButton from "@/components/annotator/tools/AnnotateButton";

import PolygonPanel from "@/components/annotator/panels/PolygonPanel";
import BBoxPanel from "@/components/annotator/panels/BBoxPanel";
import SelectPanel from "@/components/annotator/panels/SelectPanel";
import MagicWandPanel from "@/components/annotator/panels/MagicWandPanel";
import BrushPanel from "@/components/annotator/panels/BrushPanel";
import EraserPanel from "@/components/annotator/panels/EraserPanel";
import KeypointPanel from "@/components/annotator/panels/KeypointPanel";
import DEXTRPanel from "@/components/annotator/panels/DEXTRPanel";

import { mapMutations } from "vuex";

export default {
  name: "Annotator",
  components: {
    FileTitle,
    // CopyAnnotationsButton,
    Category,
    ClassificationLabel: Label,
    BBoxTool,
    BBoxPanel,
    PolygonTool,
    PolygonPanel,
    SelectTool,
    MagicWandTool,
    EraserTool,
    BrushTool,
    KeypointTool,
    // DownloadButton,
    SaveButton,
    SettingsButton,
    DeleteButton,
    CenterButton,
    SelectPanel,
    MagicWandPanel,
    BrushPanel,
    EraserPanel,
    ModeButton,
    UndoButton,
    HideAllButton,
    ShowAllButton,
    KeypointPanel,
    // AnnotateButton,
    DEXTRTool,
    DEXTRPanel,
  },
  mixins: [toastrs, shortcuts],
  props: {
    identifier: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      activeTool: "Select",
      lastTool: "Select",
      paper: null,
      shapeOpacity: 0.6,
      zoom: 0.2,
      cursor: "move",
      simplify: 1,
      panels: {
        show: {
          left: true,
          right: true,
        },
      },
      current: {
        category: -1,
        annotation: -1,
        keypoint: -1,
      },
      hover: {
        category: -1,
        annotation: -1,
        keypoint: -1,
      },
      image: {
        raster: {},
        scale: 0,
        metadata: {},
        ratio: 0,
        rotate: 0,
        id: null,
        url: "",
        dataset: 0,
        previous: null,
        next: null,
        filename: "",
        path: "",
        categoryIds: [],
        data: null,
      },
      text: {
        topLeft: null,
        topRight: null,
      },
      categories: [],
      dataset: {
        annotate_url: "",
      },
      loading: {
        image: true,
        data: true,
        loader: null,
      },
      search: "",
      annotating: [],
      pinching: {
        old_zoom: 1,
      },
      edit: false,
    };
  },
  methods: {
    ...mapMutations([
      "addProcess",
      "removeProcess",
      "resetUndo",
      "setDataset",
      "setFolders",
    ]),
    ...mapMutations("review", ["setAnnotateMode"]),

    save(callback) {
      let process = "Saving";
      this.addProcess(process);
      let refs = this.$refs;

      let data = {
        mode: this.annotateMode,
        reviewuser: this.user,
        user: {
          bbox: this.$refs.bbox.export(),
          polygon: this.$refs.polygon.export(),
          eraser: this.$refs.eraser.export(),
          brush: this.$refs.brush.export(),
          select: this.$refs.select.export(),
          settings: this.$refs.settings.export(),
        },
        dataset: this.dataset,
        image: {
          id: this.image.id,
          metadata: this.$refs.settings.exportMetadata(),
          settings: {
            selectedLayers: this.current,
          },
          category_ids: [],
        },
        settings: {
          activeTool: this.activeTool,
          zoom: this.zoom,
          tools: {},
        },
        categories: [],
      };

      if (refs.segmentCategory != null) {
        refs.segmentCategory.forEach((category) => {
          let categoryData = category.export();
          data.categories.push(categoryData);

          if (categoryData.annotations.length > 0) {
            let categoryIds = this.image.categoryIds;
            if (categoryIds.indexOf(categoryData.id) === -1)
              categoryIds.push(categoryData.id);
          } else {
            if (this.image.categoryIds.includes(categoryData.id)) {
              this.image.categoryIds.splice(
                this.image.categoryIds.indexOf(categoryData.id),
                1
              );
            }
          }
        });
      }

      if (refs.classifyCategory != null) {
        refs.classifyCategory.forEach((category) => {
          let categoryData = category.export();
          if (categoryData.annotations[0].id)
            data.categories.push(categoryData);
        });
      }

      data.image.category_ids = this.image.categoryIds;

      axios
        .post("/tagging/api/annotator/data", JSON.stringify(data))
        .then(() => {
          // TODO: updateUser
          if (callback != null) callback();
        })
        .finally(() => this.removeProcess(process));
    },

    acceptAnnotation() {
      if (this.image.next !== null) this.$refs.filetitle.route(this.image.next);

      if (this.image.next === null)
        this.$router.push({
          path: `/dataset/${this.dataset.id}`,
        });
    },
    editAnnotation() {
      // console.log(this.categoryGroup);
      this.edit = true;
    },

    saveAnnotation() {
      this.save(() => {
        this.edit = false;
      });
    },
    cancelAnnotation() {
      this.edit = false;
      this.activeTool = "Select";
      this.getData();
    },

    onpinchstart(e) {
      e.preventDefault();
      if (!this.doneLoading) return;
      let view = this.paper.view;
      this.pinching.old_zoom = this.paper.view.zoom;
      return false;
    },

    onpinch(e) {
      e.preventDefault();
      if (!this.doneLoading) return;
      let view = this.paper.view;
      let viewPosition = view.viewToProject(
        new paper.Point(e.center.x, e.center.y)
      );
      let curr_zoom = e.scale * this.pinching.old_zoom;
      let beta = this.paper.view.zoom / curr_zoom;
      let pc = viewPosition.subtract(this.paper.view.center);
      let a = viewPosition
        .subtract(pc.multiply(beta))
        .subtract(this.paper.view.center);
      let transform = { zoom: curr_zoom, offset: a };
      if (transform.zoom < 10 && transform.zoom > 0.01) {
        this.image.scale = 1 / transform.zoom;
        this.paper.view.zoom = transform.zoom;
        this.paper.view.center = view.center.add(transform.offset);
      }
      return false;
    },

    onwheel(e) {
      e.preventDefault();
      if (!this.doneLoading) return;

      let view = this.paper.view;

      if (e.ctrlKey) {
        // Pan up and down
        let delta = new paper.Point(0, 0.5 * e.deltaY);
        this.paper.view.setCenter(view.center.add(delta));
      } else if (e.shiftKey) {
        // Pan left and right
        let delta = new paper.Point(0.5 * e.deltaY, 0);
        this.paper.view.setCenter(view.center.add(delta));
      } else {
        let viewPosition = view.viewToProject(
          new paper.Point(e.offsetX, e.offsetY)
        );

        let transform = this.changeZoom(e.deltaY, viewPosition);
        if (transform.zoom < 10 && transform.zoom > 0.01) {
          this.image.scale = 1 / transform.zoom;
          this.paper.view.zoom = transform.zoom;
          this.paper.view.center = view.center.add(transform.offset);
        }
      }

      return false;
    },

    fit() {
      const canvas = document.getElementById("editor");

      const parentX = this.image.raster.width;
      const parentY = this.image.raster.height;

      this.paper.view.zoom = Math.min(
        (canvas.width / parentX) * 0.95,
        (canvas.height / parentY) * 0.8
      );

      this.image.scale = 1 / this.paper.view.zoom;
      this.paper.view.setCenter(0, 0);
    },

    changeZoom(delta, p) {
      const oldZoom = this.paper.view.zoom;
      const center = this.paper.view.center;
      const factor = 1 + this.zoom;

      const zoom = delta < 0 ? oldZoom * factor : oldZoom / factor;
      const beta = oldZoom / zoom;
      const pc = p.subtract(center);
      const offset = p.subtract(pc.multiply(beta)).subtract(center);

      return { zoom: zoom, offset: offset };
    },

    initCanvas() {
      const process = "Initializing canvas";
      this.addProcess(process);
      this.loading.image = true;

      const canvas = document.getElementById("editor");
      this.paper.setup(canvas);
      this.paper.view.viewSize = [
        this.paper.view.size.width,
        window.innerHeight,
      ];
      this.paper.activate();

      this.image.raster = new paper.Raster(this.image.url);
      this.image.raster.onLoad = () => {
        const width = this.image.raster.width;
        const height = this.image.raster.height;

        this.image.raster.sendToBack();
        this.fit();
        this.image.ratio = (width * height) / 1000000;
        this.removeProcess(process);

        const tempCtx = document.createElement("canvas").getContext("2d");
        tempCtx.canvas.width = width;
        tempCtx.canvas.height = height;
        tempCtx.drawImage(this.image.raster.image, 0, 0);

        this.image.data = tempCtx.getImageData(0, 0, width, height);
        const fontSize = (width + height) * 0.01;

        const positionTopLeft = new paper.Point(
          -width / 2,
          -height / 1.9 - fontSize * 0.5
        );
        this.text.topLeft = new paper.PointText(positionTopLeft);
        this.text.topLeft.fontSize = fontSize;
        this.text.topLeft.fillColor = "white";
        this.text.topLeft.content = this.image.filename;

        const positionTopRight = new paper.Point(
          width / 2,
          -height / 2 - fontSize * 0.4
        );
        this.text.topRight = new paper.PointText(positionTopRight);
        this.text.topRight.justification = "right";
        this.text.topRight.fontSize = fontSize;
        this.text.topRight.fillColor = "white";
        this.text.topRight.content = width + "x" + height;

        this.loading.image = false;
      };
    },

    setPreferences(preferences) {
      let refs = this.$refs;

      refs.bbox.setPreferences(preferences.bbox || preferences.polygon || {});
      refs.polygon.setPreferences(preferences.polygon || {});
      refs.select.setPreferences(preferences.select || {});
      // refs.magicwand.setPreferences(preferences.magicwand || {});
      refs.brush.setPreferences(preferences.brush || {});
      refs.eraser.setPreferences(preferences.eraser || {});
    },

    getData(callback) {
      let process = "Loading annotation data";
      this.addProcess(process);
      this.loading.data = true;

      axios
        .get(`/tagging/api/annotator/data/${this.image.id}`, {
          params: {
            user: this.user,
            order: this.order,
            mode: this.annotateMode,
            folder: this.$store.state.folders.join("/"),
          },
        })
        .then((response) => {
          this.loading.data = false;

          // Set image data
          this.image.path = response.data.image.path;
          this.image.metadata = response.data.image.metadata || {};
          this.image.filename = response.data.image.file_name;
          this.image.next = response.data.image.next;
          this.image.previous = response.data.image.previous;
          this.image.categoryIds =
            response.data.image.user_category_ids[this.user] || [];
          this.annotating = response.data.image.annotating || [];

          // Set other data
          this.dataset = response.data.dataset;
          this.categories = response.data.categories;

          // Update status
          this.setDataset(this.dataset);

          let preferences = response.data.preferences;
          this.setPreferences(preferences);

          if (this.text.topLeft != null && (this.isVtcc || this.isAdmin)) {
            const split = this.image.path.split("/").map((item) => item.trim());
            const path =
              split.length > 2
                ? split.splice(2, split.length - 3).join(" / ")
                : "\n";
            this.text.topLeft.content = `${path}\n${this.image.filename}`;
          }

          this.$nextTick(() => {
            this.showAll();
          });

          if (callback != null) callback();
        })
        .catch(() => {
          this.axiosRequestError(
            "Could not find requested image",
            "Redirecting to previous page."
          );
          this.$router.go(-1);
        })
        .finally(() => this.removeProcess(process));
    },

    onCategoryClick(indices) {
      this.current.annotation = indices.annotation;
      this.current.category = indices.category;
      if (!indices.hasOwnProperty("keypoint")) {
        indices.keypoint = -1;
      }
      if (indices.keypoint !== -1) {
        this.current.keypoint = indices.keypoint;
        let ann = this.currentCategory.category.annotations[
          this.current.annotation
        ];
        let kpTool = this.$refs.keypoint;
        let selectTool = this.$refs.select;
        let category = this.$refs.segmentCategory[this.current.category];
        let annotation = category.$refs.annotation[this.current.annotation];
        annotation.showKeypoints = true;
        let keypoints = annotation.keypoints;
        if (keypoints._labelled[indices.keypoint + 1]) {
          let indexLabel = String(this.current.keypoint + 1);
          let keypoint = keypoints._labelled[indexLabel];
          keypoint.selected = true;
          this.activeTool = selectTool;
          this.activeTool.click();
        } else {
          this.currentAnnotation.keypoint.next.label = String(
            indices.keypoint + 1
          );
          this.activeTool = kpTool;
          this.activeTool.click();
        }
      }
    },

    onKeypointsComplete() {
      this.currentAnnotation.keypoint.next.label = -1;
      this.activeTool = this.$refs.select;
      this.activeTool.click();
    },

    switchToSelectTool() {
      this.lastTool = this.activeTool;
      this.activeTool = this.$refs.select;
      this.activeTool.click();
    },

    getCategory(index) {
      if (index == null) return null;
      if (index < 0) return null;

      let ref = this.$refs.segmentCategory;

      if (ref == null) return null;
      if (ref.length < 1 || index >= ref.length) return null;

      return this.$refs.segmentCategory[index];
    },

    // Current Annotation Operations
    uniteCurrentAnnotation(
      compound,
      simplify = true,
      undoable = true,
      isBBox = false
    ) {
      if (this.currentAnnotation == null) return;
      this.currentAnnotation.unite(compound, simplify, undoable, isBBox);
    },

    subtractCurrentAnnotation(compound, simplify = true, undoable = true) {
      if (this.currentCategory == null) return;
      this.currentAnnotation.subtract(compound, simplify, undoable);
    },

    selectLastEditorTool() {
      this.activeTool = localStorage.getItem("editorTool") || "Select";
    },

    setCursor(newCursor) {
      this.cursor = newCursor;
    },

    incrementCategory() {
      if (this.current.category >= this.categories.length - 1) {
        this.current.category = -1;
      } else {
        this.current.category += 1;
        if (this.currentKeypoint) {
          this.currentAnnotation.onAnnotationKeypointClick(
            this.current.keypoint
          );
        }
      }
    },

    decrementCategory() {
      if (this.current.category === -1) {
        this.current.category = this.categories.length - 1;
        let annotationCount = this.currentCategory.category.annotations.length;
        if (annotationCount > 0) {
          this.current.annotation = annotationCount - 1;
        }
      } else {
        this.current.category -= 1;
      }
    },

    incrementAnnotation() {
      let annotationCount = this.currentCategory.category.annotations.length;
      if (this.current.annotation === annotationCount - 1) {
        this.incrementCategory();
        this.current.annotation = -1;
      } else {
        this.current.annotation += 1;
        if (
          this.currentAnnotation != null &&
          this.currentAnnotation.showKeypoints
        ) {
          this.current.keypoint = 0;
          this.currentAnnotation.onAnnotationKeypointClick(
            this.current.keypoint
          );
        } else {
          this.current.keypoint = -1;
        }
      }
    },

    decrementAnnotation() {
      let annotationCount = this.currentCategory.category.annotations.length;
      if (this.current.annotation === -1) {
        this.current.annotation = annotationCount - 1;
      } else if (this.current.annotation === 0) {
        this.decrementCategory();
      } else {
        this.current.annotation -= 1;
        if (
          this.currentAnnotation != null &&
          this.currentAnnotation.showKeypoints
        ) {
          this.current.keypoint =
            this.currentAnnotation.keypointLabels.length - 1;
          this.currentAnnotation.onAnnotationKeypointClick(
            this.current.keypoint
          );
        } else {
          this.current.keypoint = -1;
        }
      }
    },

    incrementKeypoint() {
      let keypointCount = this.currentAnnotation.keypointLabels.length;
      if (this.current.keypoint === keypointCount - 1) {
        this.incrementAnnotation();
      } else {
        this.current.keypoint += 1;
      }
      if (this.currentKeypoint != null) {
        this.currentAnnotation.onAnnotationKeypointClick(this.current.keypoint);
        // this.currentAnnotation.$emit("keypoint-click", this.current.keypoint);
      }
    },

    decrementKeypoint() {
      if (this.current.keypoint === 0) {
        this.decrementAnnotation();
      } else {
        this.current.keypoint -= 1;
      }
      if (this.currentKeypoint != null) {
        this.currentAnnotation.onAnnotationKeypointClick(this.current.keypoint);
        // this.currentAnnotation.$emit("keypoint-click", this.current.keypoint);
      }
    },

    moveUp() {
      if (this.currentCategory != null) {
        if (this.currentAnnotation != null) {
          if (this.currentKeypoint != null) {
            this.decrementKeypoint();
          } else if (
            this.currentAnnotation.showKeypoints &&
            this.current.keypoint == -1
          ) {
            this.decrementKeypoint();
          } else {
            this.decrementAnnotation();
          }
        } else if (this.current.annotation == -1) {
          this.decrementAnnotation();
        } else {
          this.decrementCategory();
        }
      } else {
        this.decrementCategory();
      }
    },

    moveDown() {
      if (this.currentCategory != null) {
        if (this.currentAnnotation != null) {
          if (this.currentKeypoint != null) {
            this.incrementKeypoint();
          } else if (
            this.currentAnnotation.showKeypoints &&
            this.current.keypoint == -1
          ) {
            this.incrementKeypoint();
          } else {
            this.incrementAnnotation();
          }
        } else if (this.current.annotation == -1) {
          this.incrementAnnotation();
        } else {
          this.incrementCategory();
        }
      } else {
        this.incrementCategory();
      }
    },

    stepIn() {
      if (this.currentCategory != null) {
        if (!this.currentCategory.isVisible) {
          this.currentCategory.isVisible = true;
          this.current.annotation = 0;
          this.currentAnnotation.showKeypoints = false;
          this.current.keypoint = -1;
        } else if (
          !this.currentCategory.showAnnotations &&
          this.currentAnnotationLength > 0
        ) {
          this.currentCategory.showAnnotations = true;
          this.current.annotation = 0;
          this.currentAnnotation.showKeypoints = false;
          this.current.keypoint = -1;
        } else if (
          !this.currentAnnotation.showKeypoints &&
          this.currentAnnotation.keypointLabels.length > 0
        ) {
          this.currentAnnotation.showKeypoints = true;
          this.current.keypoint = 0;
          this.currentAnnotation.onAnnotationKeypointClick(
            this.current.keypoint
          );
        }
      }
    },

    stepOut() {
      if (this.currentCategory != null) {
        if (
          this.currentAnnotation != null &&
          this.currentAnnotation.showKeypoints
        ) {
          this.currentAnnotation.showKeypoints = false;
          this.current.keypoint = -1;
        } else if (this.currentCategory.showAnnotations) {
          this.currentCategory.showAnnotations = false;
          this.current.annotation = -1;
        } else if (this.currentCategory.isVisible) {
          this.currentCategory.isVisible = false;
        }
      }
    },

    scrollElement(element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    },

    showAll() {
      if (this.$refs.segmentCategory == null) return;

      this.$refs.segmentCategory.forEach((category) => {
        category.isVisible = category.category.annotations.length > 0;
      });
    },

    hideAll() {
      if (this.$refs.segmentCategory == null) return;

      this.$refs.segmentCategory.forEach((category) => {
        category.isVisible = false;
        category.showAnnotations = false;
      });
    },

    findCategoryByName(categoryName) {
      let categoryComponent = this.$refs.segmentCategory.find(
        (category) =>
          category.category.name.toLowerCase() === categoryName.toLowerCase()
      );
      if (!categoryComponent) return null;
      return categoryComponent.category;
    },

    addAnnotation(categoryName, segments, keypoints, isbbox = false) {
      segments = segments || [];
      keypoints = keypoints || [];

      if (keypoints.length == 0 && segments.length == 0) return;

      let category = this.findCategoryByName(categoryName);
      if (category == null) return;

      Annotations.create({
        image_id: this.image.id,
        category_id: category.id,
        segmentation: segments,
        keypoints: keypoints,
        isbbox: isbbox,
        creator: this.user,
      }).then((response) => {
        let annotation = response.data;
        category.annotations.push(annotation);
      });
    },

    updateAnnotationCategory(annotation, oldCategory, newCategoryName) {
      let newCategory = this.findCategoryByName(newCategoryName);
      if (!newCategory || !annotation) return;

      Annotations.update(annotation.id, { category_id: newCategory.id }).then(
        (response) => {
          let newAnnotation = {
            ...response.data,
            ...annotation,
            metadata: response.data.metadata,
            category_id: newCategory.id,
          };

          if (newAnnotation) {
            oldCategory.annotations = oldCategory.annotations.filter(
              (a) => a.id !== annotation.id
            );
            newCategory.annotations.push(newAnnotation);
          }
        }
      );
    },

    removeFromAnnotatingList() {
      if (this.annotatingUser == null) return;

      var index = this.annotating.indexOf(this.annotatingUser.username);
      //Remove self from list
      if (index > -1) {
        this.annotating.splice(index, 1);
      }
    },

    nextImage() {
      if (this.image.next != null) this.$refs.filetitle.route(this.image.next);
    },

    previousImage() {
      if (this.image.previous != null)
        this.$refs.filetitle.route(this.image.previous);
    },

    classifyCategoriesEachGroup(group) {
      return this.classifyCategories.filter(
        (category) => category.group === group
      );
    },
  },
  watch: {
    doneLoading(done) {
      if (done) {
        if (this.loading.loader) {
          this.loading.loader.hide();
        }
      }
    },
    currentCategory() {
      if (this.currentCategory != null) {
        if (
          this.currentAnnotation == null ||
          !this.currentCategory.showAnnotations
        ) {
          let element = this.currentCategory.$el;
          this.scrollElement(element);
        }
      }
    },
    currentAnnotation(newElement) {
      if (newElement != null) {
        if (newElement.showAnnotations) {
          let element = newElement.$el;
          this.scrollElement(element);
        }
      }
    },
    "current.category"(cc) {
      if (cc < -1) this.current.category = -1;
      let max = this.categories.length;
      if (cc > max) {
        this.current.category = -1;
      }
    },
    "current.annotation"(ca) {
      if (ca < -1) this.current.annotation = -1;
      if (this.currentCategory != null) {
        let max = this.currentAnnotationLength;
        if (ca > max) {
          this.current.annotations = -1;
        }
      }
    },
    "current.keypoint"(sk) {
      if (sk < -1) this.current.keypoint = -1;
      if (this.currentCategory != null) {
        let max = this.currentAnnotationLength;
        if (sk > max) {
          this.current.keypoint = -1;
        }
      }
    },
    annotating() {
      this.removeFromAnnotatingList();
    },
    annotatingUser() {
      this.removeFromAnnotatingList();
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    isVtcc() {
      return this.$store.getters["user/isVtcc"];
    },
    order() {
      return localStorage.getItem("dataset/order");
    },
    doneLoading() {
      return !this.loading.image && !this.loading.data;
    },
    currentAnnotationLength() {
      if (this.currentCategory == null) return null;
      return this.currentCategory.category.annotations.length;
    },
    currentKeypointLength() {
      if (this.currentAnnotation == null) return null;
      return this.currentAnnotation.annotation.keypoints.length;
    },
    currentCategory() {
      return this.getCategory(this.current.category);
    },
    currentAnnotation() {
      if (this.currentCategory == null) {
        return null;
      }
      return this.currentCategory.getAnnotation(this.current.annotation);
    },
    currentKeypoint() {
      if (this.currentCategory == null) {
        return null;
      }
      if (
        this.currentAnnotation == null ||
        this.currentAnnotation.keypointLabels.length === 0 ||
        !this.currentAnnotation.showKeypoints
      ) {
        return null;
      }
      if (this.current.keypoint == -1) {
        return null;
      }
      return {
        label: [String(this.current.keypoint + 1)],
        visibility: this.currentAnnotation.getKeypointVisibility(
          this.current.keypoint
        ),
      };
    },
    annotatingUser() {
      return this.$store.getters["user/user"];
    },
    reviewUser() {
      return this.$store.getters["review/reviewUser"];
    },
    annotateMode() {
      return this.$store.getters["review/annotateMode"];
    },
    user() {
      if (this.annotateMode === "review") return this.reviewUser;
      return this.$store.getters["user/username"];
    },
    segmentCategories() {
      return this.categories.filter((category) => !category.classified);
    },
    classifyCategories() {
      return this.categories.filter((category) => category.classified);
    },
    categoryGroup() {
      let groups = this.classifyCategories.map((category) => category.group);
      return Array.from(new Set(groups));
    },
  },
  sockets: {
    annotating(data) {
      if (data.image_id !== this.image.id) return;

      if (data.active) {
        let found = this.annotating.indexOf(data.username);
        if (found < 0) {
          this.annotating.push(data.username);
        }
      } else {
        this.annotating.splice(this.annotating.indexOf(data.username), 1);
      }
    },
  },
  beforeRouteLeave(to, from, next) {
    this.current.annotation = -1;

    this.$nextTick(() => {
      this.$socket.emit("annotating", {
        image_id: this.image.id,
        active: false,
      });

      // don't save if in review mode
      if (this.annotateMode === "annotate") this.save(next);
      else next();
    });
  },
  mounted() {
    this.setDataset(null);

    // this.loading.loader = this.$loading.show({
    //   color: "white",
    //   // backgroundColor: "#4b5162",
    //   height: 150,
    //   opacity: 0.8,
    //   width: 150
    // });

    this.initCanvas();
    this.getData();

    this.$socket.emit("annotating", { image_id: this.image.id, active: true });
  },
  created() {
    this.paper = new paper.PaperScope();

    this.image.id = parseInt(this.identifier);
    this.image.url = "/tagging/api/image/" + this.image.id;
  },
};
</script>

<style scoped>
.alert {
  bottom: 0;
  width: 50%;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

/* width */
::-webkit-scrollbar {
  width: 7px;
}

/* Track */
::-webkit-scrollbar-track {
  box-shadow: inset 0 0 5px grey;
  border-radius: 10px;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: white;
  border-radius: 10px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: #9feeb0;
}

.top-panel {
  width: 100%;
  /* left: 5%; */
  padding-top: 55px;
  background-color: #4b5162;
  /* background-color: white; */
  color: white;
  /* position: relative; */
}

.left-panel {
  background-color: #4b5162;
  width: 85px;
  padding-top: 40px;
  float: left;
  height: 100%;
  /* overflow: hidden; */
}

.right-panel {
  padding-top: 40px;
  background-color: #4b5162;
  width: 300px;
  height: inherit;
  float: right;
}

.middle-panel {
  display: block;
  width: inherit;
  height: inherit;
  background-color: #7c818c;
  overflow: hidden;
  position: relative;
}

.frame {
  /* padding-top: vh; */
  /* padding-left: 5vw; */
  margin: 0;
  width: 100%;
  height: 100%;
}

.canvas {
  /* padding-top: 5vh; */
  display: block;
  width: 100%;
  height: 100%;
}

#image {
  position: absolute;
}

.sidebar-section {
  width: 100%;
  padding-left: 5px;
  padding-right: 5px;
  overflow: auto;
}

.sidebar-title {
  color: white;
}

/* Tool section */
.tool-section {
  margin: 5px;
  border-radius: 5px;
  background-color: #383c4a;
  padding: 0 5px 5px 5px;
  overflow: auto;
}

/* Categories/Annotations section */
.meta-input {
  padding: 3px;
  background-color: inherit;
  width: 100%;
  height: 100%;
  border: none;
}

.meta-item {
  background-color: inherit;
  height: 30px;
  border: none;
}

.status-icon {
  font-size: 150px;
  /* color: white; */
  color: white;
  position: absolute;
  left: calc(50% - 75px);
  top: calc(50% - 75px);
}

.search {
  width: 100%;
  height: 20px;
  /* color: white; */
  background-color: rgba(255, 255, 255, 0.945);
  border: none;
  text-align: center;
  border-radius: 4px;
}

.hr-line {
  background-color: rgba(180, 180, 180, 0.925);
  height: 1px;
  border: 0;
}

hr {
  width: 87%;
}

.btn-custom {
  width: 83px !important;
}
</style>
