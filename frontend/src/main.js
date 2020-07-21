import Vue from 'vue'
import App from './App'
import router from './router'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  // el: '#app',
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')
