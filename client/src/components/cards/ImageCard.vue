<template>
  <div class="col-md-3">
    <div
      class="card mb-4 shadow-sm"
      :class="{ border: annotated, 'border-danger': annotated }"
      @mouseover="hover = true"
      @mouseleave="hover = false"
    >
      <div @click="openAnnotator">
        <v-lazy-image
          :src="imageUrl"
          :src-placeholder="loaderUrl"
          class="card-img-top"
          style="width: 100%; display: block"
          :style="{ opacity: annotated ? 0.3 : 1 }"
        />
      </div>

      <b v-if="annotated" class="overlay-text text-center">
        Being annotated by {{ image.annotating.join(", ") }}
      </b>

      <div class="card-body" :style="{ opacity: annotated ? 0.3 : 1 }">
        <span
          class="d-inline-block"
          :class="{ 'text-truncate': !hover }"
          style="max-width: 91%; float: left"
        >
          <strong class="card-title"
            >{{ image.id }}. {{ image.file_name }}</strong
          >
        </span>

        <i
          class="card-text fa fa-caret-down fa-lg icon-more"
          :id="'dropdownImage' + image.id"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
          aria-hidden="true"
        />

        <div
          class="dropdown-menu"
          :aria-labelledby="'dropdownImage' + image.id"
        >
          <button class="btn dropdown-item" @click="onDeleteClick">
            Delete
          </button>
          <button class="btn dropdown-item" @click="openAnnotator">
            Annotate
          </button>
          <!-- <button
            v-show="(isAdmin || isVtcc)"
            class="btn dropdown-item"
            @click="onDownloadClick"
          >
            Download Image & Annotation
          </button> -->
        </div>

        <br />

        <div class="flex-body-image-card">
          <div style="text-align: left">
            <p
              v-show="user_num_annotations > 0 && user_category_ids.length > 0"
            >
              {{ user_num_annotations }} annotation<span
                v-show="user_num_annotations > 1"
                >s</span
              >
            </p>
            <p v-if="!user_annotated || user_category_ids.length <= 0">
              No annotation
            </p>
          </div>

          <div>
            <span
              v-if="user_annotated && user_category_ids.length > 0"
              class="badge badge-pill category-badge badge-success"
            >
              Annotated
            </span>
          </div>

          <div v-if="user_annotated && user_category_ids.length > 0">
            <p class="card-text">
              <small class="text-muted"> Categories </small>
            </p>
            <span
              v-for="(id, index) in user_category_ids"
              :key="index"
              class="badge badge-pill badge-primary category-badge"
              :style="{ 'background-color': categories[id].color }"
            >
              {{ categories[id].name }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ImageCard",
  props: {
    image: {
      type: Object,
      required: true,
    },
    categories: {
      default: () => ({ name: "default", color: "#000000" }),
      type: Object,
      require: true,
    },
    order: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      hover: false,
      showAnnotations: true,
      loaderUrl: require("@/assets/loader.gif"),
    };
  },
  methods: {
    downloadURI(uri, exportName) {
      let link = document.createElement("a");
      link.href = uri;
      link.download = exportName;
      document.body.appendChild(link);
      link.click();
      link.remove();
    },

    openAnnotator() {
      this.$router.push({
        path: `/annotate/${this.image.id}`,
      });
      // this.$router.push({
      //   name: `annotate`,
      //   params: {
      //     identifier: this.image.id,
      //     folders: this.$parent.folders
      //   }
      // });
    },

    // onDownloadClick() {
    //   this.downloadURI(
    //     "/tagging/api/image/" + this.image.id + "?asAttachment=true",
    //     this.image.file_name
    //   );

    //   axios.get("/tagging/api/image/" + this.image.id + "/coco")
    //     .then(reponse => {
    //       let dataStr =
    //         "data:text/json;charset=utf-8," +
    //         encodeURIComponent(JSON.stringify(reponse.data));

    //       this.downloadURI(
    //         dataStr,
    //         this.image.file_name.replace(/\.[^/.]+$/, "") + ".json"
    //       );
    //     });
    // },

    onDeleteClick() {
      axios.delete("/tagging/api/image/" + this.image.id).then(() => {
        this.$parent.updatePage();
      });
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    isVtcc() {
      return this.$store.getters["user/isVtcc"];
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
    user_num_annotations() {
      return this.image.user_num_annotations[this.user];
    },
    user_annotated() {
      return this.image.user_annotated[this.user];
    },
    user_category_ids() {
      const ids = this.image.user_category_ids[this.user];
      if (ids) return ids.filter((id) => this.categories[id]);
      else return [];
    },
    annotated() {
      if (!this.image.annotating) return 0;
      return this.image.annotating.length > 0;
    },
    imageUrl() {
      // let d = new Date();
      // if (this.showAnnotations) {
      //   return `/tagging/api/image/${
      //     this.image.id
      //   }?width=250&thumbnail=true&dummy=${d.getTime()}`;
      // } else {
      //   return "/tagging/api/image/" + this.image.id + "?width=250";
      // }
      return "/tagging/api/image/" + this.image.id + "?width=250";
    },
  },
};
</script>

<style scoped>
.card-img-overlay {
  padding: 0;
}

.overlay-text {
  position: absolute;
  padding: 10px;
  top: 30px;
  width: 100%;
}

.card-body {
  padding: 10px 10px 0 10px;
}

p {
  margin: 0;
  padding: 0 0 3px 0;
}

.list-group-item {
  height: 21px;
  font-size: 13px;
  padding: 2px;
  background-color: #4b5162;
}

.icon-more {
  position: absolute;
  right: 5px;
  padding: 3px 10px;
  float: right;
  color: black;
}

.category-badge {
  float: left;
  margin: 0 2px 5px 0;
}

.flex-body-image-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  width: 100%;
  flex: 0 0 100%;
  float: left;
}
</style>
