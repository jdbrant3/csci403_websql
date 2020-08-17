<template>
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
                v-if="results.length > 0"
        >
          <v-tabs
            v-model="tab"
            vertical
          >
            <v-tab
              v-for="(result, idx) in results"
              :key="'tab-' + idx"
            >
              {{ idx + 1 }}
            </v-tab>
            <v-tab-item
              class="text-left"
              v-for="(run, idx) in results"
              :key="'result-' + idx"
            >
              <v-card class="ma-4 pa-4" rounded v-for="(result, idx2) in run" :key="'result-' + idx + '-' + idx2">
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
</template>

<script>
import axios from 'axios'
export default {
  name: 'WebSQL',

  data: () => ({
    query: '',
    raw_results: [],
    tab: null
  }),

  mounted() {
    if (sessionStorage.getItem('query')) {
      this.query = sessionStorage.getItem('query')
    }
    if (sessionStorage.getItem('raw_results')) {
      try {
        this.raw_results = JSON.parse(sessionStorage.getItem('raw_results'))
      }
      catch(e) {
        sessionStorage.removeItem('raw_results')
      }
    }
    if (sessionStorage.getItem('tab')) {
      this.tab = parseInt(sessionStorage.getItem('tab'))
    }
  },

  computed: {
    // convert results into v-data-table happy form
    results: function() {
      return this.raw_results.map(run => {
        return run.map(result => {
          if ('data' in result) {
            result.data = result.data.map(row => {
              let conversion = {}
              for (let index = 0; index < row.length; index++) {
                conversion[result.columns[index]] = row[index]
              }
              return conversion
            })
          }
          if ('columns' in result) {
            result.columns = result.columns.map(el => ({ text: el, value: el }))
          }
          return result;
        })
      })
    }
  },

  methods: {
    execute_sql_backend: async function () {
      const path = `http://localhost:5000/api/query`

      // save the query regardless of success
      sessionStorage.setItem('query', this.query)
      // axios.defaults.withCredentials = true
      const axiosWithCookies = axios.create({
          withCredentials: true
        })
      axiosWithCookies.post(path, {query: this.query})
      .then(response => {
        let result = response.data
        this.raw_results.push(result)
        this.tab = this.raw_results.length - 1
        sessionStorage.setItem('raw_results', JSON.stringify(this.raw_results))
        sessionStorage.setItem('tab', this.tab)
      })
      .catch(error => {
        console.log(error)
      })
    }
  }
}
</script>
