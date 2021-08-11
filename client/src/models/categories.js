import axios from "axios";

const baseURL = "/tagging/api/category/";

export default {
  allData(params) {
    return axios.get(baseURL + "data", {
      params: {
        ...params
      }
    });
  },
  getCategories(params) {
    return axios.get(baseURL + 'categories', {
      params: {
        ...params
      }
    })
  },
  create(create) {
    return axios.post(baseURL, { ...create }, {
      'Content-Type': 'application/json'
    });
  }
};
