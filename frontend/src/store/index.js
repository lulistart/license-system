import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    licenses: []
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setLicenses(state, licenses) {
      state.licenses = licenses
    }
  },
  actions: {
    logout({ commit }) {
      localStorage.removeItem('token')
      commit('setUser', null)
      commit('setLicenses', [])
    }
  }
}) 