import { createWebHistory, createRouter } from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import NotFound from "@/views/NotFound";
import Login from "@/views/Login";
import Register from "@/views/Register";
import Panel from "@/views/Panel";
import Plugin from "@/views/Plugin";

const routes = [
  {
    path: "/",
    name: "Panel",
    component: Panel,
  },

  {
    path: "/dashboard/:name",
    name: "Dashboard",
    component: Dashboard,
  },

  {
    path: "/plugin/:plugin",
    name: "Plugin",
    component: Plugin,
  },

  {
    path: "/login",
    name: "Login",
    component: Login,
  },

  {
    path: "/register",
    name: "Register",
    component: Register,
  },

  {
    path: "/:catchAll(.*)",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
