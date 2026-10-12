import { createRouter, createWebHashHistory } from "vue-router";
import PredictView from "../views/PredictView.vue";
import BaseView from "../views/BaseView.vue";
import ScoreView from "../views/ScoreView.vue";
import SourceView from "../views/SourceView.vue";

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/predict" },
    { path: "/predict", component: PredictView },
    { path: "/base", component: BaseView },
    { path: "/score", component: ScoreView },
    { path: "/sources", component: SourceView },
  ],
});
