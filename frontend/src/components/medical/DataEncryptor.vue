<template>
    <div class="data-encryptor">
      <button @click="encryptData">
        <i class="fas fa-lock"></i>
        Verileri Şifrele
      </button>
    </div>
  </template>
  
  <script>
  export default {
    methods: {
      encryptData() {
        this.$store.dispatch('medicalAuth/encryptMedicalData')
      }
    }
  }
  </script>