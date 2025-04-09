<template>
    <div class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-content confirmation-modal">
        <div class="modal-header">
          <i class="fas fa-exclamation-circle header-icon"></i>
          <h3>{{ title }}</h3>
        </div>
        
        <div class="modal-body">
          <p>{{ message }}</p>
          
          <div class="confirmation-actions">
            <button class="btn btn-cancel" @click="$emit('cancel')">
              <i class="fas fa-times"></i> Cancel
            </button>
            <button class="btn btn-danger" @click="$emit('confirm')">
              <i class="fas fa-check"></i> Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      title: {
        type: String,
        default: 'Confirm Action'
      },
      message: {
        type: String,
        required: true
      }
    }
  }
  </script>
  
  <style scoped>
  .confirmation-modal {
    max-width: 400px;
    text-align: center;
  }
  
  .modal-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h3 {
    margin: 0;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-body p {
    margin-bottom: 25px;
    line-height: 1.5;
  }
  
  .confirmation-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
  }
  
  .btn-cancel {
    background: #6c757d;
    color: white;
  }
  
  .btn-danger {
    background: #dc3545;
    color: white;
  }
  
  /* Shared modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .header-icon {
    color: #dc3545;
    font-size: 24px;
  }
  </style>