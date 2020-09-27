<template>
  <v-container>
    <v-row>
      <v-col :cols="schema_showing ? 7 : 11">
        <v-container>
          <v-row class="text-center">
            <v-col class="mb-4">
              <v-textarea
                v-model="query"
                label="SQL"
                auto-grow
                outlined
                filled
                clearable
              >
              </v-textarea>
              <v-btn
                @click="execute_sql_backend"
                color="green"
                :disabled="!query"
                rounded
              >
                run
              </v-btn>
            </v-col>
          </v-row>
          <v-row class="text-center">
            <v-col cols="12">
              <v-card
                v-if="runs.length > 0"
              >
                <v-tabs
                  v-model="tab"
                  vertical
                >
                  <v-tab
                    v-for="(run, idx) in runs"
                    :key="'tab-run-' + run.run_number"
                  >
                    <v-card flat>
                      <v-card-text>
                        <span>{{ run.run_number }}</span>
                        <v-btn icon fab x-small dark @click="close_tab(idx)" color="grey">
                          <v-icon>mdi-close-box</v-icon>
                        </v-btn>
                      </v-card-text>
                    </v-card>
                  </v-tab>
                  <v-tab-item
                    class="text-left"
                    v-for="run in runs"
                    :key="'tab-item-run-' + run.run_number"
                  >
                    <v-card
                      class="ma-4 pa-4"
                      rounded
                      v-for="(result, idx2) in run.results"
                      :key="'result-' + run.run_number + '-' + idx2"
                    >
                      <pre v-if="result.comment">{{ result.comment }}</pre>
                      <pre v-if="result.query">{{ result. query }}</pre>
                      <v-alert v-if="result.error" type="error">
                        <pre>{{ result.error }}</pre>
                      </v-alert>
                      <div v-else>
                        <v-data-table
                          class="mt-4"
                          v-if="result.data"
                          :headers="result.columns"
                          :items="result.data"
                          dense
                          fixed-header
                          disable-filtering
                          disable-sort
                        />
                        <p
                          v-if="result.limit_message && result.limit_message.length > 0"
                          class="info pa-2"
                        >
                          {{ result.limit_message }}
                        </p>
                        <v-alert v-if="result.message" type="success">{{ result.message }}</v-alert>
                      </div>
                    </v-card>
                  </v-tab-item>
                </v-tabs>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
      <v-col :cols="schema_showing ? 5 : 1">
        <v-container class="mx-4">
          <v-row class="text-center">
            <v-col :cols="schema_showing ? 1 : 6" class="d-flex align-center">
              <v-btn icon large @click="toggle_schema">
                <v-icon v-if="schema_showing">mdi-chevron-right</v-icon>
                <v-icon v-else>mdi-chevron-left</v-icon>
              </v-btn>
            </v-col>
            <v-col v-if="schema_showing" cols="11">
              <v-container>
                <v-row class="text-left">
                  <v-col>
                    <h4>Your schemas: </h4>
                    <p>(Click on SETTINGS in menu above to change active schemas)</p>
                    <v-card>
                      <v-expansion-panels hover multiple v-model="selected_schemas" class="pa-2">
                        <v-expansion-panel v-for="schema in schemas" :key="schema.name" >
                          <v-expansion-panel-header>{{ schema.name }}</v-expansion-panel-header>
                          <v-expansion-panel-content>
                            <v-expansion-panels hover multiple v-model="selected_schema_objects[schema.name]">
                              <v-expansion-panel
                                v-for="obj in schema.objects"
                                :key="schema.name + '.' + obj.name"
                                @click="get_object_info(schema.name, obj.name, obj.type)"
                              >
                                <v-expansion-panel-header>{{ obj.name }}</v-expansion-panel-header>
                                <v-expansion-panel-content>
                                  <div class="mb-4">
                                    <b>type: </b> {{ obj.type }}
                                    <b>owner: </b> {{ obj.owner }}
                                  </div>
                                  <v-card v-if="obj.details.columns">
                                    <v-simple-table class="pa-3">
                                      <thead>
                                        <tr>
                                          <th v-for="col in obj.details.columns">{{ col }}</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        <tr v-for="row in obj.details.data">
                                          <td v-for="val in row">{{ val }}</td>
                                        </tr>
                                      </tbody>
                                    </v-simple-table>
                                  </v-card>
                                  <pre v-if="obj.details.info" class="mt-4 body-2">{{ obj.details.info }}</pre>
                                </v-expansion-panel-content>
                              </v-expansion-panel>
                            </v-expansion-panels>
                          </v-expansion-panel-content>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>
            <v-col v-else cols="6" class="d-flex align-center">
              <span class="pa-4 text-button" style="writing-mode: vertical-rl;">&nbsp; SCHEMA &nbsp;</span>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
export default {
  name: 'WebSQL',

  data: () => ({
    query: '',
    run_number: 0,
    runs: [],
    tab: null,
    schema_showing: false,
    selected_schemas: [],
    selected_schema_objects: {},
    schemas: [],
    schema_objects: {},
    search_path: ''
  }),

  mounted() {
    this.baseurl = process.env.VUE_APP_API_BASE + '/api';

    if (sessionStorage.getItem('csci403_query')) {
      this.query = sessionStorage.getItem('csci403_query')
    }
    if (sessionStorage.getItem('csci403_runs')) {
      try {
        this.runs = JSON.parse(sessionStorage.getItem('csci403_runs'))
        this.run_number = parseInt(sessionStorage.getItem('csci403_run_number'))
      }
      catch(e) {
        sessionStorage.removeItem('csci403_runs')
        sessionStorage.removeItem('csci403_tab')
        sessionStorage.removeItem('csci403_run_number')
      }
    }
    if (sessionStorage.getItem('csci403_tab')) {
      this.tab = parseInt(sessionStorage.getItem('csci403_tab'))
    }
  },

  methods: {
    execute_sql_backend: async function () {
      const path = this.baseurl + '/query'
      const axiosWithCookies = axios.create({
          withCredentials: true
      })

      // save the query regardless of success
      sessionStorage.setItem('csci403_query', this.query)

      axiosWithCookies.post(path, {query: this.query})
      .then(response => {
        // convert to v-data-table happy format
        let results = response.data.map(r => {
          if ('data' in r) {
            r.data = r.data.map(row => {
              let conversion = {}
              for (let index = 0; index < row.length; index++) {
                conversion[r.columns[index]] = row[index]
              }
              return conversion
            })
          }
          if ('columns' in r) {
            r.columns = r.columns.map(el => ({ text: el, value: el }))
          }
          return r;
        })
        this.runs.push({ run_number: this.run_number, results: results })
        this.run_number++
        this.tab = this.runs.length - 1
        sessionStorage.setItem('csci403_runs', JSON.stringify(this.runs))
        sessionStorage.setItem('csci403_run_number', this.run_number)
        sessionStorage.setItem('csci403_tab', this.tab)
      })
      .catch(error => {
        console.log(error)
      })
    },

    close_tab: function(idx) {
      this.runs.splice(idx, 1)
      this.tab = this.tab - 1
      sessionStorage.setItem('csci403_runs', JSON.stringify(this.runs))
      sessionStorage.setItem('csci403_tab', this.tab)
    },

    toggle_schema() {
      this.schema_showing = !this.schema_showing
      this.selected_schemas = []
      if (this.schema_showing) {
        this.refresh_schemas()
      }
    },

    async refresh_schemas () {
      let search_path = await this.get_search_path()
      const path = this.baseurl + '/describe'
      const axiosWithCookies = axios.create({ withCredentials: true })
      let response = await axiosWithCookies.post(path, { show_extra: false })
      for (let i = 0; i < search_path.length; i++) {
        this.selected_schema_objects[search_path[i]] = []
      }
      this.schemas = search_path.map(schema => ({
          name: schema,
          objects: response.data.data.filter(obj => {
              return obj[0] === schema
            }).map(obj => ({
              name: obj[1],
              type: obj[2],
              owner: obj[3],
              details: {}
            }))
          })
        )
    },

    async get_object_info (schema_name, object_name, object_type) {
      const path = this.baseurl + '/describe_object'
      const axiosWithCookies = axios.create({ withCredentials: true })
      let response = await axiosWithCookies.post(
        path, { name: schema_name + '.' + object_name, show_extra: object_type === 'view' }
      )
      this.schemas = this.schemas.map(schema => {
        if (schema.name === schema_name) {
          return {
            name: schema.name,
            objects: schema.objects.map(obj => {
              if (obj.name === object_name) {
                return {
                  name: obj.name,
                  type: obj.type,
                  owner: obj.owner,
                  details: response.data
                }
              } else {
                return obj
              }
            })
          }
        } else {
          return schema
        }
      })
    },

    async get_one_string (query) {
      const path = this.baseurl + '/query'
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      let response = await axiosWithCookies.post(path, {query: query})
      return response.data[0].data[0][0]
    },

    async get_search_path () {
      let sp = await this.get_one_string('show search_path')
      return sp.split(', ').map(el => {
        if (el === '"$user"') return this.current_user
        return el
      })
    }
  }
}
</script>

