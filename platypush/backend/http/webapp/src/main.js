import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'

const app = createApp(App)
app.config.globalProperties._config = window.config
app.use(router).mount('#app')
