<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-hospital-user"></i>
        </div>
        <h2>MEDICARE PRO <span>v2.0</span></h2>
        <p>Medical Management System</p>
      </div>

      <form @submit.prevent="handleLogin" class="medical-form">
        <input type="text" v-model="honeypot" style="display: none;">

        <div class="input-group">
          <label>Email Address</label>
          <div class="input-field">
            <i class="fas fa-envelope"></i>
            <input 
              type="email" 
              v-model="credentials.email" 
              @input="clearError"
              placeholder="example@medicare.com"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label>Password</label>
          <div class="input-field">
            <i class="fas fa-lock"></i>
            <input 
              type="password" 
              v-model="credentials.password" 
              @input="clearError"
              placeholder="••••••••"
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
          <i class="fas fa-sign-in-alt"></i>
          {{ isLoading ? 'AUTHENTICATING...' : 'SYSTEM LOGIN' }}
          <div class="hover-effect"></div>
        </button>

        <div class="medical-links">
          <router-link to="/resetpassword" class="security-link">
            <i class="fas fa-redo-alt"></i> Reset Password
          </router-link>      
          <router-link to="/signup" class="security-link">
            <i class="fas fa-user-plus"></i> Sign Up
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
      credentials: {
        email: '',
        password: ''
      },
      honeypot: '',
      isLoading: false,
      errorMessage: '',
      loginAttempts: 0,
      isLocked: false,
      lockTimer: null
    }
  },
  methods: {
    sanitizeInputs() {
      this.credentials.email = this.credentials.email.trim().toLowerCase()
      this.credentials.password = this.credentials.password
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .trim()
    },
    validateForm() {
      const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
      if (!emailRegex.test(this.credentials.email)) {
        return 'Invalid email format';
      }
      return null;
    },
    clearError() {
      this.errorMessage = '';
    },
    async handleLogin() {
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

      this.sanitizeInputs();
      this.isLoading = true;

      try {
        await this.$store.dispatch('medicalAuth/login', {
          credentials: this.credentials,
          router: this.$router
        });

        this.loginAttempts = 0;
      } catch (error) {
        this.loginAttempts++;
        
        if (this.loginAttempts >= 3) {
          this.isLocked = true;
          this.lockTimer = setTimeout(() => {
            this.isLocked = false;
            this.loginAttempts = 0;
          }, 300000);
          this.errorMessage = 'Too many failed attempts. Account locked for 5 minutes.';
        } else {
          this.errorMessage = error.response?.data?.message || 'Login failed. Please try again.';
        }
        
        console.error('Login error:', error.response?.data || error.message);
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