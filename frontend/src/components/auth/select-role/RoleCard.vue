<template>
    <button 
      type="button" 
      @click="$emit('click')"
      :class="['role-card', { 'selected': selected }]"
    >
      <i :class="role.icon"></i>
      <span>{{ role.label }}</span>
    </button>
  </template>
  
  <script>
  export default {
    props: {
      role: {
        type: Object,
        required: true
      },
      selected: {
        type: Boolean,
        default: false
      }
    }
  }
  </script>
  
  <style scoped>
  .role-card {
    padding: 1.5rem;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    background: #f8f9fa;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .role-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }
  
  .role-card.selected {
    border-color: #1976d2;
    background: #e3f2fd;
  }
  
  .role-card i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: #1976d2;
  }
  </style>