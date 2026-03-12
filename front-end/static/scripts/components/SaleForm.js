import Modal from "./Modal.js";

const normalizeNumber = (val) => {
  if (typeof val === "string") {
    return parseFloat(val.replace(",", "."));
  }
  return parseFloat(val);
};

const toCents = (val) => Math.round(parseFloat(val.toString().replace(",", ".")) * 100);
const fromCents = (cents) => (cents / 100).toFixed(2);

export default {
  components: { Modal },
  props: {
    items: { type: Array, required: true },
    fieldMap: { 
      type: Object, 
      default: () => ({
        id: "id",
        product: "product",
        price: "price"
      })
    }
  },
  data() {
    return {
      cart: [],
      discountActive: false,
      showPayment: false,
      retroactiveSale: false,
      discountPercentage: 0,
      discountValue: 0,
      payments: { 
        pix: { active: false, value: 0, tax: 0, alias: "pix", method:"pix"}, 
        cash: { active: false, value: 0, tax: 0, alias: "dinheiro", method:"cash"}, 
        credit: { active: false, value: 0, tax: 0, alias: "crédito", method:"credit"}, 
        debit: { active: false, value: 0, tax: 0, alias: "débito", method:"debit"} 
      },
      retrodate: "",
    };
  },
  computed: {
    total() {
      const sum = this.cart.reduce(
        (acc, item) => acc + (normalizeNumber(item.unit_price) * item.quantity),
        0
      );
      return sum - (normalizeNumber(this.discountValue) || 0);
    },
    sumPayments() {
      return Object.values(this.payments)
        .filter(p => p.active)
        .reduce((acc, p) => {
          const val = normalizeNumber(p.value) || 0;
          const tax = normalizeNumber(p.tax) || 0;
          return acc + val + tax;
        }, 0);
    },
    dueAmount() {
      const baseTotal = (typeof this.total === 'function') ? this.total() : this.total;
      const taxSum = Object.values(this.payments)
        .filter(p => p.active)
        .reduce((acc, p) => acc + (normalizeNumber(p.tax) || 0), 0);
      return baseTotal + taxSum;
    },
    showDifference() {
      const value = this.dueAmount - this.sumPayments;
      let result;
      (value > 0) ?  result = value : result = 0
      return result 
    },
    calcChange() {
      if (!(this.payments.credit.active || this.payments.debit.active || this.payments.pix.active)){
        if (this.payments.cash && this.payments.cash.active){
          const change = this.sumPayments - this.dueAmount;
          if (change > 0) {
            return change;
          }
        }
      }
      return 0;
    }
  },
  methods: {
    addToCart(product) {
      const idField = this.fieldMap.id;
      const productField = this.fieldMap.product;
      const priceField = this.fieldMap.price;

      const exists = this.cart.find(i => i.id === product[idField]);
      if (!exists) {
        this.cart.push({
          id: product[idField],
          product: product[productField],
          quantity: 1,
          unit_price: parseFloat(product[priceField].replace(",","."))
        });
      }
    },
    removeFromCart(productId) {
      this.cart = this.cart.filter(i => i.id !== productId);
    },
    updateQuantity(productId, quantity) { 
        const item = this.cart.find(i => i.id === productId); 
        if (item) { 
            item.quantity = quantity;
         }
        this.syncDiscount();
    },
    validateQuantity(productId) { 
        const item = this.cart.find(i => i.id === productId); 
        if (item) {  
            if (!item.quantity || item.quantity < 1) { 
                item.quantity = 1; 
            }
        }
    },
    toggleDiscount() {
      this.discountActive = !this.discountActive;
    },
    toggleRetroactiveSale() {
      this.retroactiveSale = !this.retroactiveSale;
    },
    applyDiscountPercentage(percent) {
      const totalWithoutDiscountCents = this.cart.reduce(
        (acc, i) => acc + toCents(i.unit_price) * i.quantity,
        0
      );
      const discountCents = Math.round(totalWithoutDiscountCents * percent / 100);
      this.discountValue = fromCents(discountCents);
      this.discountPercentage = percent;
    },

    applyDiscountValue(value) {
      const totalWithoutDiscountCents = this.cart.reduce(
        (acc, i) => acc + toCents(i.unit_price) * i.quantity,
        0
      );
      const valueCents = toCents(value);
      this.discountPercentage = (valueCents / totalWithoutDiscountCents) * 100;
      this.discountValue = valueCents / 100;
    },

    syncDiscount() {
      if (this.discountPercentage > 0) {
        this.applyDiscountPercentage(this.discountPercentage);
      } else if (this.discountValue > 0) {
        this.applyDiscountValue(this.discountValue);
      }
    },
    validatePayments() {
      const paid = this.sumPayments;
      const debt = this.dueAmount;
      const change = this.calcChange;

      const totalPaid = Number((paid - change).toFixed(2));
      const expectedValue = Number(debt.toFixed(2));

      if (totalPaid < expectedValue) {
        alert("Não foi possível registrar a venda: valor pago não corresponde ao valor devido.");
        return false;
      }

      return true;
    },
    cancelSale() {
      this.cart = [];
      this.clearValues();
      this.retroactiveSale = false;
      this.retrodate = "";
      this.discountPercentage = 0;
      this.discountValue = 0;
    },
    autoComplete() {
      const toCents = (val) => Math.round(parseFloat(val) * 100);

      const dueAmountCents = toCents(this.dueAmount);
      const sumPaymentsCents = toCents(this.sumPayments);

      let remaining = dueAmountCents - sumPaymentsCents;

      const activeMethods = Object.entries(this.payments)
        .filter(([_, data]) => data.active);

      if (activeMethods.length === 1) {
        const [method] = activeMethods[0];
        this.payments[method].value = (dueAmountCents / 100).toFixed(2);
        return;
      }

      if (remaining <= 0) return;

      const emptyFields = activeMethods.filter(([_, data]) => !data.value || data.value === 0);

      if (emptyFields.length === 0) return;

      const share = Math.floor(remaining / emptyFields.length);
      let remainder = remaining % emptyFields.length;

      emptyFields.forEach(([method, data]) => {
        let val = share;
        if (remainder > 0) {
          val += 1;
          remainder -= 1;
        }

        this.payments[method].value = (val / 100).toFixed(2);
      });
    },
    clearValues() {
      Object.keys(this.payments).forEach(method => {
        this.payments[method].value = 0
        this.payments[method].tax = 0
      })
    },
    goToPayment() {
      console.log("Efetivar venda com:", this.cart, this.payments, this.total);
    },
    save() {
      this.validatePayments()

      let products = []
      let payments = []

      for (let item of Object.values(this.cart)) {
        products.push({
          "id": item.id, 
          "quantity": item.quantity
        });
      }


      for (let p of Object.values(this.payments)) {
        if (p.active) {
          payments.push({
            "method": p.method, 
            "value": p.value
          });
        }
      }

      let totalFee = Object.values(this.payments)
        .filter(p => p.active)
        .reduce((acc, p) => acc + (parseFloat(p.tax) || 0), 0);
      
      let request = {
        payment: payments,
        items: products,
        discount: this.discountValue,
        fee: totalFee,
        sale_date: this.retrodate
      }

      if (payments.length == 1 && payments[0].method == "cash"){
        request["change"] = this.calcChange
      }

      console.log(request)

      this.$emit("submit-request", request)
    },
  },
  template: `
    <div>
      <section class="saleform__items__section">
        <ul class="saleform__items__container">
          <li v-for="item in cart" :key="item.id" class="saleform__items__item">
            <input type="number" min="1" v-model.number="item.quantity" @input="updateQuantity(item.id, item.quantity)" @blur="validateQuantity(item.id)"" />
            <p><strong>{{ item.product }}</strong></p>
            <p>R$ {{ (item.unit_price * item.quantity).toFixed(2) }}</p>
            <button @click="removeFromCart(item.id)" class="saleform__items__item__delete btn">Remover item</button>
          </li>
        </ul>

        <div class="mt-2">
          <p>{{ cart.length }} itens</p>
          <p>Total: R$ {{ total.toFixed(2) }}</p>
        </div>

        <!-- Desconto -->
        <div class="saleform__sale__props mb-2">
          <button @click="toggleDiscount" class="btn w-50 mt-3">Aplicar Desconto</button>
          <div v-if="discountActive" class="d-flex flex-col mb-3">
            <label class="mt-3">Desconto (%):</label>
            <input type="number" class="input" min=0 v-model.number="discountPercentage" @input="applyDiscountPercentage(discountPercentage)"/>
            <label class="mt-3">Desconto (R$):</label>
            <input type="number" class="input" min=0 v-model.number="discountValue" @input="applyDiscountValue(discountValue)" />
          </div>

          <button @click="toggleRetroactiveSale" class="btn w-50 mt-2">Venda Retroativa</button>
          <div v-if="retroactiveSale" class="d-flex flex-col mt-2 mb-3">
            <label for="saleDate">Insira a data em que a venda foi feita:</label>
            <input v-model="retrodate" class="input" type="datetime-local" id="saleDate" required/>
          </div>
        </div>

        <hr />

        <!-- Ações -->
        <div class="saleform__sale__actions mt-2">
          <button @click="showPayment = true" class="btn btn--medium btn--blue mr-2">Ir para pagamento</button>
          <button @click="cancelSale" class="btn btn--medium">Cancelar venda</button>
        </div>

      </section>

      <Modal v-model:show="showPayment">
        <!-- Pagamentos -->
        <div>
          <h3>Formas de pagamento</h3>

          <div class="mt-3">
            <span v-for="(p, method) in payments" :key="'ch-' + method">
              <input type="checkbox" v-model="p.active" /> {{ p.alias.toUpperCase() }}
              &nbsp; </span>
          </div>

          <div class="mt-3">
            <button @click="autoComplete" class="btn mr-1">Preenchimento automático</button>
            <button @click="clearValues" class="btn">Limpar valores</button>
          </div>

         <div v-for="(p, method) in payments" :key="'f-' + method" class="mt-3">
            <div v-if="p.active" class="d-flex flex-col">
              <strong>{{ p.alias.toUpperCase() }}: </strong>
              
              <label class="mt-3">Valor Pago:</label>
              <input type="number" class="input" min=0 v-model.number="p.value" :placeholder="showDifference.toFixed(2)" />
              
              <label class="mt-2">Taxa aplicada:</label>
              <input type="number" class="input mb-3" min=0 v-model.number="p.tax" />
              
              <hr />
            </div>
          </div>

          <div class="mt-3">
            <p>Total devido: R$ {{ dueAmount.toFixed(2) }}</p>
            <p>Total pago: R$ {{ sumPayments.toFixed(2) }}</p>
            <p v-if="payments.cash.active">Troco: R$ {{ calcChange.toFixed(2)}}</p>
          </div>

          <button @click="save" class="btn btn--medium btn--submit mt-3">Registrar venda</button>
        </div>
      </Modal>
    </div>
  `
};

