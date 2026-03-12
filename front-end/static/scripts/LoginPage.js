
export default {
  template: `
    <div class="view d-flex flex-col">
      <div class="loginSection d-flex flex-col pd-1 h-100"">
        <div class="align-center pd-1">
          <h1>Overflow Lanches 🍔</h1>
          <p>Bem-vindo ao sistema de registro de vendas</p>
        </div>
        
        <div class="login__fields mt-3">
          <input v-model="user" placeholder="Usuário" class="input input--medium">
          <input v-model="pass" type="password" placeholder="Senha" class="input input--medium mt-1">
        </div>
        
        <button @click="doLogin" class="login__button btn btn--medium btn--submit mt-3 align-center">Entrar</button>
      </div>
    </div>
  `,
  data() {
    return {
      user: "",
      pass: ""
    }
  },
  methods: {
    async doLogin() {
      try {
        await window.AuthStore.doLogin(this.user, this.pass)
        alert("Login realizado com sucesso!")
        this.$router.push("/")
      } catch (err) {
        alert("Falha no login")
      }
    }
  }
}
