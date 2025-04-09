<template>
    <div class="patient-card">
      <h4>{{ patient.name }}</h4>
      <div class="medical-data">
        <span>Kan Grubu: {{ patient.bloodType }}</span>
        <span>Son Muayene: {{ patient.lastCheckup }}</span>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: ['patient']
  }
  </script>