<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />
        <!-- <v-img
          alt="Mines Logo"
          class="shrink mr-2"
          contain
          src="..\assets\cs_dept_logo_cropped.png"
          transition="scale-transition"
          width="40"
        /> -->
        <span>
          Web SQL Interface
        </span>
      </div>
      
      <v-spacer></v-spacer>

      <v-btn
        href=""
        text
        @click="$router.push('login')"
      >
        <span class="mr-2">Logout</span>
      </v-btn>
    </v-app-bar>

    <v-main>
    <!-- <div id="nav">
      <router-link to="/">Home</router-link> |
      <router-link to="/login">Login</router-link> |
      <router-link to="/websql">WebSQL</router-link>
    </div> -->
    <router-view/>
    </v-main>
  </v-app>
</template>

<script>
import WebSQL from './components/WebSQL.vue'
export default {
  name: 'app',

  components: {
    WebSQL
  },
  data: () => ({
    //
  })
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
