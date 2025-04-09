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
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>License Number</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input 
            type="text" 
            v-model="modelValue.license_number"
            placeholder="License number"
            @blur="validateLicenseNumber"
          >
        </div>
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
const PHARMACY_DEGREES = ['PharmD', 'BPharm', 'MPharm', 'DPharm'];

export default {
  props: {
    modelValue: {
      type: Object,
      required: true,
      default: () => ({
        pharmacy_id: '',
        specialization: '',
        degree: '',
        license_number: '',
        pharmacist_cert: null,
        profile_image: null
      })
    },
    pharmacies: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      pharmacyDegrees: PHARMACY_DEGREES,
      errors: {
        pharmacist_cert: '',
        profile_image: ''
      }
    };
  },
  methods: {
    updateHospitalId() {
      // Implement if needed
    },
    validateLicenseNumber() {
      const isValid = typeof this.modelValue.license_number === 'string' && 
                     [10, 12].includes(this.modelValue.license_number.length);
      if (!isValid) {
        this.$emit('error', 'License number must be 10 or 12 characters');
      }
      return isValid;
    },
    validateDegree() {
      const isValid = PHARMACY_DEGREES.includes(this.modelValue.degree);
      if (!isValid) {
        this.$emit('error', 'Please select a valid pharmacy degree');
      }
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
    validateForm() {
      return this.validateDegree() && this.validateLicenseNumber();
    }
  }
}
</script>