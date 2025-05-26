import { createRouter, createWebHistory } from 'vue-router';
import MainView from '../views/HomeView.vue';
import FilesView from '../views/FilesView.vue';
import PdfView from '../views/PdfView.vue';
import RegistrationView from '../views/RegistrationView.vue';
import LoginView from '../views/LoginView.vue';
import SignupView from '../views/SignupView.vue';
import ChatView from '../views/ChatView.vue';

const routes = [
  {
    path: '/',
    name: 'Main',
    component: MainView,
    meta: { requiresAuth: true }
  },
  {
    path: '/files',
    name: 'Files',
    component: FilesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/files/:filePath',
    name: 'PdfExplorerView',
    component: PdfView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    'path': '/register',
    name: 'RegistrationView',
    component: RegistrationView,
    meta: { requiresAuth: true }
  },
  {
    'path': '/login',
    name: 'LoginView',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/signup',
    name: 'SignupView',
    component: SignupView,
    meta: { requiresGuest: true }
  },
  {
    path: '/chat/:fileName',
    name: 'chat',
    component: ChatView,
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;