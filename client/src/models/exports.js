import axios from "axios";

const baseURL = "/tagging/api/export";

export default {
  download(id, dataset) {
    axios({
      url: `${baseURL}/${id}/download`,
      method: "GET",
      responseType: "blob"
    })
      .then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${dataset}.zip`);
        document.body.appendChild(link);
        link.click();
      });
  },
  delete(id) {
    return axios.delete(`${baseURL}/${id}`)
  }
};
