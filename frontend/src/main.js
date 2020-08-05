import Vue from 'vue'
import App from './App'
import router from './router'
import vuetify from './plugins/vuetify'
import login from './components/Login'

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  // el: '#app',
  router,
  vuetify,
  // login,
  render: h => h(App)
}).$mount('#app')
