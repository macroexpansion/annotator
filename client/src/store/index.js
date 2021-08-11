import Vue from "vue";
import Vuex from "vuex";
import createPersistedState from "vuex-persistedstate";

import user from "./user";
import info from "./info";
import review from "./review";

const dataState = createPersistedState({
  paths: ['user', 'review', 'project', 'folders', 'toFolders']
})

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    user,
    info,
    review
  },
  plugins: [dataState],
  state: {
    process: [],
    undo: [],
    dataset: "",
    project: "",
    folders: [],
    toFolders: false
  },
  mutations: {
    setToFolders(state, val) {
      state.toFolders = val;
    },
    setFolders(state, folders) {
      state.folders = folders;
    },
    setDataset(state, dataset) {
      state.dataset = dataset;
    },
    setProject(state, project) {
      state.project = project;
    },
    addProcess(state, process) {
      state.process.push(process);
    },
    removeProcess(state, process) {
      let index = state.process.indexOf(process);
      if (index > -1) {
        state.process.splice(index, 1);
      }
    },
    resetUndo(state) {
      state.undo = [];
    },
    addUndo(state, action) {
      state.undo.push(action);
    },
    undo(state) {
      let action = state.undo.pop();
      if (action != null) {
        action.undo();
      }
    },
    removeUndos(state, action) {
      state.undo = state.undo.filter(undo => undo.action !== action);
    }
  },
  actions: {}
});
