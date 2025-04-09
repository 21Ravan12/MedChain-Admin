<template>
  <div class="role-fields">
    <div class="input-row">
      <!-- Required Fields -->
      <div class="input-group">
        <label>Pharmacy*</label>
        <div class="input-field">
          <i class="fas fa-hospital"></i>
          <select v-model="modelValue.pharmacy_id" @change="updateHospitalId">
            <option value="">Select Pharmacy</option>
            <option v-for="pharmacy in pharmacies" 
                    :value="pharmacy.id" 
                    :key="pharmacy.id">
              {{ pharmacy.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="input-group">
        <label>Admin ID*</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input 
            type="text" 
            v-model="modelValue.admin_id"
            placeholder="8-character admin ID"
            @blur="validateAdminId"
            :class="{ 'error': errors.admin_id }"
          >
          <span class="error-message" v-if="errors.admin_id">{{ errors.admin_id }}</span>
        </div>
      </div>
    </div>

    <!-- Optional Fields -->
    <div class="input-row">
      <div class="input-group">
        <label>Access Level</label>
        <div class="input-field">
          <i class="fas fa-shield-alt"></i>
          <select v-model="modelValue.access_level">
            <option value="">Select Access Level</option>
            <option>basic</option>
            <option>standard</option>
            <option>premium</option>
          </select>
        </div>
      </div>

      <div class="input-group">
        <label>Pharmacist Certification</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input" :class="{ 'error': errors.pharmacist_cert }">
            <i class="fas fa-certificate"></i>
            <span>{{ modelValue.pharmacist_cert?.name || 'Upload certification' }}</span>
            <input 
              type="file" 
              @change="handleCertUpload" 
              ref="certInput" 
              style="display: none;"
              accept=".pdf,.jpg,.png"
            >
          </div>
          <button class="btn-file" @click="$refs.certInput.click()">Browse</button>
          <span class="error-message" v-if="errors.pharmacist_cert">{{ errors.pharmacist_cert }}</span>
        </div>
      </div>
    </div>

    <!-- Profile Image Upload -->
    <div class="input-group">
      <label>Profile Image</label>
      <div class="file-upload-wrapper">
        <div class="file-upload-input" :class="{ 'error': errors.profile_image }">
          <i class="fas fa-image"></i>
          <span>{{ modelValue.profile_image?.name || 'Select profile image' }}</span>
          <input 
            type="file" 
            @change="handleProfileImageUpload" 
            ref="profileImageInput" 
            style="display: none;"
            accept="image/jpeg,image/png"
          >
        </div>
        <button class="btn-file" @click="$refs.profileImageInput.click()">Browse</button>
        <span class="error-message" v-if="errors.profile_image">{{ errors.profile_image }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: Object,
      required: true,
      default: () => ({
        pharmacy_id: '',
        admin_id: '',
        access_level: '',
        pharmacist_cert: null,
        profile_image: null
      })
    },
    pharmacies: {
      type: Array,
      required: true,}
  },
  data() {
    return {
      errors: {
        admin_id: '',
        pharmacist_cert: '',
        profile_image: ''
      }
    }
  },
  methods: {
    validateForm() {
      const validations = [
        this.validateAdminId()
      ];
      return validations.every(v => v);
    },
    updateHospitalId() {
      // You can implement this method if needed
    },
    validateAdminId() {
      if (!this.modelValue.admin_id) {
        this.errors.admin_id = 'Admin ID is required';
        return false;
      }
      
      const isValid = typeof this.modelValue.admin_id === 'string' && 
                     this.modelValue.admin_id.length === 8;
      
      this.errors.admin_id = isValid ? '' : 'Admin ID must be exactly 8 characters';
      return isValid;
    },
    handleCertUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validTypes.includes(file.type)) {
        this.errors.pharmacist_cert = 'Invalid file type. Please upload PDF, JPEG, or PNG';
        return;
      }

      if (file.size > maxSize) {
        this.errors.pharmacist_cert = 'File size exceeds 5MB limit';
        return;
      }

      this.errors.pharmacist_cert = '';
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = reader.result.split(',')[1];
        this.$emit('update:modelValue', {
          ...this.modelValue,
          pharmacist_cert: {
            name: file.name,
            data: base64Data,
            type: file.type
          }
        });
      };
      reader.readAsDataURL(file);
    },
    handleProfileImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const validTypes = ['image/jpeg', 'image/png'];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validTypes.includes(file.type)) {
        this.errors.profile_image = 'Invalid file type. Please upload JPEG or PNG only';
        return;
      }

      if (file.size > maxSize) {
        this.errors.profile_image = 'File size exceeds 5MB limit';
        return;
      }

      this.errors.profile_image = '';
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = reader.result.split(',')[1];
        this.$emit('update:modelValue', {
          ...this.modelValue,
          profile_image: {
            name: file.name,
            data: base64Data,
            type: file.type
          }
        });
      };
      reader.readAsDataURL(file);
    },
    prepareSubmitData() {
      return {
        pharmacy_id: this.modelValue.pharmacy_id,
        admin_id: this.modelValue.admin_id,
        access_level: this.modelValue.access_level,
        pharmacist_cert: this.modelValue.pharmacist_cert?.data || null,
        profile_image: this.modelValue.profile_image?.data || null
      };
    }
  }
}
</script>