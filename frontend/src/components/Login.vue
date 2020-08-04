<template>
  <v-app id="inspire">
    <v-main>
      <v-container
        class="fill-height"
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
          <v-img src="https://cs-courses.mines.edu/csci303/CSLogoNew.jpg"/>
            <v-card class="elevation-12">
              <v-toolbar
                color="primary"
                dark
                flat
              >
                <v-toolbar-title>Login to Flowers</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      :href="source"
                      icon
                      large
                      target="_blank"
                      v-on="on"
                    >
                      <v-icon>mdi-code-tags</v-icon>
                    </v-btn>
                  </template>
                  <span>Source</span>
                </v-tooltip>
              </v-toolbar>
              <v-card-text>
                <v-form>
                  <v-text-field
                    label="Username"
                    name="login"
                    prepend-icon="mdi-account"
                    type="text"
                  ></v-text-field>

                  <v-text-field
                    id="password"
                    label="Password"
                    name="password"
                    prepend-icon="mdi-lock"
                    type="password"
                  ></v-text-field>
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn  @click="$router.push('websql')" color="primary">Login</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios'
export default {
    name: 'Login',

    data: () => ({
      uname: '',
      pass: ''
    }),

    methods: {
      execute_login: async function () {
        const path = `http://localhost:5000/api/login`
        axios.post(path, {uname: this.uname, pass: this.pass})
        .then(response => {
            console.log(response.data);
            let headers = null;
            let rows = response.data;
            if (rows) {
              headers = Object.keys(rows[0]).map(
                e => ({ text: e, value: e})
              );
            }
            this.results.push({
                query: this.query,
                headers: headers,
                rows: rows
            })
        })
        .catch(error => {
            console.log(error)
        })
        this.tab = this.results.length - 1
      }
    }
  }
</script>