<template>
  <div class="form-inline my-2 my-lg-0" style="margin-right: 10px">
    <div class="btn-group open">
      <a
        class="btn btn-primary"
        href="#"
        role="button"
        id="dropdownMenuLink"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        style="
          max-width: 20em;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        "
        ><i class="fa fa-user fa-fw"></i>
        {{ displayUsername }}
      </a>
      <a
        class="btn btn-primary dropdown-toggle"
        data-toggle="dropdown"
        href="#"
      ></a>

      <ul
        class="dropdown-menu dropdown-menu-right"
        aria-labelledby="dropdownMenuLink"
        role="menu"
      >
        <li>
          <a
            v-show="$store.getters['user/isAdmin']"
            class="dropdown-item"
            href="#"
          >
            <RouterLink class="route" :to="`/admin`">Admin Panel</RouterLink>
          </a>
        </li>
        <li>
          <a class="dropdown-item" href="#">
            <RouterLink class="route" :to="`/user`">User Settings</RouterLink>
          </a>
        </li>
        <li>
          <a class="dropdown-item" href="#" @click="logoutButton">Logout</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  name: "User",
  methods: {
    ...mapActions("user", ["logout"]),
    logoutButton() {
      localStorage.removeItem("dataset/tab");
      if (this.$route.name === "annotate") {
        this.$router.replace({ name: "auth" }, this.logout);
        return;
      }
      this.logout();
    },
  },
  computed: {
    user() {
      return this.$store.state.user.user;
    },
    displayUsername() {
      if (!this.user) return "";
      return this.user.name.length === 0 ? this.user.username : this.user.name;
    },
  },
};
</script>

<style scoped>
a:hover {
  text-decoration: none;
}
.route {
  color: black;
}
</style>
