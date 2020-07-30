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
        <span>
          Web SQL Interface
        </span>
      </div>

      <v-spacer></v-spacer>

      <v-btn
        to="/"
        text
      >
        <span class="mr-2">SQL</span>
      </v-btn>
      <v-btn
        to="/settings"
        text
      >
        <span class="mr-2">Settings</span>
      </v-btn>
      <v-btn
        href=""
        text
      >
        <span class="mr-2">Logout</span>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>
import WebSQL from './components/WebSQL.vue'
import Settings from './components/Settings.vue'

export default {
  name: 'app',

  components: {
    WebSQL,
    Settings
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
