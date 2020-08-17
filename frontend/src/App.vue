<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <span>
          CSCI 403 Web SQL Interface
        </span>
      </div>

      <v-spacer></v-spacer>

      <v-btn
        to="/websql"
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
        @click="logout"
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
import Login from './components/Login.vue'
import WebSQL from './components/WebSQL.vue'
import Settings from './components/Settings.vue'
import NotFound from './components/NotFound.vue'

import axios from 'axios'

export default {
  name: 'app',

  components: {
    Login,
    WebSQL,
    Settings,
    NotFound
  },
  data: () => ({
    //
  }),
  methods: {
    logout () {
      const path = `http://localhost:5000/api/logout`
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.post(path)
        .then(response => {
          let result = response.data
          if (result.success) {
            this.$router.push('login')
          }
        })
        .catch(error => {
          console.log('Error Logging Out: ', error)
        })
    }
  }
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
