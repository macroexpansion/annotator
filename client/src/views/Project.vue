<template>
  <div>
    <div style="padding-top: 55px" />

    <div
      class="album py-5 bg-light"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="container">
        <h2 class="text-center">
          {{ project.name }}
        </h2>

        <p v-if="tab.selected === 'datasets'" class="text-center">
          Loaded <strong>{{ dataset.datasets.length }}</strong> datasets.
        </p>
        <p v-else class="text-center">
          Loaded <strong>{{ category.categories.length }}</strong> categories.
        </p>

        <div class="row justify-content-md-center">
          <div
            class="col-md-auto btn-group"
            role="group"
            style="padding-bottom: 20px"
          >
            <button
              type="button"
              class="btn btn-success"
              :disabled="false"
              :class="{ disabled: false }"
              data-toggle="modal"
              :data-target="
                tab.selected === 'datasets'
                  ? '#createDataset'
                  : '#createCategory'
              "
            >
              Create
            </button>

            <button
              type=" button"
              class="btn btn-secondary"
              @click="updatePage(dataset.page)"
            >
              Refresh
            </button>
          </div>
        </div>

        <ul class="nav nav-tabs nav-fill" id="myTab" role="tablist">
          <li class="nav-item" v-for="(item, idx) in tab.items" :key="idx">
            <a
              class="nav-link"
              :class="{ active: item.state }"
              data-toggle="tab"
              :href="'#' + item.name.toLowerCase()"
              role="tab"
              @click="onTabClick(item.name.toLowerCase())"
            >
              {{ item.name }}
            </a>
          </li>
        </ul>
        <div class="tab-content">
          <div
            v-for="(item, idx) in tab.items"
            :key="idx"
            :id="item.name.toLowerCase()"
            class="tab-pane"
            :class="{ show: item.state, active: item.state }"
            role="tabpanel"
          >
            <br />
            <div v-if="item.name === 'Datasets'">
              <p v-if="dataset.datasets.length < 1" class="text-center">
                You need to create a dataset!
              </p>
              <div v-else style="background-color: gray">
                <Pagination
                  :numPages="dataset.pages"
                  @pagechange="updatePage"
                />
                <div class="row bg-light">
                  <DatasetCard
                    v-for="item in dataset.datasets"
                    :key="item.id"
                    :dataset="item"
                    :categories="dataset.categories"
                  />
                </div>
              </div>
            </div>

            <div v-else>
              <p v-if="category.categories.length < 1" class="text-center">
                You need to create a category!
              </p>
              <div v-else>
                <Pagination
                  :numPages="category.pages"
                  @pagechange="updatePage"
                />
                <div class="row">
                  <CategoryCard
                    v-for="item in category.categories"
                    :key="item.id"
                    :category="item"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="createDataset">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Creating a Dataset</h5>
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
                <label>Dataset Name</label>
                <input
                  v-model.trim="createDataset.name"
                  class="form-control"
                  :class="{
                    'is-invalid': createDataset.name.trim().length === 0,
                    'is-valid': true,
                  }"
                  placeholder="Dataset name"
                  required
                />
                <div class="invalid-feedback">
                  {{ "Dataset name is required" }}
                </div>
              </div>

              <div class="form-group">
                <label>Default Categories</label>
                <TagsInput
                  v-model="createDataset.categories"
                  element-id="createCategoryID"
                  :existing-tags="categoryTags"
                  :typeahead="true"
                  :typeahead-activation-threshold="0"
                ></TagsInput>
              </div>

              <div class="form-group" required>
                <label>Folder Directory</label>
                <input class="form-control" disabled :value="directory" />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              :disabled="createDataset.name.trim().length === 0"
              :class="{ disabled: createDataset.name.trim().length === 0 }"
              data-dismiss="modal"
              @click="onCreateDatasetClick"
            >
              Create Dataset
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

    <div class="modal fade" tabindex="-1" role="dialog" id="createCategory">
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
                  v-model="createCategory.name"
                  class="form-control"
                  :class="{
                    'is-invalid': createCategory.name.trim().length === 0,
                    'is-valid': true,
                  }"
                  required="true"
                  placeholder="Name"
                />
                <div class="invalid-feedback">
                  {{ "Category name is required" }}
                </div>
              </div>

              <div class="form-group row">
                <label class="col-sm-2 col-form-label">Color:</label>
                <div class="col-sm-9">
                  <input
                    v-model="createCategory.color"
                    type="color"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-check">
                <input
                  v-model="createCategory.isClassified"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Label</label>
              </div>
              <br />

              <div v-if="createCategory.isClassified" class="form-group">
                <label>Subcategory:</label>
                <button
                  type="button"
                  class="btn btn-light"
                  style="float: right"
                  @click="onCreateSubcategoryClick"
                >
                  <i
                    class="fa fa-plus"
                    aria-hidden="true"
                    style="color: green"
                  />
                </button>
                <br />

                <li
                  v-for="(object, index) in createCategory.subcategory"
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
                      @click="onRemoveSubcategoryClick(index)"
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

              <div v-if="createCategory.isClassified" class="form-group">
                <label>Group:</label>
                <input
                  v-model="createCategory.group"
                  class="form-control"
                  :class="{
                    'is-invalid': createCategory.group.trim().length === 0,
                  }"
                  required="true"
                  placeholder="Group"
                />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!isFormValid"
              :class="{ disabled: !isFormValid }"
              data-dismiss="modal"
              @click="onCreateCategoryClick"
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

import Datasets from "@/models/datasets";
import Projects from "@/models/projects";
import AdminPanel from "@/models/admin";
import Category from "@/models/categories";

import DatasetCard from "@/components/cards/DatasetCard";
import CategoryCard from "@/components/cards/CategoryCard";
import Pagination from "@/components/Pagination";
import TagsInput from "@/components/TagsInput";

import { mapMutations } from "vuex";

export default {
  name: "Project",
  components: { DatasetCard, Pagination, TagsInput, CategoryCard },
  mixins: [toastrs],
  props: {
    identifier: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      project: {},
      createDataset: {
        name: "",
        categories: [],
      },
      createCategory: {
        name: "",
        group: "Labeling",
        supercategory: "",
        subcategory: [],
        color: "",
        isClassified: false,
      },
      users: [],
      dataset: {
        pages: 1,
        limit: 20,
        page: 1,
        datasets: [],
        subdirectories: [],
        categories: [],
      },
      category: {
        pages: 1,
        limit: 20,
        page: 1,
        categories: [],
        categoryCount: 0,
      },
      tab: {
        selected: "datasets",
        items: [
          { name: "Datasets", state: true },
          { name: "Categories", state: false },
        ],
      },
    };
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess", "setProject"]),
    updatePage(page) {
      const process = "Loading datasets";
      this.addProcess(process);

      Projects.getProject(this.identifier)
        .then((response) => {
          this.project = response.data;
          this.setProject({ name: this.project.name, id: this.project.id });

          if (this.tab.selected === "datasets") {
            Datasets.getDatasets({
              page: page,
              limit: this.dataset.limit,
              project_id: this.project.id,
            })
              .then((response) => {
                this.dataset.datasets = response.data.datasets;
                this.dataset.categories = response.data.categories;
                this.dataset.subdirectories = response.data.subdirectories;
                this.dataset.pages = response.data.pagination.pages;
                this.dataset.page = response.data.pagination.page;

                AdminPanel.getUsers(this.dataset.limit).then((response) => {
                  this.users = response.data.users;
                });
              })
              .catch((error) => {
                this.axiosRequestError(
                  "Could not find datasets",
                  "Loading datasets error"
                );
              });
          } else {
            Category.getCategories({
              page: page,
              limit: this.category.limit,
              project_id: this.project.id,
            })
              .then((response) => {
                this.category.categories = response.data.categories;
                this.category.page = response.data.pagination.page;
                this.category.pages = response.data.pagination.pages;
                this.category.categoryCount = response.data.pagination.total;
              })
              .catch((error) => {
                this.axiosRequestError("Category", "Request data error");
              });
          }
        })
        .catch((error) => {
          this.axiosRequestError("Get project", "Get project error");
          this.$router.push({ name: "projects" });
        })
        .finally(() => this.removeProcess(process));
    },
    onCreateDatasetClick() {
      if (this.createDataset.name.length < 1) return;
      const categories = [];

      for (let key in this.createDataset.categories) {
        categories.push(this.createDataset.categories[key]);
      }

      Datasets.create(this.createDataset.name, categories, this.identifier)
        .then(() => {
          this.createDataset.name = "";
          this.createDataset.categories = [];
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError(
            "Creating Dataset",
            error.response.data.message
          );
        });
    },
    onCreateCategoryClick() {
      if (this.createCategory.name.length < 1) return;
      const arr = [];
      if (this.createCategory.subcategory.length > 0) {
        const temp = this.createCategory.subcategory.map((x) => x.name);
        for (const item of Array.from(new Set(temp))) {
          arr.push({ name: item });
        }
      }

      Category.create({
        name: this.createCategory.name,
        supercategory: this.createCategory.supercategory,
        subcategory: arr,
        color: this.createCategory.color,
        classified: this.createCategory.isClassified,
        group: this.createCategory.group,
        project_id: this.project.id,
      })
        .then(() => {
          this.createCategory.name = "";
          this.createCategory.supercategory = "";
          this.createCategory.color = "";
          this.createCategory.isClassified = false;
          this.createCategory.subcategory = [];
          this.createCategory.group = "Labeling";
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError(
            "Creating Category",
            error.response.data.message
          );
        });
    },
    onCreateSubcategoryClick() {
      this.createCategory.subcategory.push({
        name: "",
      });
    },
    onRemoveSubcategoryClick(index) {
      this.createCategory.subcategory.splice(index, 1);
    },
    onTabClick(tab) {
      this.tab.selected = tab;
    },
  },
  watch: {
    user() {
      this.updatePage();
    },
    "tab.selected"(newVal, oldVal) {
      if (this.tab.selected === "datasets") {
        Datasets.getDatasets({
          page: this.dataset.page,
          limit: this.dataset.limit,
          project_id: this.project.id,
        })
          .then((response) => {
            this.dataset.datasets = response.data.datasets;
            this.dataset.categories = response.data.categories;
            this.dataset.subdirectories = response.data.subdirectories;
            this.dataset.pages = response.data.pagination.pages;
            this.dataset.page = response.data.pagination.page;

            AdminPanel.getUsers(this.dataset.limit).then((response) => {
              this.users = response.data.users;
            });
          })
          .catch((error) => {
            this.axiosRequestError(
              "Could not find datasets",
              "Loading datasets error"
            );
          });
      } else {
        Category.getCategories({
          page: this.category.page,
          limit: this.category.limit,
          project_id: this.project.id,
        })
          .then((response) => {
            this.category.categories = response.data.categories;
            this.category.page = response.data.pagination.page;
            this.category.pages = response.data.pagination.pages;
            this.category.categoryCount = response.data.pagination.total;
          })
          .catch((error) => {
            this.axiosRequestError("Category", "Request data error");
          });
      }
    },
    "category.pages"() {
      this.updatePage();
    },
    "dataset.pages"() {
      this.updatePage();
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    isVtcc() {
      return this.$store.getters["user/isVtcc"];
    },
    isFormValid() {
      return (
        this.createCategory.name.length !== 0 &&
        this.createCategory.group.length &&
        this.createCategory.subcategory.every((x) => x.name)
      );
    },
    directory() {
      let closing = this.createDataset.name.length > 0 ? "/" : "";
      return "/datasets/" + this.createDataset.name + closing;
    },
    categoryTags() {
      const tags = {};
      this.dataset.categories.forEach((category) => {
        tags[category.name] = category.name;
      });
      return tags;
    },
    user() {
      return this.$store.state.user.user;
    },
  },
  created() {
    if (this.user) {
      this.updatePage();
      localStorage.removeItem("pagination/page");
      localStorage.removeItem("dataset/tab");
      localStorage.removeItem("panel/showAnnotated");
      localStorage.removeItem("panel/showNotAnnotated");
    }
  },
  mounted() {
    this.setProject(null);
  },
};
</script>

<style scoped>
.help-icon {
  color: darkblue;
  font-size: 20px;
  display: inline;
}
</style>
