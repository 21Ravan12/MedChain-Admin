<template>
  <div class="role-fields">
    <div class="input-row">
      <div class="input-group">
        <label>Medical License Number*</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input 
            type="text" 
            v-model="modelValue.license_number"
            placeholder="State license number (8 or 12 characters)"
            @blur="validateLicenseNumber"
          >
        </div>
      </div>

      <div class="input-group">
        <label>Specialty*</label>
        <div class="input-field">
          <i class="fas fa-stethoscope"></i>
          <select v-model="modelValue.specialty" @change="validateSpecialty">
            <option value="">Select Specialty</option>
            <option v-for="specialty in medicalSpecialties" 
                    :value="specialty" 
                    :key="specialty">
              {{ specialty }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <div class="input-row">
      <!-- Hospital (Required) -->
      <div class="input-group">
        <label>Hospital*</label>
        <div class="input-field">
          <i class="fas fa-hospital"></i>
          <select v-model="modelValue.hospital_id">
            <option value="">Select Hospital</option>
            <option v-for="hospital in hospitals" 
                    :value="hospital.id" 
                    :key="hospital.id">
              {{ hospital.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Degree (Required) -->
      <div class="input-group">
        <label>Medical Degree*</label>
        <div class="input-field">
          <i class="fas fa-graduation-cap"></i>
          <select v-model="modelValue.degree" @change="validateDegree">
            <option value="">Select Degree</option>
            <option v-for="degree in medicalDegrees" 
                    :value="degree" 
                    :key="degree">
              {{ degree }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <div class="input-row">
      <!-- Available Hours (Optional) -->
      <div class="input-group">
        <label>Available Hours</label>
        <div class="input-field">
          <i class="fas fa-clock"></i>
          <input 
            type="text" 
            v-model="modelValue.available_hours"
            placeholder="e.g., Mon-Fri 9am-5pm"
          >
        </div>
      </div>

      <!-- Languages (Optional) -->
      <div class="input-group">
        <label>Languages Spoken</label>
        <div class="input-field">
          <i class="fas fa-language"></i>
          <input 
            type="text" 
            v-model="modelValue.languages"
            placeholder="e.g., English, Spanish"
          >
        </div>
      </div>
    </div>

    <!-- Profile Image (Optional) -->
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
const MEDICAL_SPECIALTIES = ['Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics', 'Neurology', 'General Practice'];
const MEDICAL_DEGREES = ['MD', 'DO', 'MBBS', 'MBChB'];

export default {
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    hospitals: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      medicalSpecialties: MEDICAL_SPECIALTIES,
      medicalDegrees: MEDICAL_DEGREES
    };
  },
  methods: {
    validateLicenseNumber() {
      const isValid = typeof this.modelValue.license_number === 'string' && 
                      [8, 12].includes(this.modelValue.license_number.length);
      if (!isValid) {
        this.$emit('error', 'License number must be 8 or 12 characters');
      }
      return isValid;
    },
    validateSpecialty() {
      const isValid = MEDICAL_SPECIALTIES.includes(this.modelValue.specialty);
      if (!isValid) {
        this.$emit('error', 'Please select a valid medical specialty');
      }
      return isValid;
    },
    validateDegree() {
      const isValid = MEDICAL_DEGREES.includes(this.modelValue.degree);
      if (!isValid) {
        this.$emit('error', 'Please select a valid medical degree');
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