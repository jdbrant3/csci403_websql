<template>
  <v-container>
    <v-row>
      <v-col cols="3"></v-col>
      <v-col class="mb-4" cols="6">
        <v-alert v-if="error_state" type="error">
          {{ error_message }}
        </v-alert>
        <div v-else>
          <div class="text-h4 mb-4">Current settings for {{ current_user }}</div>
          <v-card class="mb4" width="100%">
            <v-card-title>Search path</v-card-title>
            <v-card-text v-if="!is_editing_search_path" class="text-left">
              {{ current_search_path.join(", ") }}
            </v-card-text>
            <v-card-text v-else>
              <v-container>
                <v-row cols="12">
                  <v-col class="mx-2" cols="5">
                    <div class="text-subtitle-1">Search Path</div>
                    <draggable v-model="current_search_path" group="sp" @start="drag=true" @end="drag=false">
                      <v-card class="mb-1" v-for="s in current_search_path" :key="s">{{ s }}</v-card>
                    </draggable>
                  </v-col>
                  <v-col class="mx-2" cols="5">
                    <div class="text-subtitle-1">Available Schemas</div>
                    <draggable v-model="available_schemas" group="sp" @start="drag=true" @end="drag=false">
                      <v-card class="mb-1" v-for="s in available_schemas" :key="s">{{ s }}</v-card>
                    </draggable>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions v-if="!is_editing_search_path">
              <v-spacer/>
              <v-btn text @click="start_editing_search_path">Edit</v-btn>
            </v-card-actions>
            <v-card-actions v-else>
              <v-spacer/>
              <v-btn text @click="save_search_path">Save</v-btn>
              <v-btn text @click="cancel_editing_search_path">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </v-col>
      <v-col cols="3"></v-col>
    </v-row>
  </v-container>
</template>


<script>
import axios from 'axios'
import draggable from 'vuedraggable'

export default {
  components: {
    draggable
  },

  name: 'Settings',

  data: () => ({
    current_user: '',
    current_search_path: [],
    error_state: false,
    error_message: '',
    is_editing_search_path: false,
    available_schemas: []
  }),

  mounted () {
    this.baseurl = process.env.VUE_APP_API_BASE + '/api'
    this.get_user()
      .then(response => {
        this.current_user = response
        this.get_search_path()
          .then(response => {
            this.current_search_path = response
          })
          .catch(error => {
            console.log(error)
            this.error_message = 'Error retrieving search path!'
            this.error_state = true
          })
      })
      .catch(error => {
        console.log(error)
        this.error_message = 'Error retrieving user name!'
        this.error_state = true
      })
  },

  methods: {
    async get_one_string (query) {
      const path = this.baseurl + '/query'
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      let response = await axiosWithCookies.post(path, {query: query})
      return response.data[0].data[0][0]
    },

    get_user () {
      return this.get_one_string('select current_user')
    },

    async get_search_path () {
      let sp = await this.get_one_string('show search_path')
      return sp.split(', ').map(el => {
        if (el === '"$user"') return this.current_user
        return el
      })
    },

    start_editing_search_path () {
      const path = this.baseurl + '/query'
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.post(path, {query: 'select schema_name from information_schema.schemata order by schema_name'})
        .then(response => {
          let rows = response.data[0].data
          this.available_schemas = rows
            .map(el => el[0])
            .filter(s => !this.current_search_path.includes(s))
          this.is_editing_search_path = true
        })
        .catch(error => {
          console.log(error)
          this.error_message = 'Error retrieving available schemas'
          this.error_state = true
        })
    },

    save_search_path () {
      const path = this.baseurl + '/query'
      let query = 'alter user current_user set search_path to ' + this.current_search_path.join(', ')
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.post(path, {query: query})
        .then(() => {
          this.is_editing_search_path = false
        })
        .catch(error => {
          console.log(error)
          this.is_editing_search_path = false
        })
    },

    cancel_editing_search_path () {
      this.get_search_path()
        .then(response => {
          this.current_search_path = response
          this.is_editing_search_path = false
        })
        .catch(error => {
          console.log(error)
          this.error_message = 'Error retrieving search path!'
          this.error_state = true
          this.is_editing_search_path = false
        })
    }
  }
}
</script>
