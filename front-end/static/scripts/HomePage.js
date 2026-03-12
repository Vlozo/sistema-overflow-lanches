// scripts/HomeComponent.js
import Navbar from "./components/Navbar.js"

export default {
  components: { Navbar },
  template: `
    <div class="view home-page">
      <Navbar />
      <div class="container pd-1">
        <p>Versão: 0.1.0-alpha</p>
        <h2 class="mt-3">Bem-vindo, {{ userName }}!</h2>
        <p>Selecione uma das opções no menu.</p>
      </div>
    </div>
  `,
  data() {
    return {
      userName: window.AuthStore.user ? window.AuthStore.user.username : "Usuário"
    }
  }
}
