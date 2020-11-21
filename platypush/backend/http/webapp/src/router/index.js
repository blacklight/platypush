import { createWebHistory, createRouter } from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import NotFound from "@/views/NotFound";

const routes = [
  {
    path: "/dashboard/:name",
    name: "Dashboard",
    component: Dashboard,
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
