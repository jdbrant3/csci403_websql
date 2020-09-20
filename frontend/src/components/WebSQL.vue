<template>
  <v-container>
    <v-row>
      <v-col :cols="schemaShowing ? 7 : 11">
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
      <v-col :cols="schemaShowing ? 5 : 1">
        <v-container class="mx-4">
          <v-row class="text-center">
            <v-col :cols="schemaShowing ? 1 : 6" class="d-flex align-center">
              <v-btn icon large @click="schemaShowing = !schemaShowing">
                <v-icon v-if="schemaShowing">mdi-chevron-right</v-icon>
                <v-icon v-else>mdi-chevron-left</v-icon>
              </v-btn>
            </v-col>
            <v-col v-if="schemaShowing" cols="11">
              <v-container>
                <v-row class="text-left">
                  <v-col>
                    <h4>Your schemas</h4>
                    <p>(Click on SETTINGS in menu above to change active schemas)</p>
                    <v-card>
                      <v-expansion-panels flat hover multiple v-model="selectedSchemas">
                        <v-divider></v-divider>
                          <v-data-table
                          v-if=describe_output.data
                          :items=describe_output
                          />
                        <v-divider></v-divider>
                        <!-- <v-alert>{{ describe_object_output }}</v-alert> -->
                          <!-- <v-data-table
                            items = describe_object_output
                          /> -->
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
    schemaShowing: false,
    selectedSchemas: []
  }),

  mounted() {
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
    this.get_describe()
    this.get_describe_obj('pioneers_people')
  },

  methods: {
    execute_sql_backend: async function () {
      const path = `http://localhost:5000/api/query`
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

    get_describe: function() {
      const path = `http://localhost:5000/api/describe`
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.get(path)
        .then(response => {
        let describe_output = response.data.map(r => {
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
        console.log(describe_output)
        })
        .catch(error => {
          console.log(error)
          this.describe_output = error.toString()
        })
    },

    get_describe_obj: function(name) {
      const path = `http://localhost:5000/api/describe_object`
      const axiosWithCookies = axios.create({
        withCredentials: true
      })
      axiosWithCookies.post(path, name)
        .then(response => {
          this.describe_object_output = response.data
        })
        .catch(error => {
          console.log(error)
          this.describe_object_output = error.toString()
        })
    }

  }
}
</script>

