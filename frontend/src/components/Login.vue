<template>
  <v-app id="inspire">
    <v-main>
      <v-container
        fluid
      >
        <v-row
          align="center"
          justify="center"
        >
          <v-col
            cols="12"
            sm="8"
            md="4"
          >
          <v-img :src="require('../assets/cs_dept_logo.png')"/>
            <v-card class="elevation-12">
              <v-toolbar
                color="primary"
                dark
                flat
              >
                <v-toolbar-title>Login to CSCI 403</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      icon
                      large
                      target="_blank"
                      v-on="on"
                    >
                      <v-icon>mdi-code-tags</v-icon>
                    </v-btn>
                  </template>
                  <!-- <span>Source</span> -->
                </v-tooltip>
              </v-toolbar>
              <v-card-text>
                <v-text-field
                  @keyup.enter="validate"
                  label="Username"
                  name="login"
                  prepend-icon="mdi-account"
                  type="text"
                  v-model="username"
                  required
                ></v-text-field>
                <v-text-field
                  @keyup.enter="validate"
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  type="password"
                  v-model="password"
                  required
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  @keyup.enter="validate"
                  @click="validate"
                  color="primary"
                  class="mr-4"
                  :disabled="username === null || username.length === 0 || password === null || password.length === 0"
                >
                  Login
                </v-btn>
                <v-btn
                  @click="reset"
                  color="error"
                  class="mr-4"
                >
                  Reset
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
      <v-snackbar
        v-model="showMessage"
        top
        color="error"
        timeout="5000"
      >
        Invalid username or password.
        <template v-slot:action="{ attrs }">
          <v-btn
            text
            v-bind="attrs"
            @click="showMessage = false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios'
export default {
  name: 'Login',

  data: () => ({
    username: null,
    password: null,
    showMessage: false
  }),

  mounted () {
    this.baseurl = process.env.VUE_APP_API_BASE + '/api';
    console.log(this.baseurl)
  },

  methods: {
    validate () {
      const path = this.baseurl + '/login'
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.post(path, { username: this.username, password: this.password })
      .then(response => {
        let result = response.data
        if(result.authorized){
          this.$router.push('websql')
        }
        else{
          this.showMessage = true
        }
      })
      .catch(error => {
          console.log('Error Authenticating: ', error)
      })
    },
    reset () {
      this.showMessage = false
      this.username = null
      this.password = null
    }
  }
}
</script>
