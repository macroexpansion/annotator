import Vue from "vue";
import Router from "vue-router";

import About from "@/views/About";
import Annotator from "@/views/Annotator";
import AdminPanel from "@/views/AdminPanel";
import Datasets from "@/views/Datasets";
import Categories from "@/views/Categories";
import Undo from "@/views/Undo";
import Dataset from "@/views/Dataset";
import Auth from "@/views/Auth";
import User from "@/views/User";
import Tasks from "@/views/Tasks";
import PageNotFound from "@/views/PageNotFound";
import Projects from "@/views/Projects"
import Project from "@/views/Project"

Vue.use(Router);

export default new Router({
  base: '/tagging/',
  mode: "history",
  routes: [
    {
      path: "/about",
      name: "about",
      component: About
    },
    {
      alias: "/",
      path: "/projects",
      name: "projects",
      component: Projects
    },
    {
      path: "/project/:identifier",
      name: "project",
      component: Project,
      props: true
    },
    {
      path: "/datasets",
      name: "datasets",
      component: Datasets
    },
    {
      path: "/dataset/:identifier",
      name: "dataset",
      component: Dataset,
      props: true
    },
    {
      path: "/categories",
      name: "categories",
      component: Categories
    },
    {
      path: "/undo",
      name: "undo",
      component: Undo
    },
    {
      path: "/annotate/:identifier",
      name: "annotate",
      component: Annotator,
      props: true
    },
    {
      path: "/auth",
      name: "authentication",
      component: Auth,
      props: true
    },
    {
      path: "/user",
      name: "user",
      component: User
    },
    {
      // path: "/admin/panel",
      path: "/admin",
      name: "admin",
      component: AdminPanel
    },
    {
      path: "/tasks",
      name: "tasks",
      component: Tasks
    },
    {
      path: "*",
      // redirect: "/",
      component: PageNotFound
    }
  ]
});
