<template>
  <div v-if="isAdmin">
    <div style="padding-top: 55px" />
    <div
      class="album py-5 bg-light"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="container">
        <h2 class="text-center">Users</h2>
        <p class="text-center">
          Total of <strong>{{ total }}</strong> user accounts.
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
              data-toggle="modal"
              data-target="#createUser"
            >
              Create User
            </button>
            <button type="button" class="btn btn-secondary" @click="updatePage">
              Refresh
            </button>
          </div>
        </div>

        <div class="row justify-content-md-center" style="padding-bottom: 10px">
          <div class="col-md-2 text-right">
            <span>Limit</span>
          </div>
          <div class="col-md-2">
            <select
              v-model="limit"
              class="form-control form-control-sm text-inline"
            >
              <option>50</option>
              <option>100</option>
              <option>500</option>
              <option>1000</option>
            </select>
          </div>
        </div>

        <div>
          <table class="table table-hover table-sm">
            <thead class="remove-top-border">
              <tr>
                <th scope="col">Username</th>
                <th scope="col">Name</th>
                <th scope="col">Admin</th>
                <th scope="col">VTCC</th>
                <th class="text-center" scope="col">Edit</th>
                <th class="text-center" scope="col" @click="deleteUser(user)">
                  Delete
                </th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="(user, index) in users" :key="index">
                <td>{{ user.username }}</td>
                <td>{{ user.name }}</td>
                <td>
                  <i v-if="user.is_admin" class="fa fa-circle text-center" />
                  <i v-else class="fa fa-circle-thin text-center" />
                </td>
                <td>
                  <i v-if="user.is_vtcc" class="fa fa-circle text-center" />
                  <i v-else class="fa fa-circle-thin text-center" />
                </td>
                <td>
                  <i
                    class="fa fa-pencil text-center edit-icon"
                    @click="editUser(user)"
                  />
                </td>
                <td>
                  <i
                    class="fa fa-remove text-center delete-icon"
                    @click="deleteUser(user)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div
      v-for="(user, idx) in users"
      :key="idx"
      class="modal fade"
      tabindex="-1"
      role="dialog"
      :id="'editUser' + user.username"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit a User</h5>
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
                :class="{ 'was-validated': user.name.length !== 0 }"
              >
                <label>Name</label>
                <input
                  v-model="user.name"
                  class="form-control"
                  :class="{ 'is-invalid': !user.name }"
                  placeholder="Name"
                  required
                />
              </div>

              <!-- <div
                class="form-group"
                :class="{ 'was-validated': (edit.password === edit.confirmPassword) }"
              >
                <label>New Password</label>
                <input
                  type="password"
                  v-model="edit.password"
                  class="form-control"
                  :class="{ 'is-invalid': (edit.password !== edit.confirmPassword) }"
                  placeholder="Enter Password"
                  required
                />
              </div>

              <div
                class="form-group"
                :class="{ 'was-validated': (edit.password === edit.confirmPassword) }"
              >
                <label>Confirm New Password</label>
                <input
                  type="password"
                  v-model="edit.confirmPassword"
                  class="form-control"
                  :class="{ 'is-invalid': (edit.password !== edit.confirmPassword) }"
                  placeholder="Re-enter New Password"
                  required
                />
              </div> -->

              <div class="form-check">
                <input
                  v-model="user.is_admin"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Admin</label>
              </div>

              <div class="form-check">
                <input
                  v-model="user.is_vtcc"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">VTCC</label>
              </div>

              <div class="modal-footer">
                <!-- <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="!(user.name.length > 0 && edit.password === edit.confirmPassword && edit.password)"
                  :class="{disabled: !(user.name.length > 0  && edit.password === edit.confirmPassword && edit.password)}"
                  @click="saveEdit"
                  data-dismiss="modal"
                > -->
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="!(user.name.length > 0)"
                  :class="{ disabled: !(user.name.length > 0) }"
                  @click="saveEdit(user)"
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
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="createUser">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create a User</h5>
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
                :class="{
                  'was-validated':
                    create.username.length !== 0 &&
                    !create.username.includes('.') &&
                    !create.username.includes(' ') &&
                    !create.username.includes('$'),
                }"
              >
                <label>Username</label>
                <input
                  v-model="create.username"
                  class="form-control"
                  :class="{ 'is-invalid': !create.username }"
                  placeholder="Username"
                  required
                />
              </div>
              <div
                class="form-group"
                :class="{ 'was-validated': create.password.length !== 0 }"
              >
                <label>Password</label>
                <input
                  type="password"
                  v-model="create.password"
                  class="form-control"
                  placeholder="Password"
                  required
                />
              </div>
              <div
                class="form-group"
                :class="{
                  'was-validated':
                    create.name.length !== 0 &&
                    !create.name.includes('.') &&
                    !create.name.includes(' ') &&
                    !create.name.includes('$'),
                }"
              >
                <label>Name</label>
                <input
                  v-model="create.name"
                  class="form-control"
                  :class="{ 'is-invalid': !create.name }"
                  placeholder="Name"
                  required
                />
              </div>

              <div class="form-check">
                <input
                  v-model="create.isAdmin"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">Admin</label>
              </div>

              <div class="form-check">
                <input
                  v-model="create.isVtcc"
                  type="checkbox"
                  class="form-check-input"
                />
                <label class="form-check-label">VTCC</label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!isFormValid"
              :class="{ disabled: !isFormValid }"
              @click="createUser"
              data-dismiss="modal"
            >
              Create User
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

    <!-- <div class="modal fade" tabindex="-1" role="dialog" id="editUser">
      <div class="modal-dialog" role="document">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">Edit a User</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>

        </div>
      </div>
    </div> -->
  </div>
</template>

<script>
import AdminPanel from "@/models/admin";
import toastrs from "@/mixins/toastrs";
import { mapMutations } from "vuex";
import JQuery from "jquery";
const $ = JQuery;

export default {
  name: "AdminPanel",
  mixins: [toastrs],
  data() {
    return {
      users: [],
      limit: 50,
      total: 0,
      create: {
        name: "",
        username: "",
        password: "",
        isAdmin: false,
        isVtcc: false,
      },
      edit: {
        password: "",
        confirmPassword: "",
      },
    };
  },
  methods: {
    ...mapMutations(["addProcess", "removeProcess"]),
    updatePage() {
      const process = "Loading users";
      this.addProcess(process);

      AdminPanel.getUsers(this.limit)
        .then((response) => {
          this.users = response.data.users;
          this.total = response.data.total;
        })
        .finally(() => this.removeProcess(process));
    },
    createUser(event) {
      event.preventDefault();
      AdminPanel.createUser(this.create)
        .then(this.updatePage)
        .catch((error) => {
          this.axiosRequestError("Create User", "Create User Error");
        });

      this.create.username = "";
      this.create.name = "";
      this.create.password = "";
      this.create.isAdmin = false;
      this.create.isVtcc = false;
    },
    editUser(user) {
      $("#editUser" + user.username).modal("show");
    },
    saveEdit(user) {
      AdminPanel.editUser(user)
        .then((response) => {
          this.updatePage();
        })
        .catch((error) => {
          this.axiosRequestError("Edit User", "Edit User Error");
        });
    },
    deleteUser(user) {
      let yes = confirm(
        "Are you sure you want to delete " +
          user.username +
          ". This action cannot be undone."
      );
      if (!yes) return;

      AdminPanel.deleteUser(user.username)
        .then(this.updatePage)
        .catch((error) => {
          this.axiosRequestError("Create User", error.response.data.message);
        });
    },
  },
  computed: {
    isFormValid() {
      // console.log(
      //   this.create.username.length > 0 &&
      //     !this.create.username.includes(".") &&
      //     !this.create.username.includes(" ") &&
      //     !this.create.username.includes("$") &&
      //     this.create.name.length > 0 &&
      //     this.create.password.length > 0
      // );

      return (
        this.create.username.length > 0 &&
        !this.create.username.includes(".") &&
        !this.create.username.includes(" ") &&
        !this.create.username.includes("$") &&
        this.create.name.length > 0 &&
        this.create.password.length > 0
      );
    },
    isAdmin() {
      return this.$store.getters["user/isAdmin"];
    },
  },
  watch: {
    limit: "updatePage",
  },
  created() {
    if (!this.isAdmin) this.$router.push({ path: "*" });
    else this.updatePage();
  },
};
</script>

<style scoped>
.remove-top-border {
  border: none !important;
}

.fa {
  margin: 0;
  padding: 2px;
}

.edit-icon:hover {
  color: green;
}

.delete-icon:hover {
  color: red;
}
</style>
