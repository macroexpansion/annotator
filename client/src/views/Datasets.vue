<template>
  <div v-if="isAdmin">
    <div style="padding-top: 55px" />

    <div
      class="album py-5 bg-light"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="container">
        <h2 class="text-center">Datasets</h2>

        <p class="text-center">
          Loaded <strong>{{ datasets.length }}</strong> datasets.
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
              data-target="#createDataset"
            >
              Create
            </button>
            <button
              type=" button"
              class="btn btn-secondary"
              @click="updatePage(page)"
            >
              Refresh
            </button> 
          </div>
        </div> -->

        <hr />
        <p v-if="datasets.length < 1" class="text-center">
          You need to create a dataset!
        </p>
        <div v-else style="background-color: gray">
          <Pagination :numPages="pages" @pagechange="updatePage" />
          <div class="row bg-light">
            <DatasetCard
              v-for="dataset in datasets"
              :key="dataset.id"
              :dataset="dataset"
              :categories="categories"
            />
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
              <div
                class="form-group"
                :class="{ 'was-validated': validDatasetName.length !== 0 }"
              >
                <label>Dataset Name</label>
                <input
                  v-model="create.name"
                  class="form-control"
                  placeholder="Dataset name"
                  required
                />
                <div class="invalid-feedback">
                  {{ validDatasetName }}
                </div>
              </div>

              <div class="form-group">
                <label>Default Categories</label>
                <TagsInput
                  v-model="create.categories"
                  element-id="createCategory"
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
              data-dismiss="modal"
              @click="createDataset"
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
  </div>
</template>

<script>
import toastrs from "@/mixins/toastrs";
import Datasets from "@/models/datasets";
import AdminPanel from "@/models/admin";
import DatasetCard from "@/components/cards/DatasetCard";
import Pagination from "@/components/Pagination";
import TagsInput from "@/components/TagsInput";

import { mapMutations } from "vuex";

export default {
  name: "Datasets",
  components: { DatasetCard, Pagination, TagsInput },
  mixins: [toastrs],
  data() {
    return {
      pages: 1,
      limit: 52,
      page: 1,
      create: {
        name: "",
        categories: [],
      },
      datasets: [],
      subdirectories: [],
      categories: [],
      users: [],
    };
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess"]),
    updatePage(page) {
      const process = "Loading datasets";
      this.addProcess(process);

      Datasets.allData({
        limit: this.limit,
        page: page,
      })
        .then((response) => {
          this.datasets = response.data.datasets;
          console.log(datasets);
          this.categories = response.data.categories;
          this.subdirectories = response.data.subdirectories;
          this.pages = response.data.pagination.pages;
          this.page = response.data.pagination.page;

          AdminPanel.getUsers(this.limit)
            .then((response) => {
              this.users = response.data.users;
            })
            .finally(() => this.removeProcess(process));
        })
        .catch((error) => {
          this.axiosRequestError(
            "Could not find requested image",
            "Loading datasets error"
          );
        });
    },
    createDataset() {
      if (this.create.name.length < 1) return;
      let categories = [];

      for (let key in this.create.categories) {
        categories.push(this.create.categories[key]);
      }

      Datasets.create(this.create.name, categories)
        .then(() => {
          this.create.name = "";
          this.create.categories = [];
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError(
            "Creating Dataset",
            error.response.data.message
          );
        });
    },
  },
  watch: {
    user() {
      this.updatePage();
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    directory() {
      let closing = this.create.name.length > 0 ? "/" : "";
      return "/datasets/" + this.create.name + closing;
    },
    categoryTags() {
      let tags = {};
      this.categories.forEach((category) => {
        tags[category.name] = category.name;
      });
      return tags;
    },
    validDatasetName() {
      if (this.create.name.length === 0) return "Dataset name is required";
      return "";
    },
    user() {
      return this.$store.state.user.user;
    },
  },
  created() {
    if (!this.isAdmin) {
      this.$router.push({ path: "*" });
    } else if (this.user) {
      this.updatePage();
    }
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
