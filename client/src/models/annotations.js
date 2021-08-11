import axios from "axios";

const baseURL = "/tagging/api/annotation/";

export default {
  create(annotation) {
    return axios.post(baseURL, annotation);
  },
  delete(id) {
    return axios.delete(`${baseURL}${id}`);
  },
  update(id, newParams) {
    return axios.put(`${baseURL}${id}`, newParams);
  },
  createLabel(annotation) {
    return axios.post(`${baseURL}label`, annotation);
  },
  // getLabel(image_id, category_id) {
  //   return axios.get(`${baseURL}label?image_id=${image_id}&category_id=${category_id}`);
  // },
};