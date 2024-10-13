import { createRouter, createWebHistory } from 'vue-router';
import MainView from '../views/MainView.vue';
import FilesView from '../views/FilesView.vue';
import PdfView from '../views/PdfView.vue';
const routes = [
    

      {
        path: '/',
        name: 'Main',
        component: MainView,
       
      },

      {
        path: '/files',
        name: 'Files',
        component: FilesView,
       
      },
      {
        path: '/files/:filePath',
        name: 'PdfExplorerView',
        component: PdfView,
        props: true,
      },

]

const BASE_URL = '/';

const router = createRouter({
  history: createWebHistory(BASE_URL),
  routes
})




export default router