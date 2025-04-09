<template>
    <div class="reject-modal">
      <div class="modal-overlay" @click.self="$emit('cancel')"></div>
      <div class="modal-content">
        <div class="modal-header">
          <i class="fas fa-shield-alt header-icon"></i>
          <h3>Reject Admin Verification</h3>
          <button class="close-btn" @click="$emit('cancel')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="admin-preview" v-if="admin">
            <div class="avatar">
              <img :src="admin.avatar || defaultAdmin" alt="Admin Photo">
            </div>
            <div class="details">
              <h4>{{ admin.name }}</h4>
              <p class="position">{{ admin.position }}</p>
            </div>
          </div>
          
          <div class="reject-form">
            <label for="rejectReason">
              <i class="fas fa-comment-alt"></i> Reason for rejection 
              <span class="required">*</span>
            </label>
            <textarea
              id="rejectReason"
              v-model="rejectionReason"
              placeholder="Please specify the reason for rejecting this admin's verification..."
              rows="5"
              maxlength="500"
            ></textarea>
            <div class="form-footer">
              <div class="char-count">{{ rejectionReason.length }}/500</div>
              <div class="action-buttons">
                <button 
                  class="btn btn-cancel"
                  @click="$emit('cancel')"
                >
                  Cancel
                </button>
                <button 
                  class="btn btn-submit"
                  :disabled="!rejectionReason.trim()"
                  @click="submitRejection"
                >
                  <i class="fas fa-ban"></i> Confirm Rejection
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      admin: {
        type: Object,
        default: null
      }
    },
    data() {
      return {
        rejectionReason: '',
        defaultAdmin: '/images/default-admin.png'
      }
    },
    methods: {
      submitRejection() {
        if (this.rejectionReason.trim()) {
          this.$emit('submit', this.rejectionReason);
          this.rejectionReason = '';
        }
      }
    },
    watch: {
      rejectionReason(newVal) {
        if (newVal.length > 500) {
          this.rejectionReason = newVal.slice(0, 500);
        }
      }
    }
  }
  </script>
    <style scoped>
    .reject-modal {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1050;
    }
    
    .modal-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
    }
    
    .modal-content {
      position: relative;
      background: white;
      border-radius: 8px;
      width: 100%;
      max-width: 500px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      animation: modalFadeIn 0.3s ease;
    }
    
    @keyframes modalFadeIn {
      from {
        opacity: 0;
        transform: translateY(-20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .modal-header {
      display: flex;
      align-items: center;
      padding: 20px;
      border-bottom: 1px solid #e8f0eb;
      position: relative;
    }
    
    .header-icon {
      font-size: 24px;
      color: #e76f51;
      margin-right: 15px;
    }
    
    .modal-header h3 {
      margin: 0;
      font-size: 18px;
      color: #2d3748;
    }
    
    .close-btn {
      position: absolute;
      right: 20px;
      top: 20px;
      background: none;
      border: none;
      font-size: 18px;
      color: #7b8a82;
      cursor: pointer;
      padding: 5px;
    }
    
    .close-btn:hover {
      color: #2d6a4f;
    }
    
    .modal-body {
      padding: 20px;
    }
    
    .admin-preview {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid #e8f0eb;
    }
    
    .admin-preview .avatar {
      width: 60px;
      height: 60px;
      border-radius: 8px;
      overflow: hidden;
      flex-shrink: 0;
    }
    
    .admin-preview .avatar img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .admin-preview h4 {
      margin: 0 0 5px 0;
      font-size: 16px;
      color: #2d3748;
    }
    
    .admin-preview .type {
      margin: 0;
      font-size: 14px;
      color: #718096;
    }
    
    .reject-form label {
      display: block;
      margin-bottom: 10px;
      font-weight: 500;
      color: #2d3748;
    }
    
    .required {
      color: #e76f51;
    }
    
    .reject-form textarea {
      width: 100%;
      padding: 12px;
      border: 1px solid #e8f0eb;
      border-radius: 6px;
      font-family: inherit;
      font-size: 14px;
      resize: vertical;
      min-height: 120px;
      transition: border-color 0.3s ease;
    }
    
    .reject-form textarea:focus {
      outline: none;
      border-color: #2d6a4f;
      box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.1);
    }
    
    .char-count {
      text-align: right;
      font-size: 12px;
      color: #a0aec0;
      margin-top: 5px;
    }
    
    .form-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 20px;
    }
    
    .btn {
      padding: 10px 20px;
      border-radius: 6px;
      font-weight: 500;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .btn-cancel {
      background: white;
      border: 1px solid #e8f0eb;
      color: #718096;
    }
    
    .btn-cancel:hover {
      background: #f8faf9;
      color: #2d6a4f;
    }
    
    .btn-submit {
      background: #e76f51;
      border: none;
      color: white;
    }
    
    .btn-submit:hover:not(:disabled) {
      background: #d64524;
    }
    
    .btn-submit:disabled {
      background: #b8c7ce;
      cursor: not-allowed;
    }
    
    /* Responsive adjustments */
    @media (max-width: 576px) {
      .modal-content {
        width: 95%;
        margin: 0 auto;
      }
      
      .form-footer {
        flex-direction: column;
      }
      
      .btn {
        width: 100%;
      }
    }
    </style>