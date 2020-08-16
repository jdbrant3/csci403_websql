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
          <v-img src="http://cs-courses.mines.edu/csci101/static/dept_logo.png"/>
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
                <v-form
                      ref="form"
                      v-model="isValid"
                      lazy-validation

                >
                  <v-text-field
                    label="Username"
                    name="login"
                    prepend-icon="mdi-account"
                    type="text"
                    v-model="username"
                    :rules="[v => !!v || 'username is required']"
                    required
                  ></v-text-field>

                  <v-text-field
                    id="password"
                    label="Password"
                    name="password"
                    prepend-icon="mdi-lock"
                    type="password"
                    v-model="password"
                    :rules="[v => !!v || 'password is required']"
                    requried
                  ></v-text-field>
                </v-form>
              </v-card-text>
              <v-alert v-if="this.show" type="error">Invalid username and/or password.</v-alert>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                        @click="validate"
                        color="primary"
                        class="mr-4"
                        :disabled="!isValid"
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
        <div>
        </div>
      </v-container>
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
      errorMessage: null,
      isValid: true,
      show: false
  }),

    methods: {
      validate () {
        const path = `http://localhost:5000/api/login`
        const axiosWithCookies = axios.create({
          withCredentials: true
        });
        axiosWithCookies.post(path, {username: this.username, password: this.password})
        .then(response => {
          let result = response.data
          if(result.authorized){
            this.$router.push('websql')
          }
          else{
            this.isValid = false
            this.show = true
          }


        })
        .catch(error => {
            console.log('Error Authenticating: ', error)

        })
      },
      reset () {
        this.show = false
        if(this.$refs.form) {
          this.$refs.form.reset();
        }


      }
    }
  }
</script>
