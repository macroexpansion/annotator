import axios from "axios";

const baseURL = "/tagging/api/admin/";

export default {
  getUsers(limit) {
    return axios.get(baseURL + `users?limit=${limit}`);
  },
  editUser(user) {
    return axios.patch(baseURL + `user/${user.username}`, { ...user });
  },
  createUser(user) {
    return axios.post(baseURL + "user", { ...user });
  },
  deleteUser(username) {
    return axios.delete(baseURL + `user/${username}`);
  }
};
