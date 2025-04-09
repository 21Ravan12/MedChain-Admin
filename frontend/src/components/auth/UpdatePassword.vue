<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-lock"></i>
        </div>
        <h2>MEDICARE PRO <span>v2.0</span></h2>
        <p>Password Update System</p>
      </div>

      <form @submit.prevent="handleSubmit" class="medical-form">
        <input type="text" v-model="honeypot" style="display: none;">

        <div class="input-group">
          <label>New Password</label>
          <div class="input-field">
            <i class="fas fa-lock"></i>
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="••••••••"
              required
              @input="clearError"
              :class="{ 'input-error': errorMessage }"
            >
            <i 
              class="fas fa-eye toggle-password"
              :class="{ 'fa-eye-slash': showPassword }"
              @click="togglePasswordVisibility"
            ></i>
          </div>
        </div>

        <div class="input-group">
          <label>Confirm Password</label>
          <div class="input-field">
            <i class="fas fa-lock"></i>
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              v-model="confirmPassword"
              placeholder="••••••••"
              required
              @input="clearError"
              :class="{ 'input-error': errorMessage }"
            >
            <i 
              class="fas fa-eye toggle-password"
              :class="{ 'fa-eye-slash': showConfirmPassword }"
              @click="toggleConfirmPasswordVisibility"
            ></i>
          </div>
        </div>

        <transition name="slide-fade">
          <div v-if="errorMessage" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
            <div v-if="isLocked" class="lock-timer">
              <i class="fas fa-lock"></i>
              Account locked for 5 minutes
            </div>
          </div>
        </transition>

        <button class="medical-btn" :disabled="isLoading || isLocked">
          <i class="fas fa-sync-alt"></i>
          {{ isLoading ? 'UPDATING...' : 'UPDATE PASSWORD' }}
          <div class="hover-effect"></div>
        </button>

        <div class="medical-links">
          <router-link to="/">
            <i class="fas fa-arrow-left"></i>
            Back to Login
          </router-link>
        </div>
      </form>

      <div class="medical-security">
        <i class="fas fa-shield-alt"></i>
        <span>HIPAA Compliant • AES-256 Encryption • PBKDF2 Hashing</span>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      password: '',
      confirmPassword: '',
      honeypot: '',
      errorMessage: '',
      isLoading: false,
      showPassword: false,
      showConfirmPassword: false,
      updateAttempts: 0,
      isLocked: false,
      lockTimer: null
    }
  },
  methods: {
    clearError() {
      this.errorMessage = ''
    },
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    toggleConfirmPasswordVisibility() {
      this.showConfirmPassword = !this.showConfirmPassword
    },
    validatePassword() {
      const requirements = {
        length: this.password.length >= 12,
        uppercase: /[A-Z]/.test(this.password),
        number: /\d/.test(this.password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(this.password)
      }

      if (!Object.values(requirements).every(v => v)) {
        return 'Password must contain: 12+ characters, 1 uppercase letter, 1 number, and 1 special character';
      }
      
      if (this.password !== this.confirmPassword) {
        return 'Passwords do not match';
      }

      return null;
    },
    sanitizeInputs() {
      this.password = this.password.trim();
      this.confirmPassword = this.confirmPassword.trim();
    },
    async handleSubmit() {
      if (this.honeypot !== '') return;
      if (this.isLocked) {
        this.errorMessage = 'Account temporarily locked. Please try again later.';
        return;
      }

      this.sanitizeInputs();
      const validationError = this.validatePassword();
      if (validationError) {
        this.errorMessage = validationError;
        return;
      }

      this.isLoading = true;
      this.clearError();

      try {
        await this.$store.dispatch('medicalAuth/updatePassword', {
          newPassword: this.password,
        });
        
        this.updateAttempts = 0;
        this.$router.push('/');
      } catch (error) {
        this.updateAttempts++;
        
        if (this.updateAttempts >= 3) {
          this.isLocked = true;
          this.lockTimer = setTimeout(() => {
            this.isLocked = false;
            this.updateAttempts = 0;
          }, 300000);
          this.errorMessage = 'Too many failed attempts. Account locked for 5 minutes.';
        } else {
          this.errorMessage = 'Password update failed. Please try again.';
        }
      } finally {
        this.isLoading = false;
      }
    }
  },
  beforeUnmount() {
    clearTimeout(this.lockTimer);
  }
}
</script>