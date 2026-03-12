import PaginatedTable from "./components/PaginatedTable.js";
import RowForm from "./components/RowForm.js";
import Navbar from "./components/Navbar.js";
import Modal from "./components/Modal.js";

const productAliases = {
  id: "ID",
  code: "Código",
  new_code: "Novo Código",
  product: "Produto",
  price: "Preço",
  cost: "Custo",
  created_at: "Criado em",
  last_updated: "Atualizado em",
  updated_by: "Atualizado por"
};


export default {
  components: { Navbar, PaginatedTable, RowForm, Modal},
  data() {
    return {
      selectedRow: null,
      fields: ["code", "product", "price", "cost"],
      productAliases: productAliases,
      statusMessage: "",
      statusType: "",
      showModal: false
    };
  },
  methods: {
    validateForm(formData) {
      if (!formData.product || formData.product.trim() === "") {
        alert("O campo 'product' é obrigatório.");
        return false;
      }
      if (formData.price <= 0) {
        alert("O preço deve ser maior que zero.");
        return false;
      }
      return true;
    },
    async handleSave(formData) {
      try {
        if (formData.id) {
          await axios.put(`/products/${formData.id}`, {
            code: formData.code,
            product: formData.product,
            price: parseFloat(String(formData.price).replace(',', '.')) || 0,
            cost: parseFloat(String(formData.cost).replace(',', '.')) || 0
          }, { withCredentials: true });
        } else {
          await axios.post(`/products`, formData, { withCredentials: true });
        }

        this.statusMessage = "Registro salvo com sucesso!";
        this.statusType = "success";
        return true;

      } catch (error) {
        this.statusMessage = "Erro ao salvar registro."; 
        this.statusType = "error";
        throw error;
      }
    },

    handleDelete(id) {
      axios.delete(`/products/${id}`).then(() => {
        this.selectedRow = null;
      });
    },
    handleCancel() {
      this.selectedRow = null;
      this.$refs.form.clearFields();
    },
    newProduct() {
      this.handleCancel();
      this.$refs.table.cancelSelection();
      this.showModal = true;
    },
  },
  template: `
    <Navbar />
    <main class="pd-1">
      <p>Cadastre um novo produto ou clique sobre um produto existente para editar ou excluir</p>
      <PaginatedTable
        ref="table"
        path="/products" 
        :columns="['id','code','product','price','cost','created_at','last_updated','updated_by']"
        :moneyFields="['price', 'cost']"
        :searchPlaceholder="'Buscar por nome ou código'"
        :perPage="10"
        :fieldAliases="productAliases"
        @row-selected="selectedRow = $event"
        @row-dblclick="showModal = true"
        class="mt-3"
        />

      <button class="btn mt-3 btn--medium btn--blue" @click="newProduct">Novo Produto</button>
      <Modal v-model:show="showModal" :onClose="() => this.statusMessage = ''">
        <template #header>
          <h3>{{ modalTitle }}</h3>
        </template>
        <RowForm
          ref="form"
          :selectedRow="selectedRow" 
          :fields="['product', 'code','price','cost']"
          :fieldAliases="{ code: 'Código', product: 'Produto', price: 'Preço', cost: 'Custo' }"
          :statusMessage="statusMessage"
          :statusType="statusType"
          @save="handleSave" 
          @delete="handleDelete" 
          @cancel="handleCancel"
          />
      </Modal>
    </main>
    `
};