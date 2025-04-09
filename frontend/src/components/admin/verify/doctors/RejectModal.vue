<template>
  <div class="reject-modal">
    <div class="modal-overlay" @click.self="$emit('cancel')"></div>
    <div class="modal-content">
      <div class="modal-header">
        <i class="fas fa-user-md header-icon"></i>
        <h3>Reject Doctor Verification</h3>
        <button class="close-btn" @click="$emit('cancel')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="doctor-preview" v-if="doctor">
          <div class="avatar">
            <img :src="doctor.avatar || defaultAvatar" alt="Doctor Avatar">
          </div>
          <div class="details">
            <h4>Dr. {{ doctor.fullName }}</h4>
            <p class="specialty">{{ doctor.specialization }}</p>
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
            placeholder="Please specify the clinical or administrative reason for rejecting this doctor's verification..."
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
    doctor: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      rejectionReason: '',
      defaultAvatar: '/images/default-doctor.png'
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
@import '@fortawesome/fontawesome-free/css/all.min.css';

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
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.15);
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
  border-bottom: 1px solid #f0f0f0;
  background: #fff9f9;
  border-radius: 12px 12px 0 0;
}

.header-icon {
  font-size: 24px;
  color: #e74c3c;
  margin-right: 15px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #c0392b;
  font-weight: 600;
}

.close-btn {
  position: absolute;
  right: 20px;
  top: 20px;
  background: none;
  border: none;
  font-size: 18px;
  color: #95a5a6;
  cursor: pointer;
  padding: 5px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e74c3c;
}

.modal-body {
  padding: 20px;
}

.doctor-preview {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.doctor-preview .avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid #f0f0f0;
}

.doctor-preview .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.doctor-preview h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #2c3e50;
}

.doctor-preview .specialty {
  margin: 0;
  font-size: 14px;
  color: #7f8c8d;
  font-style: italic;
}

.reject-form label {
  display: block;
  margin-bottom: 12px;
  font-weight: 500;
  color: #2c3e50;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reject-form label i {
  color: #e74c3c;
}

.required {
  color: #e74c3c;
  margin-left: 3px;
}

.reject-form textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;
  line-height: 1.5;
}

.reject-form textarea:focus {
  outline: none;
  border-color: #e74c3c;
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.form-footer {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.char-count {
  text-align: right;
  font-size: 13px;
  color: #95a5a6;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: white;
  border: 1px solid #bdc3c7;
  color: #7f8c8d;
}

.btn-cancel:hover {
  background: #f5f5f5;
  border-color: #95a5a6;
}

.btn-submit {
  background: #e74c3c;
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #c0392b;
}

.btn-submit:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .modal-content {
    width: 95%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>