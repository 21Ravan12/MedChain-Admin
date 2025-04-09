<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content" role="dialog" aria-labelledby="modal-title" aria-modal="true">
      <div class="modal-header">
        <div class="header-icon-container">
          <i class="fas fa-user-plus header-icon" aria-hidden="true"></i>
        </div>
        <h3 id="modal-title">Add New User</h3>
        <button 
          class="close-btn" 
          @click="$emit('cancel')"
          aria-label="Close modal"
        >
          <i class="fas fa-times" aria-hidden="true"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="submitForm" novalidate>
          <div class="form-group">
            <label for="name">Full Name <span class="required">*</span></label>
            <input 
              id="name" 
              v-model.trim="user.name" 
              type="text" 
              required
              placeholder="Enter full name"
              aria-required="true"
              :class="{ 'input-error': errors.name }"
              @input="errors.name = ''"
            >
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>
          
          <div class="form-group">
            <label for="email">Email <span class="required">*</span></label>
            <input 
              id="email" 
              v-model.trim="user.email" 
              type="email" 
              required
              placeholder="Enter email address"
              aria-required="true"
              :class="{ 'input-error': errors.email }"
              @input="errors.email = ''"
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>
          
          <div class="form-group">
            <label for="role">Role <span class="required">*</span></label>
            <select 
              id="role" 
              v-model="user.role" 
              required
              aria-required="true"
              :class="{ 'input-error': errors.role }"
              @change="errors.role = ''"
            >
              <option value="" disabled>Select role</option>
              <option value="admin">Admin</option>
              <option value="doctor">Doctor</option>
              <option value="pharmacist">Pharmacist</option>
              <option value="patient">Patient</option>
            </select>
            <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
          </div>
          
          <div class="form-group">
            <label for="password">Password <span class="required">*</span></label>
            <div class="password-input-container">
              <input 
                id="password" 
                v-model="user.password" 
                :type="showPassword ? 'text' : 'password'" 
                required
                placeholder="Create password"
                minlength="8"
                aria-required="true"
                :class="{ 'input-error': errors.password }"
                @input="errors.password = ''"
              >
              <button 
                type="button" 
                class="toggle-password"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <p class="help-text">Minimum 8 characters</p>
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>
          
          <div class="form-group">
            <label for="avatar">Profile Picture</label>
            <div class="avatar-upload">
              <img 
                :src="user.avatar || defaultAvatar" 
                alt="Profile preview" 
                class="avatar-preview"
                :class="{ 'default-avatar': !user.avatar }"
              >
              <div class="avatar-upload-controls">
                <input 
                  id="avatar" 
                  type="file" 
                  accept="image/*" 
                  @change="handleAvatarUpload"
                  aria-describedby="avatar-help"
                >
                <label for="avatar" class="btn btn-outline">
                  <i class="fas fa-upload"></i> Choose Image
                </label>
                <button 
                  v-if="user.avatar" 
                  type="button" 
                  class="btn btn-text btn-remove"
                  @click="user.avatar = null"
                >
                  <i class="fas fa-trash-alt"></i> Remove
                </button>
              </div>
              <p id="avatar-help" class="help-text">JPG, PNG up to 2MB</p>
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              type="button" 
              class="btn btn-cancel" 
              @click="$emit('cancel')"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <template v-if="isSubmitting">
                <i class="fas fa-spinner fa-spin"></i> Saving...
              </template>
              <template v-else>
                <i class="fas fa-save"></i> Save User
              </template>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: {
        name: '',
        email: '',
        role: '',
        password: '',
        avatar: null
      },
      errors: {
        name: '',
        email: '',
        role: '',
        password: ''
      },
      defaultAvatar: '/images/avatars/default-user.png',
      showPassword: false,
      isSubmitting: false
    }
  },
  methods: {
    validateForm() {
      let isValid = true;
      
      if (!this.user.name.trim()) {
        this.errors.name = 'Name is required';
        isValid = false;
      }
      
      if (!this.user.email.trim()) {
        this.errors.email = 'Email is required';
        isValid = false;
      } else if (!/^\S+@\S+\.\S+$/.test(this.user.email)) {
        this.errors.email = 'Please enter a valid email';
        isValid = false;
      }
      
      if (!this.user.role) {
        this.errors.role = 'Please select a role';
        isValid = false;
      }
      
      if (!this.user.password) {
        this.errors.password = 'Password is required';
        isValid = false;
      } else if (this.user.password.length < 8) {
        this.errors.password = 'Password must be at least 8 characters';
        isValid = false;
      }
      
      return isValid;
    },
    async submitForm() {
      if (!this.validateForm()) return;
      
      this.isSubmitting = true;
      
      try {
        await this.$emit('save', {
          ...this.user,
          status: 'active',
          lastActive: new Date().toISOString()
        });
        this.resetForm();
      } catch (error) {
        console.error('Error saving user:', error);
      } finally {
        this.isSubmitting = false;
      }
    },
    resetForm() {
      this.user = {
        name: '',
        email: '',
        role: '',
        password: '',
        avatar: null
      };
      this.errors = {
        name: '',
        email: '',
        role: '',
        password: ''
      };
      this.showPassword = false;
    },
    handleAvatarUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Validate file size (2MB max)
      if (file.size > 2 * 1024 * 1024) {
        alert('File size should not exceed 2MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        this.user.avatar = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }
}
</script>

<style scoped>
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
  backdrop-filter: blur(2px);
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 10px;
  width: 500px;
  max-width: 95%;
  max-height: 95vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  transform: translateY(0);
  transition: transform 0.3s ease, opacity 0.3s ease;
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
}

.header-icon-container {
  background: #4a6cf7;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon {
  font-size: 16px;
}

.modal-header h3 {
  margin: 0;
  flex: 1;
  color: #2d3748;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #6c757d;
  cursor: pointer;
  transition: color 0.2s;
  padding: 5px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #495057;
  background-color: #f8f9fa;
}

.modal-body {
  padding: 25px;
}

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9375rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  background-color: #f8fafc;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.input-error {
  border-color: #e53e3e !important;
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1) !important;
}

.error-message {
  display: block;
  margin-top: 6px;
  color: #e53e3e;
  font-size: 0.8125rem;
}

.required {
  color: #e53e3e;
}

.help-text {
  font-size: 0.8125rem;
  color: #718096;
  margin-top: 6px;
}

.avatar-upload {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-top: 10px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.default-avatar {
  padding: 15px;
  background-color: #edf2f7;
}

.avatar-upload-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.avatar-upload input[type="file"] {
  display: none;
}

.password-input-container {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 5px;
}

.toggle-password:hover {
  color: #4a5568;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 2rem;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  padding: 10px 18px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-cancel {
  background: #f8f9fa;
  color: #4a5568;
  border-color: #e2e8f0;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-outline {
  background: white;
  color: #4a6cf7;
  border-color: #4a6cf7;
}

.btn-outline:hover {
  background: #f5f8ff;
}

.btn-text {
  background: none;
  color: #718096;
  padding: 0;
}

.btn-text:hover {
  color: #4a5568;
  text-decoration: underline;
}

.btn-remove {
  color: #e53e3e;
}

.btn-remove:hover {
  color: #c53030;
}

.btn-primary {
  background: #4a6cf7;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3a5bef;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    transform: translateY(20px);
    opacity: 0.9;
  }
  to { 
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 576px) {
  .avatar-upload {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .modal-header {
    padding: 16px;
  }
  
  .modal-body {
    padding: 16px;
  }
}
</style>