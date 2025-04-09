// src/main.js
import { createApp } from 'vue' 
import App from './App.vue'
import router from './router'
import store from './store'

//axios.defaults.https = true
//axios.defaults.secure = true
import '@fortawesome/fontawesome-free/css/all.min.css'
import '@/assets/styles/authStyles.css';

const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')