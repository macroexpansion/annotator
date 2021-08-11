<template>
  <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
    <i
      class="fa fa-circle"
      :style="{ color: color }"
      style="padding: 0 10px; font-size: 10px"
      v-tooltip="backendStatus"
    ></i>

    <RouterLink class="navbar-brand" :to="`/`">
      <strong>{{ name }}</strong>
      <!-- <span class="subscript">{{ version }}</span> -->
    </RouterLink>

    <button
      class="navbar-toggler"
      type="button"
      data-toggle="collapse"
      data-target="#navbarSupportedContent"
      aria-controls="navbarSupportedContent"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon" />
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item" :class="{ active: $route.name === 'projects' }">
          <RouterLink class="nav-link" :to="`/projects`">Projects</RouterLink>
        </li>

        <li
          class="nav-item"
          v-show="
            $route.name === 'project' ||
            $route.name === 'dataset' ||
            $route.name === 'annotate'
          "
          :class="{
            active:
              $route.name === 'project' ||
              $route.name === 'dataset' ||
              $route.name === 'annotate',
          }"
        >
          <RouterLink class="nav-link" :to="`/project/${project.id}`">
            Current Project
          </RouterLink>
        </li>

        <li
          class="nav-item"
          v-show="$route.name === 'annotate'"
          :class="{ active: $route.name === 'annotate' }"
        >
          <!-- <RouterLink class="nav-link" :to="`/dataset/${dataset.id}`">
            Current Dataset
          </RouterLink> -->
          <RouterLink
            class="nav-link"
            :to="{ name: 'dataset', params: { identifier: dataset.id } }"
          >
            Current Dataset
          </RouterLink>
        </li>

        <li
          class="nav-item"
          v-show="$route.name === 'annotate' && $store.state.folders.length > 0"
          :class="{ active: $route.name === 'annotate' }"
          @click="onClickDirectory"
        >
          <RouterLink class="nav-link" :to="`/dataset/${dataset.id}`">
            Current Directory
          </RouterLink>
        </li>

        <li
          v-if="isAdmin"
          class="nav-item"
          :class="{ active: $route.name === 'datasets' }"
        >
          <RouterLink class="nav-link" :to="`/datasets`">Datasets</RouterLink>
        </li>

        <li
          v-if="isAdmin"
          class="nav-item"
          :class="{ active: $route.name === 'categories' }"
        >
          <RouterLink class="nav-link" :to="`/categories`"
            >Categories</RouterLink
          >
        </li>

        <li
          v-if="isAdmin"
          class="nav-item"
          :class="{ active: $route.name === 'undo' }"
        >
          <RouterLink class="nav-link" :to="`/undo`">Undo</RouterLink>
        </li>

        <li
          v-if="isAdmin"
          class="nav-item"
          :class="{ active: $route.name === 'tasks' }"
        >
          <RouterLink class="nav-link" :to="`/tasks`">Tasks</RouterLink>
        </li>

        <li
          v-if="isAdmin"
          class="nav-item"
          :class="{ active: $route.name === 'admin' }"
        >
          <RouterLink class="nav-link d-none d-xl-block" :to="`/admin`">
            Admin
          </RouterLink>
        </li>
      </ul>
      <!-- <Status class="nav-link left" /> -->
      <User class="nav-link left" v-if="loginEnabled" />
    </div>
  </nav>
</template>

<script>
import User from "@/components/User";
import Status from "@/components/Status";
import { mapMutations } from "vuex";

export default {
  name: "NavBar",
  components: { Status, User },
  data() {
    return {
      color: "white",
      backendStatus: "Connection unknown",
    };
  },
  methods: {
    ...mapMutations(["setFolders", "setToFolders"]),
    onClickDirectory() {
      this.setToFolders(true);
    },
  },
  computed: {
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
    version() {
      return this.$store.state.info.version;
    },
    loginEnabled() {
      return this.$store.state.info.loginEnabled;
    },
    name() {
      return this.$store.state.info.name;
    },
    socket() {
      return this.$store.state.info.socket;
    },
    dataset() {
      const dataset = this.$store.state.dataset;
      if (dataset == null) return { name: "", id: "" };

      return dataset;
    },
    project() {
      const project = this.$store.state.project;
      if (project == null) return { name: "", id: "" };

      return project;
    },
  },
  watch: {
    socket(connected) {
      if (connected == null) {
        this.color = "white";
        this.backendStatus = "Connection unknown";
        return;
      }

      if (connected) {
        this.color = "green";
        this.backendStatus = "Connected to backend";
      } else {
        this.color = "red";
        this.backendStatus = "Could not connect to backend";
      }
    },
  },
  create() {
    // console.log(this.$store.state.folders)
  },
};
</script>

<style scoped>
.subscript {
  padding: 10px;
  font-size: 10px;
  color: lightgray;
}

.navbar {
  background-color: #383c4a;
}

.left {
  padding: 0;
}
</style>
