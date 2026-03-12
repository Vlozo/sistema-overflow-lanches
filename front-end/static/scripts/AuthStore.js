window.AuthStore = {
  user: null,

  isProfileTokenValid() {
    const token = sessionStorage.getItem("profile_token")
    if (!token) return false

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp > now) {
        this.user = {
          id: payload.id,
          username: payload.sub,
          is_admin: payload.is_admin
        }
        return true
      } else {
        this.user = null
        return false
      }
    } catch {
      this.user = null
      return false
    }
  },

  async doLogin(username, password) {
    const res = await axios.post("/login", { username, password }, { withCredentials: true })
    sessionStorage.setItem("profile_token", res.data.profile_token)
    this.isProfileTokenValid()
  },

  async doLogout() {
    await axios.post("/logout", {}, { withCredentials: true })
    this.user = null
    sessionStorage.removeItem("profile_token")
  },

  get isLoggedIn() {
    return this.isProfileTokenValid()
  },

  async validateAdminAccess() {
    try {
      await axios.get("/validate", { withCredentials: true })
      return true
    } catch {
      return false
    }
  },

  async validateAccess(requiredPermission) {
    try {
      const res = await axios.get("/validate", {
        params: { permission: requiredPermission },
        withCredentials: true
      });
      return true;
    } catch {
      return false;
    }
  }
}