import PaginatedTable from "./components/PaginatedTable.js";
import Navbar from "./components/Navbar.js";
import Modal from "./components/Modal.js"

export default {
    components: { PaginatedTable, Navbar, Modal},
    data() {
        return {
            moneyFields: ["unit_price", "subtotal", "fees_applied", "discount", "total", "change"],
            saleAliases: {
            datetime: "Data",
            operator: "Operador",
            subtotal: "Subtotal",
            total: "Total",
            discount: "Desconto",
            fees_applied: "Taxas",
            change: "Troco"
            },
            productAliases: {
            product_name: "Produto",
            quantity: "Quantidade",
            unit_price: "Preço Unitário",
            subtotal: "Subtotal"
            },
            paymentMethods:{ 
                cash: "Dinheiro", 
                credit: "Crédito", 
                pix: "PIX", 
                debit: "Débito"
            },
            saleDetails: null,
        };
    },
    methods: {
        async detailSale(sale){
        try {
          const { data } = await axios.get(`/sales/${sale.id}`, { withCredentials: true });
          this.saleDetails = data;
          return true;

        } catch (error) {
          this.statusMessage = "Erro ao detalhar venda."; 
          this.statusType = "error";
          throw error;
        }
      },
    },
    template: `
    <Navbar />
    <main class="pd-1">
        <p>Clique duas vezes sobre um produto para ver detalhes da venda.</p>
        <PaginatedTable
            ref="table"
            path="/sales" 
            :columns="['id', 'datetime', 'total', 'discount','change','fees_applied', 'operator']"
            :perPage="10"
            :searchPlaceholder="'Buscar por id da venda'"
            :fieldAliases="saleAliases"
            :enableDoubleClick="true"
            :moneyFields="['total', 'discount', 'change', 'fees_applied']"
            @row-selected="selectedRow = $event"
            @row-dblclick="detailSale"
            class="mt-3"
            />
        
        <Modal v-model:show="saleDetails">
            <div v-if="saleDetails" class="sale-details">
                <h3 class="mb-2">Detalhes da Venda</h3>
                <hr />
                <ul class="mt-3 d-flex flex-col gap-A1">
                    <li v-for="(alias, key) in saleAliases" :key="key">
                    <strong>{{ alias }}: </strong>
                    <span v-if="moneyFields.includes(key)">R$ {{ parseFloat(saleDetails[key]).toFixed(2) }}</span>
                    <span v-else>{{ saleDetails[key] }}</span>
                    </li>
                </ul>

                <h4 class="mt-3 mb-3">Itens Vendidos</h4>
                <hr />
                <div class="table__container">
                    <table class="table__content">
                    <thead>
                        <tr>
                        <th v-for="(alias, key) in productAliases" :key="key">
                            {{ alias }}
                        </th>
                        <th>Resumo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, idx) in saleDetails.items" :key="idx">
                        <td v-for="(alias, key) in productAliases" :key="key">
                            <span v-if="moneyFields.includes(key)">R$ {{ item[key].toFixed(2) }}</span>
                            <span v-else>{{ item[key] }}</span>
                        </td>
                        <td>
                            {{ item.product_name }} ({{ item.quantity }} x R$ {{ item.unit_price.toFixed(2) }})
                        </td>
                        </tr>
                    </tbody>
                    </table>
                </div>

                <h4 class="mt-3 mb-2">Método de Pagamento</h4>
                <hr />
                    <ul class="mt-2">
                    <li v-for="(p, idx) in saleDetails.payments" :key="idx">
                        <strong>{{ paymentMethods[p.method] }}:</strong> R$ {{ p.value_paid }}
                    </li>
                    </ul>
            </div>
        </Modal>
    </main>
    `
}