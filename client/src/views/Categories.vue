<template>
  <div v-if="isAdmin">
    <div style="padding-top: 55px" />
    <div
      class="album py-5 bg-light"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="container">
        <h2 class="text-center">Categories</h2>

        <p class="text-center">
          Loaded <strong>{{ categoryCount }}</strong> categories.
        </p>

        <!-- <div class="row justify-content-md-center">
          <div
            class="col-md-auto btn-group"
            role="group"
            style="padding-bottom: 20px"
          >
            <button
              type="button"
              class="btn btn-success"
              data-toggle="modal"
              data-target="#createCategories"
            >
              Create
            </button>
            <button type="button" class="btn btn-secondary" @click="updatePage">
              Refresh
            </button>
          </div>
        </div> -->

        <hr />

        <p v-if="categories.length < 1" class="text-center">
          You need to create a category!
        </p>
        <div v-else>
          <Pagination :numPages="pages" @pagechange="updatePage" />
          <div class="row">
            <CategoryCard
              v-for="category in categories"
              :key="category.id"
              :category="category"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="createCategories">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Creating a Category</h5>
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
                <label>Name:</label>
                <input
                  v-model="newCategoryName"
                  class="form-control"
                  :class="{ 'is-invalid': newCategoryName.trim().length === 0 }"
                  required="true"
                  placeholder="Name"
                />
              </div>

              <div class="form-group row">
                <label class="col-sm-2 col-form-label">Color:</label>
                <div class="col-sm-9">
                  <input
                    v-model="newCategoryColor"
                    type="color"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-check">
                <input
                  v-model="newCategoryIsClassified"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Label</label>
              </div>
              <br />

              <div v-if="newCategoryIsClassified" class="form-group">
                <label>Subcategory:</label>
                <button
                  type="button"
                  class="btn btn-light"
                  style="float: right"
                  @click="createSubcategory"
                >
                  <i
                    class="fa fa-plus"
                    aria-hidden="true"
                    style="color: green"
                  />
                </button>
                <br />

                <li
                  v-for="(object, index) in newCategorySubcategory"
                  :key="index"
                  class="list-group-item"
                >
                  <div class="row" style="cell">
                    <div class="col-sm">
                      <input
                        v-model="object.name"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': !object.name }"
                      />
                    </div>
                    <button
                      type="button"
                      class="btn btn-light"
                      style="float: right"
                      @click="removeSubcategory(index)"
                    >
                      <i
                        class="fa fa-trash"
                        aria-hidden="true"
                        style="color: red"
                      />
                    </button>
                  </div>
                </li>
              </div>

              <div v-if="newCategoryIsClassified" class="form-group">
                <label>Group:</label>
                <input
                  v-model="newCategoryGroup"
                  class="form-control"
                  :class="{
                    'is-invalid': newCategoryGroup.trim().length === 0,
                  }"
                  required="true"
                  placeholder="Group"
                />
              </div>

              <!-- <div v-show="false" class="form-group">
                <KeypointsDefinition
                  ref="keypoints"
                  v-model="newCategoryKeypoint"
                  element-id="keypoints"
                  placeholder="Add a keypoint"
                ></KeypointsDefinition>
              </div> -->
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!isFormValid"
              :class="{ disabled: !isFormValid }"
              data-dismiss="modal"
              @click="createCategory"
            >
              Create Category
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

import Category from "@/models/categories";

import CategoryCard from "@/components/cards/CategoryCard";
import Pagination from "@/components/Pagination";
// import KeypointsDefinition from "@/components/KeypointsDefinition";

import { mapMutations } from "vuex";

export default {
  name: "Categories",
  components: {
    CategoryCard,
    Pagination,
    // KeypointsDefinition
  },
  mixins: [toastrs],
  data() {
    return {
      categoryCount: 0,
      pages: 1,
      page: 1,
      limit: 50,
      range: 11,
      newCategoryName: "",
      newCategorySupercategory: "",
      newCategorySubcategory: [],
      newCategoryColor: "",
      // newCategoryKeypoint: {
      //   labels: [],
      //   edges: [],
      //   colors: []
      // },
      newCategoryIsClassified: false,
      newCategoryGroup: "Labeling",
      categories: [],
      status: {
        data: { state: true, message: "Loading categories" },
      },
    };
  },
  computed: {
    isFormValid() {
      return (
        this.newCategoryName.length !== 0 &&
        this.newCategoryGroup.length &&
        this.newCategorySubcategory.every((x) => x.name)
      );
    },
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess"]),
    updatePage() {
      const process = "Loading categories";
      this.addProcess(process);

      Category.allData({
        page: this.page,
        limit: this.limit,
      })
        .then((response) => {
          this.categories = response.data.categories;
          this.page = response.data.pagination.page;
          this.pages = response.data.pagination.pages;
          this.categoryCount = response.data.pagination.total;
        })
        .catch((error) => {
          this.axiosRequestError("Category", "Request data error");
        })
        .finally(() => this.removeProcess(process));
    },

    createCategory() {
      if (this.newCategoryName.length < 1) return;
      const arr = [];
      if (this.newCategorySubcategory.length > 0) {
        const temp = this.newCategorySubcategory.map((x) => x.name);
        const a = new Set(temp);
        for (const item of Array.from(a)) {
          arr.push({ name: item });
        }
      }

      Category.create({
        name: this.newCategoryName,
        supercategory: this.newCategorySupercategory,
        subcategory: arr,
        color: this.newCategoryColor,
        classified: this.newCategoryIsClassified,
        group: this.newCategoryGroup,
        // keypoint_labels: this.newCategoryKeypoint.labels,
        // keypoint_edges: this.newCategoryKeypoint.edges,
        // keypoint_colors: this.newCategoryKeypoint.colors
      })
        .then(() => {
          this.newCategoryName = "";
          this.newCategorySupercategory = "";
          this.newCategoryColor = "";
          // this.newCategoryKeypoint = {};
          this.newCategoryIsClassified = false;
          this.newCategorySubcategory = [];
          this.newCategoryGroup = "Labeling";
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError(
            "Creating Category",
            error.response.data.message
          );
        });
    },

    createSubcategory() {
      this.newCategorySubcategory.push({
        name: "",
      });
    },

    removeSubcategory(index) {
      this.newCategorySubcategory.splice(index, 1);
    },

    previousPage() {
      this.page -= 1;
      if (this.page < 1) {
        this.page = 1;
      }
    },
    nextPage: function () {
      this.page += 1;
      if (this.page > this.pages) {
        this.page = this.pages;
      }
    },
  },
  created() {
    if (!this.isAdmin) this.$router.push({ path: "*" });
    else this.updatePage();
  },
};
</script>

<style scoped>
.card-img-overlay {
  padding: 0 10px 0 0;
}

.icon-more {
  width: 10%;
  margin: 3px 0;
  padding: 0;
  float: right;
  color: black;
}

.help-icon {
  color: darkblue;
  font-size: 20px;
  display: inline;
}

.fa {
  font-size: 20px;
}
</style>
