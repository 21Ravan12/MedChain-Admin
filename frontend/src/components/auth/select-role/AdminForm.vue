<template>
  <div class="role-fields">
    <div class="input-group">
      <label>Security Level*</label>
      <select v-model="securityLevel" @change="updateSecurityLevel">
        <option value="">Select security level</option>
        <option v-for="level in adminSecurityLevels" :value="level" :key="level">
          {{ level }}
        </option>
      </select>
    </div>

    <div class="input-group">
      <label>Admin Profile Image</label>
      <div class="file-upload-wrapper">
        <div class="file-upload-input">
          <i class="fas fa-image"></i>
          <span>{{ modelValue.profileImage?.name || 'Select profile image' }}</span>
          <input 
            type="file" 
            @change="handleProfileImageUpload($event)" 
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
const ADMIN_SECURITY_LEVELS = ['standard', 'elevated', 'super'];

export default {
  name: 'AdminForm',
  props: {
    modelValue: {
      type: Object,
      required: true,
      default: () => ({
        profileImage: null,
        securityLevel: 'standard'
      })
    }
  },
  data() {
    return {
      adminSecurityLevels: ADMIN_SECURITY_LEVELS,
      securityLevel: this.modelValue.securityLevel || 'standard'
    };
  },
  methods: {
    updateSecurityLevel() {
      const updatedValue = { 
        ...this.modelValue, 
        securityLevel: this.securityLevel 
      };
      this.$emit('update:modelValue', updatedValue);
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
        const updatedValue = { 
          ...this.modelValue, 
          profileImage: {
            name: file.name,
            data: reader.result, // Using full data URL including prefix
            type: file.type
          }
        };
        this.$emit('update:modelValue', updatedValue);
      };
      reader.readAsDataURL(file);
    }
  },
  watch: {
    'modelValue.securityLevel'(newVal) {
      this.securityLevel = newVal;
    }
  }
}
</script>