import axios from "axios";

export default {
    getProject(id) {
        return axios.get('/tagging/api/project/' + id)
    },
    getData() {
        return axios.get('/tagging/api/project/');
    },
    create(name) {
        return axios.post(`/tagging/api/project/?name=${name}`);
    },
    update(id, name) {
        return axios.post("/tagging/api/project/" + id, {
            name: name
        })
    },
    share(id, sharedUsers) {
        return axios.post("/tagging/api/project/" + id + "/share", {
            users: sharedUsers
        })
    },
    delete(id) {
        return axios.delete("/tagging/api/project/" + id)
    }
}