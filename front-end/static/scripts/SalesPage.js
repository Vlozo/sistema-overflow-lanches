import PaginatedTable from "./components/PaginatedTable.js";
import Navbar from "./components/Navbar.js";
import SaleForm from "./components/SaleForm.js";
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

const saleAliases = {
  sale_id: "Número da Venda",
  subtotal: "Subtotal",
  discount: "Desconto",
  fee: "Taxa",
  change: "Troco",
  total: "Total",
  sale_date: "Data da Venda",
  operator: "Operador"
}

export default{
    components: { Navbar, PaginatedTable, SaleForm, Modal},
      data() {
        return {
          selectedRow: null,
          saleResponse: null,
          productAliases: productAliases,
          saleAliases: saleAliases,
          statusMessage: "",
          statusType: "",
          moneyFields: ["unit_price", "subtotal", "fees_applied", "fee", "discount", "total", "change"],
          paymentMethods:{ 
                cash: "Dinheiro", 
                credit: "Crédito", 
                pix: "PIX", 
                debit: "Débito"
            },
        };
      },
    methods: {
      addToCart(product) {
      this.$refs.cart.addToCart(product);
      },
      handleCancel() {
        this.selectedRow = null;
        this.$refs.table.cancelSelection();
      },
      async handleSave(request) {
        try {
          const { data } = await axios.post(`/sales`, request, { withCredentials: true });
          this.saleResponse = data;

          this.statusMessage = "Registro salvo com sucesso!"; 
          this.statusType = "success";
          this.handleCancel();
          this.$refs.cart.showPayment = false;
          this.$refs.cart.cancelSale();
          return true;

        } catch (error) {
          this.statusMessage = "Erro ao salvar venda."; 
          this.statusType = "error";
          throw error;
        }
      },
    },
    template: `
    <Navbar />
    <main class="pd-1">
      <p>Clique duas vezes no produto que deseja adicionar à venda.</p>
      <PaginatedTable
        ref="table"
        path="/products" 
        :columns="['id', 'code','product','price','last_updated','updated_by']"
        :perPage="10"
        :moneyFields="['price']"
        :searchPlaceholder="'Buscar por nome ou código'"
        :fieldAliases="productAliases"
        :enableDoubleClick="true"
        @row-selected="selectedRow = $event"
        @row-dblclick="addToCart"
        class="mt-3"
        />
        
      <SaleForm 
      ref="cart" 
      :items="[]" 
      :fieldmap="{ id:'id', product: 'product', price: 'price'}"
      @submit-request="handleSave"
      class="mt-3"/>
    

      <Modal v-model:show="saleResponse">
        <div v-if="saleResponse" class="salepage__sale__summary">
          <h2>Resumo da Venda</h2>
          <ul class="mt-3">
            <li v-for="(alias, key) in saleAliases" :key="key">
              <strong>{{ alias }}: </strong>
              <span v-if="moneyFields.includes(key)">R$ {{ saleResponse[key] }}</span>
              <span v-else>{{ saleResponse[key] }}</span>
            </li>
          </ul>

          <h3 class="mt-3">Produtos</h3>
          <ul class="mt-2">
            <li v-for="item in saleResponse.items" :key="item.id">
              {{ item.name }} - {{ item.quantity }} x R$ {{ parseFloat(item.unit_price).toFixed(2) }}
            </li>
          </ul>

          <h3 class="mt-3">Forma de pagamento</h3>
          <ul class="mt-2">
            <li v-for="(p, idx) in saleResponse.payments" :key="idx">
              <strong>{{ paymentMethods[p.method] }}:</strong> R$ {{ p.value_paid }}
            </li>
          </ul>
        </div>
      </Modal>
    </main>
  `
}