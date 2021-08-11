<template>
  <div class="bg-light">
    <div style="padding-top: 55px" />
    <div
      class="album py-5 container"
      style="overflow: auto; height: calc(100vh - 55px)"
    >
      <div class="row">
        <div class="col-sm text-left">
          <!-- Change this section to whatever you would like -->
          <h1>WELCOME TO VIETTEL MEDICAL DATA CENTER (VT-MDC)</h1>
          <hr />
          <div v-if="totalUsers === 0">
            <p>Use the registration form to create an admin account</p>
          </div>
          <div v-else>
            <p>
              VT-MDC is created to support the research and development of computer-aided diagnosis using AI.
              <br /><br />
              Login to create a datasets.
              <br /><br />
            </p>
          </div>
          <!-- End of section -->
        </div>
        <div class="col-sm">
          <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item" v-show="totalUsers !== 0">
              <a
                class="nav-link"
                :class="{ active: tab === 'login' }"
                data-toggle="tab"
                href="#login"
                role="tab"
                aria-controls="home"
                aria-selected="true"
                @click="tab = 'login'"
              >
                Login
              </a>
            </li>

            <li class="nav-item" v-show="showRegistrationForm">
              <a
                class="nav-link"
                :class="{ active: tab === 'register' }"
                data-toggle="tab"
                href="#register"
                role="tab"
                aria-controls="contact"
                aria-selected="false"
                @click="tab = 'register'"
                ref="registerTab"
              >
                Register
              </a>
            </li>
          </ul>
          <div
            class="tab-content panel border-bottom border-right border-left text-left"
          >
            <div
              class="tab-pane fade show active"
              id="login"
              role="tabpanel"
              aria-labelledby="login-tab"
            >
              <form class="vld-parent" ref="loginForm">
                <div class="form-group">
                  <label>Username</label>
                  <input
                    v-model="loginForm.username"
                    type="text"
                    class="form-control"
                    required
                  />
                  <div class="invalid-feedback">Invalid username format</div>
                </div>
                <div class="form-group">
                  <label>Password</label>
                  <input
                    v-model="loginForm.password"
                    type="password"
                    class="form-control"
                  />
                </div>
                <button
                  type="submit"
                  class="btn btn-primary btn-block"
                  :class="{ disabled: !loginValid }"
                  @click.prevent="loginUser"
                >
                  Login
                </button>
              </form>
            </div>
            <div
              class="tab-pane fade"
              id="register"
              role="tabpanel"
              aria-labelledby="register-tab"
            >
              <div v-if="totalUsers !== 0">
                You are not allowed to register new accounts.
              </div>
              <form v-else class="vld-parent" ref="registerForm">
                <div class="form-group" novalidate="">
                  <label
                    >Full Name <span class="text-mute">(Optional)</span></label
                  >
                  <input
                    v-model="registerForm.name"
                    type="text"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label>Username</label>
                  <input
                    v-model="registerForm.username"
                    :class="inputUsernameClasses(registerForm.username)"
                    type="text"
                    class="form-control"
                    required
                  />
                  <div class="invalid-feedback">Invalid username format</div>
                </div>

                <div class="form-group">
                  <label>Password</label>
                  <input
                    v-model="registerForm.password"
                    :class="inputPasswordClasses(registerForm.password)"
                    type="password"
                    class="form-control"
                    required
                  />
                  <div class="invalid-feedback">
                    Minimum length of 5 characters.
                  </div>
                </div>

                <div class="form-group">
                  <label>Confirm Password</label>
                  <input
                    v-model="registerForm.confirmPassword"
                    :class="{
                      'is-valid':
                        registerForm.confirmPassword.length > 0 &&
                        registerForm.confirmPassword === registerForm.password
                    }"
                    type="password"
                    class="form-control"
                  />
                </div>
                <button
                  type="submit"
                  class="btn btn-primary btn-block"
                  :class="{ disabled: !registerValid }"
                  @click.prevent="registerUser"
                >
                  Register
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import toastrs from "@/mixins/toastrs";
import { mapActions, mapMutations } from "vuex";
export default {
  name: "Authentication",
  mixins: [toastrs],
  props: {
    redirect: {
      type: Object,
      default() {
        return { name: "projects" };
      }
    }
  },
  data() {
    return {
      tab: "login",
      registerForm: {
        loading: false,
        name: "",
        username: "",
        password: "",
        confirmPassword: ""
      },
      loginForm: {
        loading: false,
        username: "",
        password: ""
      }
    };
  },
  methods: {
    ...mapActions("user", ["register", "login"]),
    ...mapMutations("info", ["increamentUserCount"]),
    /**
     * Reigsters a user with provided infomation from login form
     */
    registerUser() {
      if (!this.registerValid) return;

      const loader = this.$loading.show({
        container: this.$refs.registerForm,
        color: "#383c4a"
      });

      const data = {
        user: this.registerForm,
        successCallback: () => {
          setTimeout(() => loader.hide(), 500);
          this.increamentUserCount();
          this.$router.push(this.redirect);
        },
        errorCallback: error => {
          this.axiosRequestError(
            "User Registration",
            error.response.data.message
          )
          setTimeout(() => loader.hide(), 1000);
        }
      };

      this.register(data);
    },
    /**
     * Login a user with provided infomation from login form
     */
    loginUser() {
      if (!this.loginValid) return;

      const loader = this.$loading.show({
        container: this.$refs.registerForm,
        color: "#383c4a"
      });

      const data = {
        user: this.loginForm,
        successCallback: () => {
          setTimeout(() => loader.hide(), 400);
          this.$router.push(this.redirect);
        },
        errorCallback: error => {
          this.axiosRequestError("User Login", error.response.data.message);
          setTimeout(() => loader.hide(), 1000);
        }
      };
      this.login(data);
    },
    /**
     * Returns boolean value if provide string is a valid username
     * @param {string} username
     * @returns {boolean} true if valid otherwise false
     */
    validUsername(username) {
      return /^[0-9a-zA-Z_.-]+$/.test(username);
    },
    /**
     * Returns boolean value if provide string is a valid password
     * @param {string} password
     * @returns {boolean} true if valid otherwise false
     */
    validPassword(password) {
      return password.length > 5;
    },
    /**
     * Returns classes to be applied to a username input field for validation
     * @param {string} username input username string
     * @returns {object} validation classes
     */
    inputUsernameClasses(username) {
      const isValid = this.validUsername(username);

      return {
        "is-invalid": !isValid && username.length != 0,
        "is-valid": isValid
      };
    },
    /**
     * Returns classes to be applied to a password input field for validation
     * @param {string} password input password string
     * @returns {object} validation classes
     */
    inputPasswordClasses(password) {
      const isValid = password.length > 4;

      return {
        "is-invalid": !isValid && password.length != 0,
        "is-valid": isValid
      };
    }
  },
  computed: {
    registerValid() {
      if (!this.validUsername(this.registerForm.username)) return false;
      if (this.registerForm.password.length < 5) return false;
      if (this.registerForm.password !== this.registerForm.confirmPassword)
        return false;

      return true;
    },
    loginValid() {
      if (!this.validUsername(this.loginForm.username)) return false;
      if (this.loginForm.password.length == 0) return false;
      return true;
    },
    totalUsers() {
      return this.$store.state.info.totalUsers;
    },
    allowRegistration() {
      return this.$store.state.info.allowRegistration;
    },
    showRegistrationForm() {
      return this.totalUsers == 0 || this.allowRegistration;
      // return this.totalUsers === 0;
    },
    isAuthenticatePending() {
      return this.$store.state.user.isAuthenticatePending;
    }
  },
  watch: {
    totalUsers(users) {
      if (users === 0) {
        this.$refs.registerTab.click();
      }
    },
    isAuthenticatePending: {
      handler() {
        if (this.isAuthenticatePending) {
          this.$router.push({
            name: "projects"
          });
        }
      },
      immediate: true
    }
  },
  mounted() {}
};
</script>

<style scoped>
.panel {
  padding: 30px;
  background-color: white;
}

.text-mute {
  font-size: 10px;
}

.btn-button {
  margin-top: 10px;
}
</style>
