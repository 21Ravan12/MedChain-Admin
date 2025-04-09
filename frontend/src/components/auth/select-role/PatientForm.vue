<template>
  <div class="role-fields">
    <!-- Required Fields -->
    <div class="input-row">
      <div class="input-group">
        <label>Birth Year*</label>
        <div class="input-field">
          <i class="fas fa-birthday-cake"></i>
          <input type="number" 
                 v-model.number="modelValue.birthyear"
                 placeholder="YYYY"
                 @blur="validateBirthyear"
                 min="1900"
                 :max="new Date().getFullYear()">
        </div>
      </div>
      <div class="input-group">
        <label>ID Proof*</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input type="text" 
                 v-model="modelValue.id_proof"
                 placeholder="ID number/document"
                 @blur="validateIdProof">
        </div>
      </div>
    </div>

    <div class="input-group">
      <label>Insurance Provider*</label>
      <div class="input-field">
        <i class="fas fa-shield-alt"></i>
        <input type="text" 
               v-model="modelValue.insurance"
               placeholder="Insurance company name"
               @blur="validateInsurance">
      </div>
    </div>

    <!-- Optional Fields -->
    <div class="input-group">
      <label>Medical History</label>
      <div class="input-field">
        <i class="fas fa-file-medical"></i>
        <textarea v-model="modelValue.medical_history" 
                  placeholder="Previous conditions, allergies..."></textarea>
      </div>
    </div>

    <div class="input-row">
      <div class="input-group">
        <label>Blood Type</label>
        <div class="input-field">
          <i class="fas fa-tint"></i>
          <select v-model="modelValue.blood_type">
            <option value="">Select</option>
            <option>A+</option>
            <option>A-</option>
            <option>B+</option>
            <option>B-</option>
            <option>O+</option>
            <option>O-</option>
            <option>AB+</option>
            <option>AB-</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Profile Image Upload -->
    <div class="input-group">
      <label>Profile Image</label>
      <div class="file-upload-wrapper">
        <div class="file-upload-input">
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
    validateBirthyear() {
      const currentYear = new Date().getFullYear();
      const isValid = Number.isInteger(this.modelValue.birthyear) && 
                     this.modelValue.birthyear >= 1900 && 
                     this.modelValue.birthyear <= currentYear;
      if (!isValid) {
        this.$emit('error', `Birth year must be between 1900 and ${currentYear}`);
      }
      return isValid;
    },
    validateIdProof() {
      const isValid = typeof this.modelValue.id_proof === 'string' && 
                     this.modelValue.id_proof.length > 10;
      if (!isValid) {
        this.$emit('error', 'ID proof must be at least 10 characters');
      }
      return isValid;
    },
    validateInsurance() {
      const isValid = typeof this.modelValue.insurance === 'string' && 
                     this.modelValue.insurance.length > 5;
      if (!isValid) {
        this.$emit('error', 'Insurance provider name must be at least 5 characters');
      }
      return isValid;
    },
    handleProfileImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const validTypes = ['image/jpeg', 'image/png'];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validTypes.includes(file.type)) {
        this.$emit('error', 'Invalid file type. Please upload JPEG or PNG only.');
        return;
      }

      if (file.size > maxSize) {
        this.$emit('error', 'File size exceeds 5MB limit.');
        return;
      }

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
    }
  }
}
</script>