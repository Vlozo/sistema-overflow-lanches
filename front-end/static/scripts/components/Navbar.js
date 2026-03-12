export default {
  data(){
    return {
      navbarActive: false
    }
  },
  methods: {
    toggleNavbar() {
      this.navbarActive = !this.navbarActive;

      if (this.navbarActive == true) {
        document.body.classList.add('body-no-scroll');
      } else {
        document.body.classList.remove('body-no-scroll');
      }
    },
    async logout() {
      await window.AuthStore.doLogout();
      this.$router.push("/login");
    }
  },
    beforeUnmount() {
    document.body.classList.remove('body-no-scroll');
    document.body.style.overflow = '';
  },
  template: `
    <header class="navbar__header">
      <button @click="toggleNavbar" class="navbar__button">☰</button>
      <span class="navbar__screen__overlay active" v-if="navbarActive" @click="toggleNavbar"></span>

      <nav class="navbar__menu active" name="navbar" v-if="navbarActive">
        <ul class="navbar__list">
          <button class="navbar__close__button"@click="toggleNavbar">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
                viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>

          <li><router-link class="navbar__item" to="/">Home</router-link></li>
          <li><router-link class="navbar__item" to="/produtos">Produtos</router-link></li>
          <li><router-link class="navbar__item" to="/vendas/registrar">Registrar Venda</router-link></li>
          <li><router-link class="navbar__item" to="/vendas">Listagem de Vendas</router-link></li>
          <li><router-link class="navbar__item" to="/config">Configurações</router-link></li>
          <li><a class="navbar__item" href="#" @click.prevent="logout">Logout</a></li>
        </ul>
      </nav>
    </header>
  `
}
