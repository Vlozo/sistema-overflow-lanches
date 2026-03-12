import LoginPage from "./LoginPage.js"
import HomePage from "./HomePage.js"
import ProductsPage from "./ProductsPage.js"
import SalesPage from "./SalesPage.js"
import SalesData from "./SalesData.js"

const { createApp } = Vue 
const { createRouter, createWebHistory } = VueRouter

const NotFound = { template: "<h1>Status 404</h1><h2>Página não encontrada</h2><a href='/'>Voltar para a página inicial</a>"}
const Unauthorized = { template: "<h1>Status 403</h1><h2>Você não tem permissão para acessar essa página</h2><a href='/'>Voltar para a página inicial</a>"}

axios.defaults.withCredentials = true;
axios.defaults.baseURL = window.APP_CONFIG.apiUrl;
axios.defaults.xsrfCookieName = 'csrf_access_token';
axios.defaults.xsrfHeaderName = 'csrf_access_token';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

axios.interceptors.request.use(config => {
  const csrfToken = getCookie('csrf_access_token');
  if (csrfToken) {
    config.headers['X-CSRF-TOKEN'] = csrfToken;
  }
  config.withCredentials = true;
  return config;
});

const routes = [
  { path: "/", component: HomePage, meta: { requiresAuth: true } },
  { path: "/produtos", component: ProductsPage, meta: { permission: "create_product" } },
  { path: "/vendas/registrar", component: SalesPage, meta: { permission: "register_sale" }},
  { path: "/vendas", component: SalesData, meta: { permission: "view_cashflow"}},
  { path: "/login", component: LoginPage },
  { path: "/unauthorized", component: Unauthorized },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAdmin) {
    try {
      const res = await axios.get("/validate", { withCredentials: true });
      if (res.status === 200) {
        next();
      } else {
        next("/unauthorized");
      }
    } catch {
      next("/unauthorized");
    }
  } else if (to.meta.permission) {
    try {
      const res = await axios.get("/validate", {
        params: { permission: to.meta.permission },
        withCredentials: true
      });
      if (res.status === 200) {
        next();
      } else {
        next("/unauthorized");
      }
    } catch {
      next("/unauthorized");
    }
  } else if (to.meta.requiresAuth) {
    if (window.AuthStore.isProfileTokenValid()) {
      next();
    } else {
      next("/login");
    }
  } else {
    next();
  }
});

const app = createApp({
  created() {
    if (!window.AuthStore.isProfileTokenValid()) {
      this.$router.push("/login")
    } 
  }
})


app.use(router)
app.mount("#app")
