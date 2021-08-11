<template>
  <div class="col-md-3">
    <!-- Dataset Card -->
    <div class="card mb-4 box-shadow">
      <!-- Display Image -->
      <img
        @click="onImageClick"
        :src="imageUrl"
        class="card-img-top"
        @error="imageError = true"
        style="width: 100%; display: block"
      />
      <!-- Card Body -->
      <div class="card-body">
        <span
          class="d-inline-block text-truncate"
          style="max-width: 100%; float: left"
        >
          <strong class="card-title">{{ project.name }}</strong>
        </span>

        <i
          v-if="isAdmin"
          class="card-text fa fa-ellipsis-v fa-lg icon-more"
          :id="'dropdownProject' + project.id"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
          aria-hidden="true"
        />

        <br />
        <br />

        <div v-if="isAdmin" class="flex-body-dataset-card">
          <div style="flex-shrink: 0">
            <p class="card-text" v-if="sharedUsers.length > 0">
              <small class="text-muted"> Shared with </small>
            </p>
            <span
              v-for="user in sharedUsers"
              :key="user"
              class="badge badge-pill badge-secondary category-badge"
            >
              {{ user }}
            </span>
          </div>
          <br />
          <!-- <div style="flex-shrink: 0;" v-if="project.datasets.length > 0">
            <p class="para">{{ project.datasets.length }}</p>
          </div>

          <p v-else class="para">No dataset in project.</p> -->
        </div>

        <div
          v-if="isAdmin"
          class="dropdown-menu"
          :aria-labelledby="'dropdownProject' + project.id"
        >
          <button
            class="dropdown-item"
            data-toggle="modal"
            :data-target="'#projectEdit' + project.id"
          >
            Edit
          </button>
          <button
            class="dropdown-item"
            data-toggle="modal"
            :data-target="'#projectShare' + project.id"
          >
            Share
          </button>
          <hr />
          <button class="dropdown-item delete" @click="onDeleteClick">
            Delete
          </button>
        </div>
      </div>

      <div v-if="isAdmin" class="card-footer text-muted">
        Created by <b>{{ project.owner }}</b>
      </div>
    </div>

    <!-- Edit Project -->
    <div class="modal fade" role="dialog" :id="'projectEdit' + project.id">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ project.name }}</h5>
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
                  v-model="update.name"
                  class="form-control"
                  :class="{
                    'is-invalid': update.name.trim().length === 0,
                    'is-valid': true,
                  }"
                  required="true"
                  placeholder="Name"
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
              class="btn btn-success"
              :disabled="update.name.trim().length === 0"
              :class="{ disabled: update.name.trim().length === 0 }"
              @click="onSave"
              data-dismiss="modal"
            >
              Save
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

    <!-- Share Project -->
    <div class="modal fade" role="dialog" :id="'projectShare' + project.id">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ project.name }}</h5>
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
                <label>Users shared with</label>
                <TagsInput
                  v-model="sharedUsers"
                  element-id="usersList"
                  :existing-tags="users"
                  :typeahead="true"
                  :typeahead-activation-threshold="0"
                  placeholder="Add usernames"
                />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-success"
              @click="onShare"
              data-dismiss="modal"
            >
              Save
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
import axios from "axios";
import Project from "@/models/projects";
import Metadata from "@/components/Metadata";
import TagsInput from "@/components/TagsInput";

import { mapMutations } from "vuex";

export default {
  name: "ProjectCard",
  components: { TagsInput },
  mixins: [toastrs],
  props: {
    project: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      imageError: false,
      selectedCategories: [],
      noImageUrl: require("@/assets/no-image.png"),
      notFoundImageUrl: require("@/assets/404-image.png"),
      sharedUsers: [],
      update: {
        name: this.project.name,
      },
    };
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess"]),
    onImageClick() {
      const identifier = this.project.id;
      this.$router.push({ name: "project", params: { identifier } });
    },
    onShare() {
      this.project.users = this.sharedUsers;

      Project.share(this.project.id, this.sharedUsers)
        .then(() => {
          this.$parent.updatePage();
        })
        .catch((error) =>
          this.axiosRequestError("Share user", "Share user error")
        );
    },
    onDeleteClick() {
      Project.delete(this.project.id).then(() => {
        this.$parent.updatePage();
      });
    },
    onSave() {
      Project.update(this.project.id, this.update.name)
        .then(() => {
          this.$parent.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError("Project update", "Update project error");
        });
    },
    createSelectedUsers() {
      this.sharedUsers = this.project.users;
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    imageUrl() {
      if (this.imageError) return this.noImageUrl;
      else
        return "/tagging/api/image/project/" + this.project.id + "?width=250";

      return this.noImageUrl;
    },
    users() {
      let users = {};
      this.$parent.users.forEach((user) => {
        users[user.username] = user.username;
      });

      return users;
    },
  },
  mounted() {
    this.createSelectedUsers();
  },
};
</script>

<style scoped>
.card-img-overlay {
  padding: 0 10px 0 0;
}

.card-body {
  padding: 10px 10px 0 10px;
}

p {
  margin: 0;
  padding: 0 0 3px 0;
}

.category-badge {
  float: left;
  margin: 0 2px 5px 0;
}

.list-group-item {
  height: 21px;
  font-size: 13px;
  padding: 2px;
  background-color: #4b5162;
}

.icon-more {
  width: 10%;
  margin: 3px 0;
  padding: 0;
  float: right;
  color: black;
}

.progress {
  margin: 0 5px 7px 5px;
  height: 5px;
}

.card-footer {
  padding: 2px;
  font-size: 11px;
}

.delete {
  color: darkred;
}

.para {
  margin-top: 4px;
  margin-bottom: 4px;
}

.flex-body-dataset-card {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex: 0 0 100%;
  float: left;
}
</style>
