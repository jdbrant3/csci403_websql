/* es-lint ignore */
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
                @click="execute_sql"
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
  export default {
    name: 'WebSQL',

    data: () => ({
      query: "",
      results: [],
      somedata: {
        columns: ["item", "quantity", "cost"],
        data: [
          ["apple", 4, 7.50],
          ["orange", 1, 2.00],
          ["cherry", 50, 10.99],
          ["quince", 6, 7.49],
          ["pear", 1, 0.5],
          ["pineapple", 1, 1.10],
          ["peach", 0, null],
          ["melon", 1, 2.99],
          ["grape", 100, 3.49],
          ["papaya", 2, 4.00],
          ["guava", 3, 11.99],
          ["nectarine", 8, 6.39],
          ["plum", 8, 5.79],
          ["strawberry", 25, 4.49],
          ["lemon", 1, 0.33],
        ]
      },
      somedata2: {
        columns: ["a", "b", "c", "d", "e", "f", "g"],
        data: (Array(100).fill([]).map(
                () => Array(7).fill(Math.random() * 1000)
        ))
      },
      tab: null
    }),

    methods: {
      execute_sql: async function() {
        let d = this.somedata;
        if (Math.random() > 0.5) d = this.somedata2;
        this.results.push({
           query: this.query,
          headers: d.columns.map(
                  e => ({ text: e, value: e })
          ),
          rows: d.data.map(
                  row => row.reduce(
                          (obj, e, idx) => {
                            obj[d.columns[idx]] = e;
                            return obj;
                          },
                          {}
                  )
          )
        });
        this.tab = this.results.length - 1
      }
    }
  }
</script>
