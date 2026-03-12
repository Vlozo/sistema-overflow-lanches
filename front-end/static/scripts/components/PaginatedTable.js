const normalizeNumber = (val) => {
  if (typeof val === "string") {
    return parseFloat(val.replace(",", "."));
  }
  return parseFloat(val);
};

export default {
  name: "PaginatedTable",
  props: {
    path: { type: String, required: true },
    columns: { type: Array, required: true },
    perPage: { type: Number, default: 5 },
    fieldAliases: { type: Object, default: () => ({}) },
    enableDoubleClick: { type: Boolean, default: false },
    moneyFields: { type: Array, default: () => [] },
    searchPlaceholder: { type: String, default: "Buscar..."}
  },
  data() {
    return {
      data: [],
      currentPage: 1,
      totalPages: 1,
      search: "",
      selectedRowId: null,
    };
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get(this.path, {
          params: {
            page: this.currentPage,
            perPage: this.perPage,
            search: this.search || undefined
          }
        });

        if (response.data.rows && response.data.totalPages) {
          this.data = response.data.rows;
          this.totalPages = response.data.totalPages;
        } else {
          this.data = this.normalizeMoneyFields(rawData);
          this.totalPages = Math.ceil(this.data.length / this.perPage);
        }
      } catch (error) {
        console.error("Erro ao buscar dados:", error);
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchData();
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchData();
      }
    },
    reload() { 
      this.fetchData(); 
    },
    selectRow(row) {
      this.selectedRowId = row.id;
      this.$emit("row-selected", row);
    },
    cancelSelection() {
      this.selectedRowId = null;
      this.$emit("cancel-selection");
    },
    normalizeMoneyFields(rows) {
      return rows.map(row => {
        const normalized = { ...row };
        for (const field of this.moneyFields) {
          if (normalized[field] !== undefined && normalized[field] !== null) {
            normalized[field] = parseFloat(
              String(normalized[field]).replace(",", ".")
            );
          }
        }
        return normalized;
      });
    },
  },
  watch: {
    search() {
      this.currentPage = 1;
      this.fetchData();
    }
  },
  mounted() {
    this.fetchData();
  },
  template: `
    <div>
      <input type="text" class="input" v-model="search" :placeholder="this.searchPlaceholder"/>
      <div class="pagination__wrapper mt-2">
        <table class="pagination__table">
          <thead class="pagination__table__head">
            <tr>
              <th v-for="col in columns" :key="col">
                {{ fieldAliases[col] || col }}
              </th>
            </tr>
          </thead>
          <tbody class="pagination__table__body">
              <tr 
              v-for="row in data" 
              :key="row.id" 
              @click="selectRow(row)"
              :class="{ 'selected-row': selectedRowId === row.id }"
              @dblclick="$emit('row-dblclick', row)"
            >
              <td v-for="col in columns" :key="col">
                <span v-if="moneyFields.includes(col)">R$ {{ row[col] }}</span>
                <span v-else>{{ row[col] }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- controles de paginação -->
      <div class="pagination-controls mt-2">
        <button @click="prevPage" :disabled="currentPage === 1" class="btn mr-1">Anterior</button>
        <span class="mr-1">Página {{ currentPage }} de {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="btn mr-1">Próxima</button>
        <button @click="reload" class="btn">Recarregar</button>
      </div>
    </div>
  `
};
