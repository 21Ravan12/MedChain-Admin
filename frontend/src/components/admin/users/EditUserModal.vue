<template>
    <div class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-content">
        <div class="modal-header">
          <i class="fas fa-user-edit header-icon"></i>
          <h3>Edit User</h3>
          <button class="close-btn" @click="$emit('cancel')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <div class="form-group">
              <label for="name">Full Name <span class="required">*</span></label>
              <input 
                id="name" 
                v-model="editedUser.name" 
                type="text" 
                required
                placeholder="Enter full name"
              >
            </div>
            
            <div class="form-group">
              <label for="email">Email <span class="required">*</span></label>
              <input 
                id="email" 
                v-model="editedUser.email" 
                type="email" 
                required
                placeholder="Enter email address"
              >
            </div>
            
            <div class="form-group">
              <label for="role">Role <span class="required">*</span></label>
              <select id="role" v-model="editedUser.role" required>
                <option value="admin">Admin</option>
                <option value="doctor">Doctor</option>
                <option value="pharmacist">Pharmacist</option>
                <option value="patient">Patient</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="status">Status</label>
              <select id="status" v-model="editedUser.status">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="avatar">Profile Picture</label>
              <div class="avatar-upload">
                <img 
                  :src="editedUser.avatar || defaultAvatar" 
                  alt="Preview" 
                  class="avatar-preview"
                >
                <input 
                  id="avatar" 
                  type="file" 
                  accept="image/*" 
                  @change="handleAvatarUpload"
                >
                <label for="avatar" class="btn btn-outline">
                  <i class="fas fa-upload"></i> Change
                </label>
                <button 
                  v-if="editedUser.avatar" 
                  type="button" 
                  class="btn btn-outline btn-danger" 
                  @click="removeAvatar"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn btn-cancel" @click="$emit('cancel')">
                Cancel
              </button>
              <button type="submit" class="btn btn-success">
                <i class="fas fa-save"></i> Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      user: {
        type: Object,
        required: true
      }
    },
    data() {
      return {
        editedUser: {...this.user},
        defaultAvatar: '/images/avatars/default-user.png'
      }
    },
    methods: {
      submitForm() {
        this.$emit('save', this.editedUser);
      },
      handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.editedUser.avatar = e.target.result;
          };
          reader.readAsDataURL(file);
        }
      },
      removeAvatar() {
        this.editedUser.avatar = null;
      }
    }
  }
  </script>
  
  <style scoped>
  /* Same styles as AddUserModal */
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
    width: 500px;
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .modal-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .modal-header h3 {
    margin: 0;
    flex: 1;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 20px;
    color: #6c757d;
    cursor: pointer;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
  }
  
  .form-group input,
  .form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
  }
  
  .required {
    color: #dc3545;
  }
  
  .avatar-upload {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
  }
  
  .avatar-preview {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid #eee;
  }
  
  .avatar-upload input[type="file"] {
    display: none;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }
  
  .btn-cancel {
    background: #6c757d;
    color: white;
  }
  
  .btn-cancel:hover {
    background: #5a6268;
  }
  </style>