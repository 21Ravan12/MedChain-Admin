// src/store/index.js
import { createStore } from 'vuex'
import medicalAuth from './modules/medicalAuth'
import admin from './modules/admin'

export default createStore({
  modules: {
    medicalAuth,
    admin
  }
})