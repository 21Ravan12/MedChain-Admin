<template>
    <div class="medical-dashboard">
      <PatientCard v-for="patient in patients" :key="patient.id" :patient="patient" />
      <DataEncryptor />
    </div>
  </template>
  
  <script>
  import PatientCard from '@/components/medical/PatientCard'
  import DataEncryptor from '@/components/medical/DataEncryptor'
  
  export default {
    components: {
      PatientCard,
      DataEncryptor
    },
    computed: {
      patients() {
        return this.$store.state.medicalAuth.patients
      }
    }
  }
  </script>