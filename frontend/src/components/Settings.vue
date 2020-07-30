<template>
  <v-container>
    <v-row class="text-center">
      <v-col class="mb-4">
        <h1>SETTINGS!</h1>
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
            height="250px"
          >
            <v-tab
              v-for="(result, idx) in results"
              :key="idx"
            >
              {{ idx + 1 }}
            </v-tab>
            <v-tab-item
              v-for="(result, idx) in results"
              :key="idx"
            >
              <v-data-table
                :caption="result.query"
                :headers="result.headers"
                :items="result.rows"
                dense
                fixed-header
                disable-filtering
                disable-sort
                height="250px"
              >
              </v-data-table>
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
  name: 'Settings',

  data: () => ({
    query: '',
    results: [],
    tab: null
  }),

  methods: {
    execute_sql_backend: async function () {
      const path = `http://localhost:5000/api/query`
      axios.post(path, {query: this.query})
        .then(response => {
          console.log(response.data)
          let headers = null
          let rows = response.data
          if (rows) {
            headers = Object.keys(rows[0]).map(
                e => ({ text: e, value: e })
              )
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
