<template>
  <div class="role-fields">
    <div class="input-row">
      <!-- Hospital (Required) -->
      <div class="input-group">
        <label>Hospital*</label>
        <div class="input-field">
          <i class="fas fa-hospital"></i>
          <select v-model="modelValue.hospital_id" @change="updateHospitalName">
            <option value="">Select Hospital</option>
            <option v-for="hospital in hospitals" 
                    :value="hospital.id" 
                    :key="hospital.id">
              {{ hospital.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Department (Required) -->
      <div class="input-group">
        <label>Department*</label>
        <div class="input-field">
          <i class="fas fa-building"></i>
          <select v-model="modelValue.department" @change="validateDepartment">
            <option value="">Select Department</option>
            <option v-for="dept in hospitalDepartments" 
                    :value="dept" 
                    :key="dept">
              {{ dept }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <div class="input-row">
      <!-- Admin ID (Required) -->
      <div class="input-group">
        <label>Admin ID*</label>
        <div class="input-field">
          <i class="fas fa-id-card"></i>
          <input type="text" 
                 v-model="modelValue.admin_id"
                 placeholder="8-character admin ID"
                 @blur="validateAdminId">
        </div>
      </div>

      <!-- Qualifications (Required) -->
      <div class="input-group">
        <label>Qualifications*</label>
        <div class="input-field">
          <i class="fas fa-certificate"></i>
          <input type="text" 
                 v-model="qualificationsInput"
                 placeholder="Add qualification (press Enter)"
                 @keydown.enter="addQualification">
          <div class="tags" v-if="modelValue.qualifications?.length">
            <span class="tag" v-for="(qual, index) in modelValue.qualifications" :key="index">
              {{ qual }}
              <i class="fas fa-times" @click="removeQualification(index)"></i>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="input-row">
      <!-- Access Level (Optional) -->
      <div class="input-group">
        <label>Access Level</label>
        <div class="input-field">
          <i class="fas fa-shield-alt"></i>
          <select v-model="modelValue.access_level">
            <option value="">Select Access Level</option>
            <option v-for="level in accessLevels" 
                    :value="level" 
                    :key="level">
              {{ level }}
            </option>
          </select>
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

    <div class="input-row">
    <div class="input-group">
      <label>License Document*</label>  <!-- Added * to indicate required -->
      <div class="file-upload-wrapper">
        <div class="file-upload-input">
          <i class="fas fa-file-upload"></i>
          <span>{{ modelValue.license_document?.name || 'Select license document' }}</span>
          <input 
            type="file" 
            @change="handleFileUpload('license', $event)" 
            ref="licenseInput" 
            style="display: none;"
            accept="application/pdf,image/jpeg,image/png"
            required
          >
        </div>
        <button class="btn-file" @click="$refs.licenseInput.click()">Browse</button>
      </div>
    </div>
  </div>

  </div>
</template>

<script>
const HOSPITAL_DEPARTMENTS = [
  'Administration', 'Finance', 'HR', 'IT', 
  'Medical Records', 'Nursing', 'Pharmacy', 'Laboratory'
];

const ACCESS_LEVELS = ['basic', 'intermediate', 'advanced', 'full'];

export default {
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    hospitals: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      hospitalDepartments: HOSPITAL_DEPARTMENTS,
      accessLevels: ACCESS_LEVELS,
      qualificationsInput: '',
      hospitalName: ''
    };
  },
  methods: {
    updateHospitalName() {
      const selectedHospital = this.hospitals.find(h => h.id === this.modelValue.hospital_id);
      this.hospitalName = selectedHospital ? selectedHospital.name : '';
      this.$emit('update:modelValue', {
        ...this.modelValue,
        hospital_name: this.hospitalName
      });
    },
    validateDepartment() {
      const isValid = HOSPITAL_DEPARTMENTS.includes(this.modelValue.department);
      if (!isValid) {
        this.$emit('error', 'Please select a valid department');
      }
      return isValid;
    },
    validateAdminId() {
      const isValid = typeof this.modelValue.admin_id === 'string' && 
                     this.modelValue.admin_id.length === 8;
      if (!isValid) {
        this.$emit('error', 'Admin ID must be exactly 8 characters');
      }
      return isValid;
    },
    addQualification(e) {
      e.preventDefault();
      const qual = this.qualificationsInput.trim();
      if (!qual) return;

      const qualifications = this.modelValue.qualifications || [];
      if (!qualifications.includes(qual)) {
        qualifications.push(qual);
        this.$emit('update:modelValue', {
          ...this.modelValue,
          qualifications
        });
      }
      this.qualificationsInput = '';
    },
    removeQualification(index) {
      const qualifications = [...this.modelValue.qualifications];
      qualifications.splice(index, 1);
      this.$emit('update:modelValue', {
        ...this.modelValue,
        qualifications
      });
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
    },
    handleFileUpload(type, event) {
      const file = event.target.files[0];
      if (!file) return;

      const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!validTypes.includes(file.type)) {
        this.$emit('error', 'Invalid file type. Please upload a PDF, JPEG, or PNG file.');
        return;
      }

      if (file.size > maxSize) {
        this.$emit('error', 'File size exceeds 10MB limit.');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = reader.result.split(',')[1];
        this.$emit('update:modelValue', {
          ...this.modelValue,
          [`${type}_document`]: {
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

<style scoped>
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.tag {
  background: #e0e0e0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.tag i {
  cursor: pointer;
}
</style>
