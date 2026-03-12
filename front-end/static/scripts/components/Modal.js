export default {
  name: "Modal",
  props: {
    show: {
      type: Boolean,
      default: false
    },
    onClose: {
      type: Function,
      default: null
    }
  },
  methods: {
    close() {
      // Se a função onClose existir, executa ela
      if (this.onClose) {
        this.onClose();
      }
      this.$emit("update:show", false);
    }
  },
  template: `
    <div v-show="show" class="modal__overlay" @click.self="close">
      <div class="modal__content">
        <header class="modal__header">
          <button class="modal__close" @click="close">×</button>
        </header>

        <section class="modal__body">
          <slot>
            Conteúdo do modal aqui...
          </slot>
        </section>
      </div>
    </div>
  `
}
