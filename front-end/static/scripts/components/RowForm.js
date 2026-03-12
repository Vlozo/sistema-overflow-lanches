export default {
  name: "RowForm",
  props: {
    selectedRow: { type: Object, default: null },
    fields: { type: Array, required: true },
    secondary_key: { type: Boolean, default: false },
    secondary_key_fields: { type: Object, default: () => ({ current: "code", new: "new_code" }) },
    fieldAliases: {
      type: Object,
      default: () => ({})
    },
    onSave: { type: Function, required: true },
    statusMessage: { type: String, default: "" }, 
    statusType: { type: String, default: "" }
  },
  data() {
    return { 
      form: {},
    };
  },
  watch: {
    selectedRow: {
      immediate: true,
      handler(newRow) {
        this.form = {};
        this.fields.forEach(field => {
          this.form[field] = newRow ? newRow[field] || "" : "";
        });
        if (this.secondary_key && newRow) {
          this.form[this.secondary_key_fields.current] = newRow[this.secondary_key_fields.current] || "";
          this.form[this.secondary_key_fields.new] = "";
        }
        if (newRow && newRow.id) {
          this.form.id = newRow.id;
        }
      }
    }
  },
  emits: ['delete', 'cancel'],
  methods: {
    async save() {
      try {
        await this.onSave(this.form);
        this.statusMessage = "Registro salvo com sucesso!";
        this.statusType = "success";
      } catch (err) {
        this.statusMessage = "Erro ao salvar registro.";
        this.statusType = "error";
      }
    },
    deleteRow() { if (this.form.id) this.$emit("delete", this.form.id); },
    cancel() { this.$emit("cancel"); },
    clearFields() {
      for (let field of this.fields) {
        this.form[field] = "";
      }
    }
  },
  template: `
    <section class="row-form w-100">
      <h2>{{ form.id ? "Editar Registro" : "Criar Registro" }}</h2>

      <!-- resto do formulário -->
      <section class="row-form__field__wrapper mt-5">
        <div v-for="field in fields" :key="field" class="row-form__field">
          <label><strong>{{ fieldAliases[field] || field }}:</strong>
            <input v-model="form[field]" class="input w-100"/>
          </label>
        </div>
      </section>

      <div class="form-actions mt-5">
        <button @click="save" class="btn btn--medium btn--submit mr-1">Salvar</button>
        <button v-if="form.id" @click="deleteRow" class="btn btn--medium btn--red">Excluir</button>
        <button v-if="!form.id" @click="cancel" class="btn btn--medium">Limpar</button>
      </div>

      <!-- feedback -->
      <span v-if="statusMessage" :class="['status', statusType]" class="mt-3">
        <strong>{{ statusMessage }}</strong>
      </span>
    </section>
  `
};
