import Vue from 'vue'
import Router from 'vue-router'
const routerOptions = [
  { path: '/', component: 'WebSQL' },
  { path: '/settings', component: 'Settings' },
  { path: '*', component: 'NotFound' }
]
const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`)
  }
})

export default new Router({
  routes,
  mode: 'history'
})

Vue.use(Router)
