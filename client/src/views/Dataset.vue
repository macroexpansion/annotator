<template>
  <div @mousemove="mouseMove">
    <div style="padding-top: 55px" />

    <div class="bg-light" :style="{ 'margin-left': sidebar.width + 'px' }">
      <nav
        class="nav border-bottom shadow-sm"
        style="background-color: #4b5162"
      >
        <a
          class="btn tab"
          @click="tab = 'images'"
          :style="{ color: tab == 'images' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-picture-o" aria-hidden="true"></i> Images
        </a>

        <a
          v-if="isAdmin || isVtcc"
          class="btn tab"
          @click="tab = 'review'"
          :style="{ color: tab == 'review' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-book" aria-hidden="true"></i> Review
        </a>

        <a
          v-if="isAdmin || isVtcc"
          class="btn tab"
          @click="tab = 'exports'"
          :style="{ color: tab == 'exports' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-share" aria-hidden="true"></i> Exports
        </a>

        <a
          class="btn tab"
          @click="tab = 'members'"
          :style="{ color: tab == 'members' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-users" aria-hidden="true"></i> Members
        </a>

        <a
          v-if="isAdmin || isVtcc"
          class="btn tab"
          @click="tab = 'statistics'"
          :style="{ color: tab == 'statistics' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-bar-chart" aria-hidden="true"></i> Statistics
        </a>

        <!-- <a
          v-if="isAdmin"
          class="btn tab"
          @click="tab = 'settings'"
          :style="{ color: tab == 'settings' ? 'white' : 'darkgray' }"
        >
          <i class="fa fa-cog" aria-hidden="true"></i> Settings
        </a> -->
      </nav>

      <div class="breadcrumb-container bg-light">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"></li>
          <li class="breadcrumb-item active">
            <button class="btn btn-sm btn-link" @click="folders = []">
              {{ dataset.name }}
            </button>
          </li>
          <li
            v-for="(folder, folderId) in folders"
            :key="folderId"
            class="breadcrumb-item"
          >
            <button
              class="btn btn-sm btn-link"
              :disabled="folders[folders.length - 1] === folder"
              @click="removeFolder(folder)"
            >
              {{ folder }}
            </button>
          </li>
        </ol>
      </div>

      <div
        class="bg-light text-left"
        style="overflow: auto; height: calc(100vh - 150px); margin: 10px"
      >
        <!-- Images -->
        <div class="container" v-if="tab == 'images'">
          <p class="text-center" v-if="images.length < 1">
            No images found in directory.
          </p>
          <div v-else>
            <br />
            <div class="row">
              <ImageCard
                :categories="ImageCardCategories"
                v-for="image in images"
                :key="image.id"
                :image="image"
                :order="order"
              />
            </div>
            <Pagination
              :numPages="pages"
              @pagechange="updatePage"
              datasetPagination
              :annotatedProp="panel.showAnnotated"
              :notAnnotatedProp="panel.showNotAnnotated"
            />
          </div>
        </div>

        <!-- Review -->
        <div class="container" v-if="tab == 'review'">
          <div class="select-bar">
            <select
              v-model="selectedUser"
              class="form-control"
              style="width: 200px"
            >
              <option
                v-for="(user, idx) in users"
                :key="idx"
                :value="user.username"
              >
                {{ user.username }}
              </option>
            </select>
          </div>
          <br />

          <!-- <ol class="breadcrumb">
            <li class="breadcrumb-item"></li>
            <li class="breadcrumb-item active">
              <button class="btn btn-sm btn-link" @click="folders = []">
                {{ dataset.name }}
              </button>
            </li>
            <li
              v-for="(folder, folderId) in folders"
              :key="folderId"
              class="breadcrumb-item"
            >
              <button
                class="btn btn-sm btn-link"
                :disabled="folders[folders.length - 1] === folder"
                @click="removeFolder(folder)"
              >
                {{ folder }}
              </button>
            </li>
          </ol> -->

          <p class="text-center" v-if="images.length < 1">
            No images found in directory.
          </p>
          <div v-else>
            <br />
            <div class="row">
              <ImageCard
                :categories="ImageCardCategories"
                v-for="image in images"
                :key="image.id"
                :image="image"
                :order="order"
              />
            </div>
            <Pagination
              :numPages="pages"
              @pagechange="updatePage"
              datasetPagination
              :annotatedProp="panel.showAnnotated"
              :notAnnotatedProp="panel.showNotAnnotated"
            />
          </div>
        </div>

        <!-- Exports -->
        <div class="container" v-if="tab == 'exports'">
          <div class="card my-3 p-3 shadow-sm mr-2">
            <h6 class="border-bottom border-gray pb-2"><b>Exports</b></h6>

            <div
              class="media text-muted pt-3"
              v-for="(exp, idx) in datasetExports"
              :key="idx"
            >
              <div class="media-body lh-125 border-bottom border-gray">
                {{ exp.id }}. Exported
                {{ exp.ago.length > 0 ? exp.ago : 0 + " seconds" }} ago
                <div style="display: inline">
                  <span
                    v-for="(tag, idx) in exp.tags"
                    :key="idx"
                    class="badge badge-secondary"
                    style="margin: 1px"
                  >
                    {{ tag }}
                  </span>
                </div>

                <button
                  class="btn btn-sm btn-danger btn-custom"
                  style="float: right; margin: 2px; padding: 2px"
                  @click="deleteExport(exp.id)"
                >
                  <i class="fa fa-trash" aria-hidden="true"></i>
                </button>

                <button
                  class="btn btn-sm btn-success btn-custom"
                  style="float: right; margin: 2px; padding: 2px"
                  @click="downloadExport(exp.id)"
                >
                  <i class="fa fa-download" aria-hidden="true"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Members -->
        <div class="container" v-if="tab == 'members'">
          <!-- <div class="card my-3 p-3 shadow-sm mr-2">
            <h6 class="border-bottom border-gray pb-2">
              <b>Invite Members</b>
            </h6>
          </div> -->

          <div class="card my-3 p-3 shadow-sm mr-2">
            <h6 class="border-bottom border-gray pb-2">
              <b>Existing Members</b>
            </h6>

            <div
              class="media text-muted pt-3"
              v-for="(user, idx) in users"
              :key="idx"
            >
              <img
                src="https://d1nhio0ox7pgb.cloudfront.net/_img/o_collection_png/green_dark_grey/256x256/plain/user.png"
                class="mr-2 rounded"
                style="width: 32px; height: 32px"
              />
              <div
                class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray"
              >
                <div
                  class="d-flex justify-content-between align-items-center w-100"
                >
                  <div class="text-gray-dark">
                    <strong>{{ user.name }}</strong> @{{ user.username }}
                  </div>
                  <a href="#">{{ user.group }}</a>
                </div>
                <span class="d-block">
                  Last seen: {{ getLastSeen(user) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics -->
        <div
          class="container"
          v-if="tab == 'statistics' && (isAdmin || isVtcc)"
        >
          <div v-if="stats == null">Calculating...</div>

          <div v-else>
            <div class="row">
              <div
                v-if="stats.total"
                class="card my-3 p-3 shadow-sm col-3 mr-2"
              >
                <h6 class="border-bottom border-gray pb-2"><b>Total</b></h6>
                <div
                  class="row"
                  v-for="(stat, idx) in Object.keys(stats.total)"
                  :key="idx"
                >
                  <strong class="col-8">{{ stat }}:</strong>
                  <span class="col-4">{{ stats.total[stat].toFixed(0) }}</span>
                </div>
              </div>

              <div
                v-if="stats.average"
                class="card my-3 p-3 shadow-sm col-4 mr-2"
              >
                <h6 class="border-bottom border-gray pb-2"><b>Average</b></h6>
                <div
                  class="row"
                  v-for="(stat, idx) in Object.keys(stats.average)"
                  :key="idx"
                >
                  <strong class="col-8">{{ stat }}:</strong>
                  <span class="col-4">{{
                    stats.average[stat].toFixed(0)
                  }}</span>
                </div>
              </div>

              <div
                v-if="stats.categories"
                class="card my-3 p-3 shadow-sm col-4 mr-2"
              >
                <h6 class="border-bottom border-gray pb-2">
                  <b>Annotations Per Category</b>
                </h6>
                <div
                  class="row"
                  v-for="(stat, idx) in Object.keys(stats.categories)"
                  :key="idx"
                >
                  <strong class="col-8">{{ stat }}:</strong>
                  <span class="col-4">{{
                    stats.categories[stat].toFixed(0)
                  }}</span>
                </div>
              </div>

              <div
                v-if="stats.images_per_category"
                class="card my-3 p-3 shadow-sm col-4 mr-2"
              >
                <h6 class="border-bottom border-gray pb-2">
                  <b>Annotated Images Per Category</b>
                </h6>
                <div
                  class="row"
                  v-for="(stat, idx) in Object.keys(stats.images_per_category)"
                  :key="idx"
                >
                  <strong class="col-8">{{ stat }}:</strong>
                  <span class="col-4">{{
                    stats.images_per_category[stat].toFixed(0)
                  }}</span>
                </div>
              </div>

              <div class="card my-3 p-3 shadow-sm col-4 mr-2">
                <h6 class="border-bottom border-gray pb-2">
                  <b>Annotated Images Per User</b>
                </h6>
                <div class="row" v-for="(user, idx) in users" :key="idx">
                  <strong class="col-8"> {{ user.username }}: </strong>
                  <span class="col-4">
                    {{ getUserAnnotated(user.username) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="container" v-if="tab == 'settings' && isAdmin">
          <div class="card my-3 p-3 shadow-sm mr-2">
            <h6 class="border-bottom border-gray pb-2"><b>Metadata</b></h6>

            <button
              class="btn btn-sm btn-block btn-danger"
              @click="resetMetadata"
            >
              Reset All Metadata
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      id="filter"
      ref="sidebar"
      class="sidebar"
      :style="{ width: sidebar.width + 'px' }"
    >
      <div style="padding-top: 10px" />
      <h3>{{ dataset.name }}</h3>
      <p class="text-center" style="color: lightgray">
        Total of <strong style="color: white">{{ imageCount }}</strong> images
        displayed on <strong style="color: white">{{ pages }}</strong> pages.
      </p>
      <div class="row justify-content-md-center sidebar-section-buttons">
        <button
          v-if="isAdmin"
          type="button"
          class="btn btn-primary btn-block"
          @click="createScanTask"
        >
          <div v-if="scan.id != null" class="progress">
            <div
              class="progress-bar bg-secondary"
              :style="{ width: `${scan.progress}%` }"
            >
              Scanning
            </div>
          </div>
          <div v-else>Scan</div>
        </button>

        <div class="btn-group btn-block">
          <button
            class="btn btn-success"
            :class="{ disabled: tab !== 'images' }"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-expanded="false"
          >
            <div v-if="uploading.id != null" class="progress">
              <div
                class="progress-bar bg-success"
                :style="{ width: `${uploading.progress}%` }"
              >
                Uploading
              </div>
            </div>
            <div v-else>Upload</div>
          </button>
          <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <li>
              <a class="dropdown-item" href="#" @click="uploadModal">
                Upload Files
              </a>
            </li>
            <li>
              <a class="dropdown-item" href="#" @click="uploadFolderModal">
                Upload Folder
              </a>
            </li>
          </ul>
        </div>

        <button
          v-show="isAdmin || isVtcc"
          type="button"
          class="btn btn-light btn-block"
          @click="exportModal"
        >
          <div v-if="exporting.id != null" class="progress">
            <div
              class="progress-bar bg-dark"
              :style="{ width: `${exporting.progress}%` }"
            >
              Exporting
            </div>
          </div>
          <div v-else>Export</div>
        </button>
      </div>

      <hr />

      <h6 class="sidebar-title text-center">Subdirectories</h6>
      <div class="sidebar-section" style="max-height: 40%; color: lightgray">
        <div v-if="subdirectories.length > 0">
          <button
            v-for="(subdirectory, subId) in subdirectories"
            :key="subId"
            class="btn badge badge-pill badge-primary category-badge"
            style="margin: 2px"
            @click="folders.push(subdirectory)"
          >
            {{ subdirectory }}
          </button>
        </div>
        <p v-else style="margin: 0; font-size: 13px; color: gray">
          No subdirectory found.
        </p>
      </div>

      <hr />

      <h6 class="sidebar-title text-center">Filtering Options</h6>
      <div
        class="sidebar-section"
        :style="{
          'max-height': '50%',
          color: 'lightgray',
          display: 'flex',
          'flex-direction': 'column',
          'margin-left': sidebar.width / 2 - 77 + 'px',
        }"
      >
        <PanelToggle
          name="Show Annotated"
          v-model="panel.showAnnotated"
          filterToggle
        />
        <PanelToggle
          name="Show Not Annotated"
          v-model="panel.showNotAnnotated"
          filterToggle
        />
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="imageUpload">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Upload Image</h5>
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
              <div class="form-group">
                <label for="upload-files"
                  >Image files (.jpg, .jpeg, .dcm)</label
                >
                <input
                  type="file"
                  accept="image/*, video/*"
                  class="form-control-file"
                  id="upload-files"
                  multiple
                />
              </div>
              <div v-if="isAdmin || isVtcc" class="form-check">
                <input
                  v-model="crop"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Crop</label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              @click="uploadFiles"
              data-dismiss="modal"
            >
              Upload
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

    <div class="modal fade" tabindex="-1" role="dialog" id="folderUpload">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Upload Folder</h5>
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
              <div class="form-group">
                <label for="upload-folders">Folder</label>
                <input
                  type="file"
                  accept="image/*, video/*"
                  class="form-control-file"
                  id="upload-folders"
                  webkitdirectory
                  directory
                />
              </div>
              <div v-if="isAdmin || isVtcc" class="form-check">
                <input
                  v-model="crop"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Crop</label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              @click="uploadFolders"
              data-dismiss="modal"
            >
              Upload
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

    <div class="modal fade" tabindex="-1" role="dialog" id="exportDataset">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Export {{ dataset.name }}</h5>
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
              <div class="form-group">
                <label>Categories (Empty export all)</label>
                <TagsInput
                  v-model="exporting.categories"
                  element-id="exportCategories"
                  :existing-tags="categoryTags"
                  :typeahead="true"
                  :typeahead-activation-threshold="0"
                ></TagsInput>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="exportCOCO">
              Export
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
import toastrs from "@/mixins/toastrs";
import Dataset from "@/models/datasets";
import Export from "@/models/exports";
import ImageCard from "@/components/cards/ImageCard";
import Pagination from "@/components/Pagination";
import PanelString from "@/components/PanelInputString";
import PanelToggle from "@/components/PanelToggle";
import PanelDropdown from "@/components/PanelInputDropdown";
import JQuery from "jquery";
import TagsInput from "@/components/TagsInput";

import axios from "axios";

import { mapMutations } from "vuex";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
TimeAgo.addDefaultLocale(en);
const timeAgo = new TimeAgo("en-US");

const $ = JQuery;

export default {
  name: "Dataset",
  components: {
    ImageCard,
    Pagination,
    PanelString,
    PanelToggle,
    PanelDropdown,
    TagsInput,
  },
  mixins: [toastrs],
  props: {
    identifier: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      pages: 1,
      generateLimit: 100,
      limit: 40,
      imageCount: 0,
      categories: [],
      images: [],
      folders: [],
      dataset: {
        id: 0,
      },
      users: [],
      subdirectories: [],
      status: {
        data: { state: true, message: "Loading data" },
      },
      keyword: "",
      mouseDown: false,
      sidebar: {
        drag: false,
        width: window.innerWidth * 0.2,
        canResize: false,
      },
      scan: {
        progress: 0,
        id: null,
      },
      generate: {
        progress: 0,
        id: null,
      },
      uploading: {
        progress: 0,
        id: null,
      },
      importing: {
        progress: 0,
        id: null,
      },
      exporting: {
        categories: [],
        progress: 0,
        id: null,
      },
      selected: {
        categories: [],
      },
      datasetExports: [],
      tab: "images",
      order: "id",
      orderTypes: {
        file_name: "File Name",
        id: "ID",
      },
      query: {
        file_name__icontains: "",
        ...this.$route.query,
      },
      panel: {
        showAnnotated: true,
        showNotAnnotated: true,
      },
      stats: null,
      selectedUser: null,
      crop: false,
    };
  },
  methods: {
    ...mapMutations([
      "addProcess",
      "removeProcess",
      "setFolders",
      "setToFolders",
    ]),
    ...mapMutations("review", ["setReviewUser", "setAnnotateMode"]),
    updatePage(page) {
      if (page === undefined)
        page = parseInt(localStorage.getItem("pagination/page")) || 1;

      const process = "Loading images from dataset";
      this.addProcess(process);

      Dataset.getData(this.dataset.id, {
        page: page,
        limit: this.limit,
        folder: this.folders.join("/"),
        // ...this.query,
        annotated: this.queryAnnotated,
        order: this.order,
        user: this.current_user,
      })
        .then((response) => {
          this.images = response.data.images;
          this.dataset = response.data.dataset;
          this.categories = response.data.categories;
          this.imageCount = response.data.total;
          this.pages = response.data.pages;
          this.subdirectories = response.data.subdirectories;
          // this.scan.id = response.data.scanId;
          // this.generate.id = response.data.generateId;
          // this.importing.id = response.data.importId;
          // this.exporting.id = response.data.exportId;
        })
        .catch((error) => {
          this.axiosRequestError("Loading Dataset", error.message);
        })
        .finally(() => this.removeProcess(process));
    },
    getUsers() {
      Dataset.getUsers(this.dataset.id).then((response) => {
        this.users = response.data;
      });
    },
    downloadExport(id) {
      Export.download(id, this.dataset.name);
    },
    deleteExport(id) {
      Export.delete(id).then((response) => {
        this.getExports();
      });
    },
    getExports() {
      Dataset.getExports(this.dataset.id).then((response) => {
        this.datasetExports = response.data;
      });
    },
    resetMetadata() {
      let r = confirm(
        "You can not undo reseting of all metadata in" +
          "this dataset. This includes metadata of images" +
          "and annotations."
      );

      if (r) {
        Dataset.resetMetadata(this.dataset.id);
      }
    },
    getStats() {
      Dataset.getStats(this.dataset.id).then((response) => {
        this.stats = response.data;
      });
    },
    createScanTask() {
      if (this.scan.id != null) {
        this.$router.push({ path: "/tasks", query: { id: this.scan.id } });
        return;
      }

      Dataset.scan(this.dataset.id)
        .then((response) => {
          let id = response.data.id;
          this.scan.id = id;
        })
        .catch((error) => {
          this.axiosRequestError(
            "Scanning Dataset",
            error.response.data.message
          );
        })
        .finally(() => this.removeProcess(process));
    },
    exportModal() {
      if (this.exporting.id != null) {
        this.$router.push({ path: "/tasks", query: { id: this.exporting.id } });
        return;
      }
      $("#exportDataset").modal("show");
    },
    exportCOCO() {
      $("#exportDataset").modal("hide");
      Dataset.exportingCOCO(
        this.dataset.id,
        this.exporting.categories,
        this.exportUser
      )
        .then((response) => {
          let id = response.data.id;
          this.exporting.id = id;
        })
        .catch((error) => {
          this.axiosRequestError("Exporting COCO", error.response.data.message);
        })
        .finally(() => this.removeProcess(process));
    },
    removeFolder(folder) {
      let index = this.folders.indexOf(folder);
      this.folders.splice(index + 1, this.folders.length);
    },
    uploadModal() {
      if (this.uploading.id != null) {
        this.$router.push({ path: "/tasks", query: { id: this.uploading.id } });
        return;
      }

      $("#imageUpload").modal("show");
    },
    uploadFolderModal() {
      if (this.uploading.id != null) {
        this.$router.push({ path: "/tasks", query: { id: this.uploading.id } });
        return;
      }

      $("#folderUpload").modal("show");
    },
    uploadFiles() {
      const files = document.getElementById("upload-files").files;
      const filteredFiles = [];
      for (let i = 0; i < files.length; i++) {
        const file = files.item(i);
        if (
          file.type.includes("image/") ||
          file.type.includes("video/") ||
          file.type.includes("/dicom")
        )
          filteredFiles.push(file);
      }

      if (filteredFiles.length > 0) {
        axios
          .get(`/tagging/api/dataset/${this.dataset.id}/taskids`)
          .then((response) => {
            this.uploading.id = response.data.id;
            this.scan.id = response.data.scan_id;

            Dataset.uploadFiles(
              this.dataset.id,
              filteredFiles,
              this.uploading.id,
              this.scan.id,
              this.crop
            )
              .then((response) => {
                document.getElementById("upload-files").value = "";
                this.crop = false;
              })
              .catch((error) => {
                this.axiosRequestError("Uploading Files", error.message);
              })
              .finally(() => {
                this.removeProcess(process);
                localStorage.setItem("pagination/page", 1);
                this.updatePage(1);
              });
          });
      } else {
        this.axiosRequestError("Uploading Files", "Invalid file type");
      }
    },
    uploadFolders() {
      const files = document.getElementById("upload-folders").files;
      // console.log(files);
      const filteredFiles = [];
      for (let i = 0; i < files.length; i++) {
        const file = files.item(i);
        if (
          file.type.includes("image/") ||
          file.type.includes("video/") ||
          file.type.includes("/dicom")
        )
          filteredFiles.push(file);
      }

      if (filteredFiles.length > 0) {
        axios
          .get(`/tagging/api/dataset/${this.dataset.id}/taskids`)
          .then((response) => {
            this.uploading.id = response.data.id;
            this.scan.id = response.data.scan_id;

            Dataset.uploadFolders(
              this.dataset.id,
              filteredFiles,
              this.uploading.id,
              this.scan.id,
              this.crop
            )
              .then((response) => {
                document.getElementById("upload-folders").value = "";
                this.crop = false;
              })
              .catch((error) => {
                this.axiosRequestError("Uploading Folders", error.message);
              })
              .finally(() => {
                this.removeProcess(process);
                localStorage.setItem("pagination/page", 1);
                this.updatePage(1);
              });
          });
      } else {
        this.axiosRequestError("Uploading Images", "Invalid file type");
      }
    },
    importCOCO() {
      let uploaded = document.getElementById("coco");
      Dataset.uploadCoco(this.dataset.id, uploaded.files[0])
        .then((response) => {
          let id = response.data.id;
          this.importing.id = id;
        })
        .catch((error) => {
          this.axiosRequestError("Importing COCO", error.response.data.message);
        })
        .finally(() => this.removeProcess(process));
    },
    mouseMove(event) {
      let element = this.$refs.sidebar;

      let sidebarWidth = element.offsetWidth;
      let clickWidth = event.x;
      let pixelsFromSide = Math.abs(sidebarWidth - clickWidth);

      this.sidebar.drag = pixelsFromSide < 4;

      if (this.sidebar.canResize) {
        event.preventDefault();
        let max = window.innerWidth * 0.5;
        this.sidebar.width = Math.min(Math.max(event.x, 150), max);
        localStorage.setItem("dataset/sideWidth", this.sidebar.width);
      }
    },
    startDrag() {
      this.mouseDown = true;
      this.sidebar.canResize = this.sidebar.drag;
    },
    stopDrag() {
      this.mouseDown = false;
      this.sidebar.canResize = false;
    },
    getUserAnnotated(username) {
      let count = 0;
      this.images.forEach((image) => {
        if (image.user_annotated[username]) count++;
      });
      return count;
    },
  },
  computed: {
    getLastSeen() {
      return (user) => {
        if (user.last_seen) {
          let last_time = new Date(user.last_seen["$date"]).getTime();
          // console.log(timeAgo.format(last_time));
          return timeAgo.format(last_time);
        } else return "";
      };
    },
    current_user() {
      if (this.tab === "review") return this.selectedUser;
      return this.user;
    },
    user() {
      return this.$store.getters["user/username"];
    },
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    isVtcc() {
      return this.$store.getters["user/isVtcc"];
    },
    queryAnnotated() {
      const showAnnotated = this.panel.showAnnotated;
      const showNotAnnotated = this.panel.showNotAnnotated;

      if (showAnnotated && showNotAnnotated) return null;
      if (!showAnnotated && !showNotAnnotated) return "no";

      return showAnnotated;
    },
    categoryTags() {
      const tags = {};
      this.categories.forEach((c) => (tags[c.id] = c.name));
      return tags;
    },
    ImageCardCategories() {
      const tags = {};
      this.categories.forEach((c) => {
        tags[c.id] = {
          name: c.name,
          color: c.color,
        };
      });
      return tags;
    },
    reviewUser() {
      return this.$store.getters["review/reviewUser"];
    },
    exportUser() {
      return this.$store.getters["review/annotateMode"] === "annotate"
        ? this.user
        : this.reviewUser;
    },
  },
  sockets: {
    taskProgress(data) {
      if (data.id === this.scan.id) {
        this.scan.progress = data.progress;
      }

      if (data.id === this.uploading.id) {
        this.uploading.progress = data.progress;
      }

      if (data.id === this.importing.id) {
        this.importing.progress = data.progress;
      }

      if (data.id === this.exporting.id) {
        this.exporting.progress = data.progress;
      }
    },
    annotating(data) {
      const image = this.images.find((i) => i.id == data.image_id);
      if (image == null) return;

      if (data.active) {
        const found = image.annotating.indexOf(data.username);
        if (found < 0) {
          image.annotating.push(data.username);
        }
      } else {
        image.annotating.splice(image.annotating.indexOf(data.username), 1);
      }
    },
  },
  watch: {
    selectedUser() {
      this.setReviewUser(this.selectedUser);
      this.updatePage();
    },
    "panel.showAnnotated"(val) {
      localStorage.setItem("panel/showAnnotated", val);
    },
    "panel.showNotAnnotated"(val) {
      localStorage.setItem("panel/showNotAnnotated", val);
    },
    tab(tab) {
      localStorage.setItem("dataset/tab", tab);
      if (tab === "images") {
        this.setAnnotateMode("annotate");
      }

      if (tab === "members") this.getUsers();

      if (tab === "review") {
        Dataset.getUsers(this.dataset.id)
          .then((response) => {
            this.users = response.data;
            const users = this.users.map((user) => user.username);
            if (!users.includes(this.selectedUser)) {
              this.selectedUser = users[0];
            }
          })
          .catch((error) => {
            this.axiosRequestError("Dataset", "Get user error");
          });

        this.setAnnotateMode("review");
      }

      if (tab === "statistics") {
        this.getStats();
        this.getUsers();
      }

      if (tab === "exports") this.getExports();
    },
    // order(order) {
    //   localStorage.setItem("dataset/order", order);
    //   this.updatePage();
    // },
    queryAnnotated() {
      this.updatePage();
    },
    // "selected.categories"(val) {
    //   this.updatePage(val);
    // },
    folders() {
      this.setFolders(this.folders);
      this.updatePage();
    },
    "sidebar.drag"(canDrag) {
      let el = this.$refs.sidebar;
      if (canDrag) {
        this.$el.style.cursor = "ew-resize";
        // el.style.borderRight = "4px solid #383c4a";
      } else {
        this.$el.style.cursor = "default";
        el.style.borderRight = "";
      }
    },
    "scan.progress"(progress) {
      if (progress >= 100) {
        setTimeout(() => {
          this.scan.progress = 0;
          this.scan.id = null;
        }, 1000);
      }
      this.updatePage();
    },
    "uploading.progress"(progress) {
      if (progress >= 100) {
        setTimeout(() => {
          this.uploading.progress = 0;
          this.uploading.id = null;
        }, 1000);
      }
    },
    "importing.progress"(progress) {
      if (progress >= 100) {
        setTimeout(() => {
          this.importing.progress = 0;
          this.importing.id = null;
        }, 1000);
      }
    },
    "exporting.progress"(progress) {
      if (progress >= 100) {
        setTimeout(() => {
          this.exporting.progress = 0;
          this.exporting.id = null;

          this.getExports();
        }, 1000);
      }
    },
  },
  beforeRouteUpdate() {
    this.dataset.id = parseInt(this.identifier);
    this.updatePage();
  },
  created() {
    const showAnnotated =
      localStorage.getItem("panel/showAnnotated") === "true";
    const showNotAnnotated =
      localStorage.getItem("panel/showNotAnnotated") === "true";

    if (localStorage.getItem("panel/showAnnotated") != null) {
      this.panel.showAnnotated = showAnnotated;
    }
    if (localStorage.getItem("panel/showNotAnnotated") != null) {
      this.panel.showNotAnnotated = showNotAnnotated;
    }

    const tab = localStorage.getItem("dataset/tab");
    const order = localStorage.getItem("dataset/order");
    const sideWidth = localStorage.getItem("dataset/sideWidth");

    if (sideWidth !== null) this.sidebar.width = parseInt(sideWidth);
    if (tab !== null) this.tab = tab;
    else {
      this.setAnnotateMode("annotate");
      this.tab = "images";
    }
    if (order !== null) this.order = order;

    if (this.reviewUser) this.selectedUser = this.reviewUser;
    else this.selectedUser = this.user;

    this.dataset.id = parseInt(this.identifier);
    if (this.$store.state.toFolders) this.folders = this.$store.state.folders;
    else this.folders = [];
    // this.updatePage();
  },
  mounted() {
    window.addEventListener("mouseup", this.stopDrag);
    window.addEventListener("mousedown", this.startDrag);
  },
  destroyed() {
    this.setToFolders(false);
    window.removeEventListener("mouseup", this.stopDrag);
    window.removeEventListener("mousedown", this.startDrag);
  },
};
</script>

<style scoped>
.breadcrumb-container {
  position: sticky;
  z-index: 99;
}

.breadcrumb {
  background-color: whitesmoke;
  padding: 4px 20px;
  margin: 5px 0;
}

.btn-link {
  padding: 0px;
}

.sidebar .title {
  color: white;
}

.progress {
  padding: 2px;
  height: 24px;
}

.sidebar {
  height: 100%;
  position: fixed;
  color: white;
  z-index: 1;
  top: 0;
  left: 0;
  background-color: #4b5162;
  overflow-x: hidden;
  padding-top: 60px;
}

.sidebar .closebtn {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 36px;
  margin-left: 50px;
}

.sidebar-title {
  color: white;
}

.sidebar-section-buttons {
  margin: 5px;
}

.sidebar-section {
  margin: 5px;
  /* border-radius: 5px; */
  /* background-color: #383c4a; */
  padding: 0 5px 2px 5px;
  overflow: auto;
}

.btn-custom {
  width: 30px !important;
}
</style>
