import { createWebHistory, createRouter } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Panel",
    component: () => import(/* webpackChunkName: "panel" */ "@/views/Panel"),
  },

  {
    path: "/dashboard/:name",
    name: "Dashboard",
    component: () => import(/* webpackChunkName: "dashboard" */ "@/views/Dashboard"),
  },

  {
    path: "/plugin/:plugin",
    name: "Plugin",
    component: () => import(/* webpackChunkName: "plugin" */ "@/views/Plugin"),
  },

  {
    path: "/login",
    name: "Login",
    component: () => import(/* webpackChunkName: "login" */ "@/views/Login"),
  },

  {
    path: "/register",
    name: "Register",
    component: () => import(/* webpackChunkName: "register" */ "@/views/Register"),
  },

  {
    path: "/:catchAll(.*)",
    component: () => import(/* webpackChunkName: "notfound" */ "@/views/NotFound"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
