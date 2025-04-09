<template>
  <div class="role-fields">
    <div class="input-row">
      <!-- Required Fields -->
      <div class="input-group">
        <label>License Number*</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input 
            type="text" 
            v-model="modelValue.license_number"
            placeholder="Must start with PHARM-"
            @blur="validateLicenseNumber"
            :class="{ 'invalid': errors.license_number }"
          >
          <span class="error-message" v-if="errors.license_number">{{ errors.license_number }}</span>
        </div>
      </div>

<div class="input-row">
  <div class="input-group">
    <label for="pharmacy-type">Pharmacy Type</label>
    <div class="input-field">
      <i class="fas fa-prescription-bottle-alt"></i>
      <select 
        id="pharmacy-type"
        v-model="modelValue.type"
        class="pharmacy-type-select"
      >
        <option value="" disabled>Select pharmacy type</option>
        <option value="retail">Retail Pharmacy</option>
        <option value="compounding">Compounding Pharmacy</option>
        <option value="hospital">Hospital Pharmacy</option>
        <option value="online">Online Pharmacy</option>
        <option value="specialty">Specialty Pharmacy</option>
        <option value="mail_order">Mail Order Pharmacy</option>
      </select>
    </div>
  </div>
</div>

      <div class="input-group">
        <label>Address*</label>
        <div class="input-field">
          <i class="fas fa-map-marker-alt"></i>
          <input 
            type="text" 
            v-model="modelValue.address"
            placeholder="Full pharmacy address"
            @blur="validateAddress"
            :class="{ 'invalid': errors.address }"
          >
          <span class="error-message" v-if="errors.address">{{ errors.address }}</span>
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Establishment Date</label>
        <div class="input-field">
          <i class="fas fa-calendar-alt"></i>
          <input 
            type="date" 
            v-model="modelValue.established"
            :max="new Date().toISOString().split('T')[0]"
          >
        </div>
      </div>

      <div class="input-group">
        <label>Operating Hours</label>
        <div class="input-field">
          <i class="fas fa-clock"></i>
          <input 
            type="text" 
            v-model="modelValue.operating_hours"
            placeholder="e.g., 24/7 or 9AM-5PM"
          >
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Inventory Size</label>
        <div class="input-field">
          <i class="fas fa-boxes"></i>
          <input 
            type="number" 
            v-model.number="modelValue.inventory_size"
            placeholder="Number of items"
            min="0"
          >
        </div>
      </div>

      <div class="input-group">
        <label>Pharmacists Count</label>
        <div class="input-field">
          <i class="fas fa-user-md"></i>
          <input 
            type="number" 
            v-model.number="modelValue.pharmacists_count"
            placeholder="Number of pharmacists"
            min="0"
          >
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>License Document*</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input" :class="{ 'invalid': errors.license_document }">
            <i class="fas fa-file-upload"></i>
            <span>{{ modelValue.license_document?.name || 'Select license document' }}</span>
            <input 
              type="file" 
              @change="handleFileUpload('license', $event)" 
              ref="licenseInput" 
              accept="application/pdf,image/jpeg,image/png"
              style="display: none;"
            >
          </div>
          <button class="btn-file" @click="$refs.licenseInput.click()">Browse</button>
          <span class="error-message" v-if="errors.license_document">{{ errors.license_document }}</span>
        </div>
      </div>
      
      <div class="input-group">
        <label>Accreditation Document</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input">
            <i class="fas fa-file-alt"></i>
            <span>{{ modelValue.accreditation_document?.name || 'Select accreditation document' }}</span>
            <input 
              type="file" 
              @change="handleFileUpload('accreditation', $event)" 
              ref="accreditationInput" 
              accept="application/pdf,image/jpeg,image/png"
              style="display: none;"
            >
          </div>
          <button class="btn-file" @click="$refs.accreditationInput.click()">Browse</button>
        </div>
      </div>
    </div>

    <div class="input-group">
      <label>Pharmacy Logo</label>
      <div class="file-upload-wrapper">
        <div class="file-upload-input">
          <i class="fas fa-image"></i>
          <span>{{ modelValue.logo?.name || 'Select logo image' }}</span>
          <input 
            type="file" 
            @change="handleFileUpload('logo', $event)" 
            ref="logoInput" 
            accept="image/jpeg,image/png"
            style="display: none;"
          >
        </div>
        <button class="btn-file" @click="$refs.logoInput.click()">Browse</button>
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
        license_number: '',
        address: '',
        established: '',
        operating_hours: '',
        inventory_size: null,
        pharmacists_count: null,
        license_document: null,
        accreditation_document: null,
        logo: null
      })
    }
  },
  data() {
    return {
      errors: {
        license_number: '',
        address: '',
        license_document: ''
      }
    }
  },
  methods: {
    validateLicenseNumber() {
      if (!this.modelValue.license_number) {
        this.errors.license_number = 'License number is required';
      } else if (!this.modelValue.license_number.startsWith('PHARM-')) {
        this.errors.license_number = 'License number must start with PHARM-';
      } else {
        this.errors.license_number = '';
      }
    },
    validateAddress() {
      if (!this.modelValue.address) {
        this.errors.address = 'Address is required';
      } else if (this.modelValue.address.length < 10) {
        this.errors.address = 'Address must be at least 10 characters';
      } else {
        this.errors.address = '';
      }
    },
    validateForm() {
      this.validateLicenseNumber();
      this.validateAddress();
      
      if (!this.modelValue.license_document) {
        this.errors.license_document = 'License document is required';
      } else {
        this.errors.license_document = '';
      }
      
      return !Object.values(this.errors).some(error => error);
    },
    handleFileUpload(field, event) {
      const file = event.target.files[0];
      if (!file) return;

      let validTypes, maxSize, errorField = '';
      
      if (field === 'logo') {
        validTypes = ['image/jpeg', 'image/png'];
        maxSize = 5 * 1024 * 1024; // 5MB
      } else {
        validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
        maxSize = 10 * 1024 * 1024; // 10MB
        errorField = `${field}_document`;
      }

      if (!validTypes.includes(file.type)) {
        const errorMsg = `Invalid file type. Accepted types: ${validTypes.join(', ')}`;
        if (errorField) this.errors[errorField] = errorMsg;
        this.$emit('error', errorMsg);
        return;
      }

      if (file.size > maxSize) {
        const errorMsg = `File too large (max ${maxSize/(1024*1024)}MB)`;
        if (errorField) this.errors[errorField] = errorMsg;
        this.$emit('error', errorMsg);
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        const fileData = {
          name: file.name,
          type: file.type,
          size: file.size,
          lastModified: file.lastModified,
          data: reader.result
        };

        const updatedValue = { 
          ...this.modelValue,
          [field === 'license' || field === 'accreditation' ? `${field}_document` : field]: fileData
        };
        
        this.$emit('update:modelValue', updatedValue);
        
        // Clear any previous errors
        if (errorField) this.errors[errorField] = '';
      };
      reader.onerror = () => {
        const errorMsg = 'Error reading file';
        if (errorField) this.errors[errorField] = errorMsg;
        this.$emit('error', errorMsg);
      };
      reader.readAsDataURL(file);
    }
  }
}
</script>