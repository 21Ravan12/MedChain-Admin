<template>
  <div class="role-fields">
    <div class="input-group">
        <label>Hospital Logo</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input">
            <i class="fas fa-image"></i>
            <span>{{ modelValue.logo?.name || 'Select logo document' }}</span>
            <input type="file" @change="handleFileUpload('logo', $event)" ref="logoInput" style="display: none;">
          </div>
          <button class="btn-file" @click="$refs.logoInput.click()">Browse</button>
        </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Hospital Type</label>
        <div class="input-field">
          <i class="fas fa-clinic-medical"></i>
          <select v-model="modelValue.type">
            <option value="">Select type</option>
            <option>general</option>
            <option>specialty</option>
            <option>teaching</option>
          </select>
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Bed Count</label>
        <div class="input-field">
          <i class="fas fa-procedures"></i>
          <input type="number" 
                 v-model.number="modelValue.beds"
                 placeholder="Total beds">
        </div>
      </div>
      <div class="input-group">
        <label>Establishment Date</label>
        <div class="input-field">
          <i class="fas fa-calendar-alt"></i>
          <input type="date" v-model="modelValue.established">
        </div>
      </div>
    </div>

    <div class="input-group">
      <label>Location</label>
      <div class="input-field">
        <i class="fas fa-map-marker-alt"></i>
        <input type="text" 
               v-model="modelValue.address"
               placeholder="Full address">
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>License Number</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input type="text" 
                 v-model="modelValue.license_number"
                 placeholder="License number">
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>License Document</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input">
            <i class="fas fa-file-upload"></i>
            <span>{{ modelValue.license_document?.name || 'Select license document' }}</span>
            <input type="file" @change="handleFileUpload('license', $event)" ref="licenseInput" style="display: none;">
          </div>
          <button class="btn-file" @click="$refs.licenseInput.click()">Browse</button>
        </div>
      </div>
      
      <div class="input-group">
        <label>Accreditation Document</label>
        <div class="file-upload-wrapper">
          <div class="file-upload-input">
            <i class="fas fa-file-alt"></i>
            <span>{{ modelValue.accreditation_document?.name || 'Select accreditation document' }}</span>
            <input type="file" @change="handleFileUpload('accreditation', $event)" ref="accreditationInput" style="display: none;">
          </div>
          <button class="btn-file" @click="$refs.accreditationInput.click()">Browse</button>
        </div>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Operating Hours</label>
        <div class="input-field">
          <i class="fas fa-clock"></i>
          <input type="text" 
                 v-model="modelValue.operating_hours"
                 placeholder="e.g. 8:00 AM - 10:00 PM">
        </div>
      </div>
      <div class="input-group">
        <label>Emergency Services</label>
        <div class="input-field">
          <i class="fas fa-ambulance"></i>
          <select v-model="modelValue.emergency_services">
            <option :value="true">Available</option>
            <option :value="false">Not Available</option>
          </select>
        </div>
      </div>
    </div>

    <div class="input-group">
      <label>Medical Staff Count</label>
      <div class="input-field">
        <i class="fas fa-user-md"></i>
        <input type="number" 
               v-model.number="modelValue.medical_staff"
               placeholder="Number of medical staff">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleFileUpload(field, event) {
  const file = event.target.files[0];
  if (!file) return;

  let validTypes, maxSize;
  
  if (field === 'logo') {
    validTypes = ['image/jpeg', 'image/png'];
    maxSize = 5 * 1024 * 1024; // 5MB
  } else { // For license and accreditation documents
    validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    maxSize = 10 * 1024 * 1024; // 10MB
  }

  if (!validTypes.includes(file.type)) {
    this.$emit('error', `Invalid file type for ${field}. Please upload ${validTypes.join(' or ')}.`);
    return;
  }

  if (file.size > maxSize) {
    this.$emit('error', `File size exceeds ${maxSize/(1024*1024)}MB limit for ${field}.`);
    return;
  }

  const reader = new FileReader();
  reader.onloadend = () => {
    const updatedValue = { 
      ...this.modelValue, 
      // Use consistent property names with underscores
      [field === 'logo' ? 'logo' : `${field}_document`]: {
        name: file.name,
        data: reader.result,
        type: file.type
      }
    };
    this.$emit('update:modelValue', updatedValue);
  };
  reader.readAsDataURL(file);
}
  }
}
</script>