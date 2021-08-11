<template>
  <div>
    <div style="padding-top: 55px" />

    <div
      class="album py-5 bg-light"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="container">
        <h2 class="text-center">Projects</h2>

        <p class="text-center">
          Loaded <strong>{{ projects.length }}</strong> projects.
        </p>

        <div class="row justify-content-md-center">
          <div
            class="col-md-auto btn-group"
            role="group"
            style="padding-bottom: 20px"
          >
            <button
              v-if="isAdmin"
              type="button"
              class="btn btn-success"
              :disabled="!isAdmin"
              :class="{ disabled: !isAdmin }"
              data-toggle="modal"
              data-target="#createProject"
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
        </div>

        <hr />
        <p v-if="projects.length == 0" class="text-center">
          You need to create a project!
        </p>
        <div v-else style="background-color: gray">
          <!-- <Pagination :numPages="pages" @pagechange="updatePage" /> -->
          <div class="row bg-light">
            <ProjectCard
              v-for="project in projects"
              :key="project.id"
              :project="project"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="createProject">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Creating a Project</h5>
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
                <label>Project Name</label>
                <input
                  v-model="create.name"
                  class="form-control"
                  :class="{
                    'is-invalid': create.name.trim().length === 0,
                    'is-valid': true,
                  }"
                  placeholder="Dataset name"
                  required
                />
                <div class="invalid-feedback">
                  {{ "Project name is required" }}
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-primary"
              :disabled="create.name.trim().length === 0"
              :class="{ disabled: create.name.trim().length === 0 }"
              data-dismiss="modal"
              @click="createProject"
            >
              Create Project
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
import Project from "@/models/projects";
import AdminPanel from "@/models/admin";
import ProjectCard from "@/components/cards/ProjectCard";
import Pagination from "@/components/Pagination";
import TagsInput from "@/components/TagsInput";

import { mapMutations } from "vuex";

export default {
  name: "Projects",
  components: { Pagination, TagsInput, ProjectCard },
  mixins: [toastrs],
  data() {
    return {
      pages: 1,
      limit: 52,
      page: 1,
      create: {
        name: "",
        datasets: [],
      },
      datasets: [],
      users: [],
      projects: [],
    };
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess"]),
    updatePage(page) {
      const process = "Loading projects";
      this.addProcess(process);

      Project.getData()
        .then((response) => {
          this.projects = response.data;

          AdminPanel.getUsers(this.limit)
            .then((response) => {
              this.users = response.data.users;
            })
            .catch((error) =>
              this.axiosRequestError("Get Users", "Get users error")
            )
            .finally(() => this.removeProcess(process));
        })
        .catch((error) => {
          this.axiosRequestError(
            "Could not find projects",
            "Loading projects error"
          );
        });
    },
    createProject() {
      if (this.create.name.trim().length < 1) return;

      Project.create(this.create.name)
        .then(() => {
          this.create.name = "";
          this.create.categories = [];
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError(
            "Creating Project",
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
    isVtcc() {
      return this.$store.getters["user/isVtcc"];
    },
    user() {
      return this.$store.state.user.user;
    },
  },
  created() {
    if (this.user) {
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
