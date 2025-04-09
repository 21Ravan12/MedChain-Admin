<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-key"></i>
        </div>
        <h2>MEDICARE PRO <span>v2.0</span></h2>
        <p>Password Reset System</p>
      </div>

      <form @submit.prevent="handleReset" class="medical-form">
        <input type="text" v-model="honeypot" style="display: none;">

        <div class="input-group">
          <label>Registered Email</label>
          <div class="input-field">
            <i class="fas fa-envelope"></i>
            <input
              type="email"
              v-model="email"
              @input="clearError"
              placeholder="example@medicare.com"
              required
            >
          </div>
          <transition name="slide-fade">
            <div v-if="errorMessage" class="error-message">
              <i class="fas fa-exclamation-circle"></i>
              {{ errorMessage }}
              <div v-if="isLocked" class="lock-timer">
                <i class="fas fa-lock"></i>
                Account will be unlocked in 5 minutes
              </div>
            </div>
          </transition>
        </div>

        <button class="medical-btn" :disabled="isLoading || isLocked">
          <i class="fas fa-paper-plane"></i>
          {{ isLoading ? 'SENDING...' : 'SEND RESET CODE' }}
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
        <span>HIPAA Compliant • AES-256 Encryption</span>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      email: '',
      isLoading: false,
      errorMessage: '',
      honeypot: '',
      loginAttempts: 0,
      isLocked: false,
      lockTimer: null
    }
  },
  methods: {
    validateForm() {
      if (!this.email) {
        return 'Please fill all required fields';
      }
      const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
      if (!emailRegex.test(this.email)) {
        return 'Invalid email format';
      }
      return null;
    },
    clearError() {
      this.errorMessage = '';
    },
    async handleReset() {
      if (this.honeypot !== '') return;

      const validationError = this.validateForm();
      if (validationError) {
        this.errorMessage = validationError;
        return;
      }

      if (this.isLocked) {
        this.errorMessage = 'Account temporarily locked. Please try again later.';
        return;
      }

      this.isLoading = true;
      this.clearError();

      try {
        await this.$store.dispatch('medicalAuth/requestPasswordReset', this.email);
        this.loginAttempts = 0;
        this.$router.push('/verifycode');
      } catch (error) {
        this.loginAttempts++;
        
        if (this.loginAttempts >= 3) {
          this.isLocked = true;
          this.lockTimer = setTimeout(() => {
            this.isLocked = false;
            this.loginAttempts = 0;
          }, 300000);
          this.errorMessage = 'Too many attempts. Account locked for 5 minutes.';
        } else {
          this.errorMessage = 'Non-existent email';
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