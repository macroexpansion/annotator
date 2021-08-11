import axios from "axios";

const baseURL = "/tagging/api/dataset";

export default {
  allData(params) {
    return axios.get(`${baseURL}/data`, {
      params: {
        ...params
      }
    });
  },
  getDatasets(params) {
    return axios.get(`${baseURL}/datasets`, {
      params: {
        ...params
      }
    });
  },
  getData(id, params) {
    return axios.get(`${baseURL}/${id}/data`, {
      params: {
        ...params
      }
    });
  },
  create(name, categories, project_id) {
    return axios.post(`${baseURL}/?name=${name}`, {
      categories: categories,
      project_id: project_id
    });
  },
  generate(id, body) {
    return axios.post(`${baseURL}/${id}/generate`, {
      ...body
    });
  },
  scan(id) {
    return axios.get(`${baseURL}/${id}/scan`);
  },
  uploadFiles(id, files, upload_id, scan_id, crop) {
    let form = new FormData();
    files.forEach(file => {
      form.append("upload", file);
    })

    return axios.post(`${baseURL}/${id}/images`, form, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
      params: {
        upload_id: upload_id,
        scan_id: scan_id,
        crop: crop
      }
    });
  },
  uploadFolders(id, files, upload_id, scan_id, crop) {
    let form = new FormData();
    files.forEach(file => {
      form.append("upload", file);
    })

    return axios.post(`${baseURL}/${id}/folders`, form, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
      params: {
        upload_id: upload_id,
        scan_id: scan_id,
        crop: crop
      }
    });
  },
  exportingCOCO(id, categories, user) {
    return axios.get(`${baseURL}/${id}/export?categories=${categories}`, {
      params: {
        user: user
      }
    });
  },
  getCoco(id) {
    return axios.get(`${baseURL}/${id}/coco`);
  },
  uploadCoco(id, file) {
    let form = new FormData();
    form.append("coco", file);

    return axios.post(`${baseURL}/${id}/coco`, form, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },
  export(id, format) {
    return axios.get(`${baseURL}/${id}/${format}`);
  },
  getUsers(id) {
    return axios.get(`${baseURL}/${id}/users`);
  },
  getStats(id) {
    return axios.get(`${baseURL}/${id}/stats`);
  },
  getExports(id) {
    return axios.get(`${baseURL}/${id}/exports`);
  },
  resetMetadata(id) {
    return axios.get(`${baseURL}/${id}/reset/metadata`);
  }
};
