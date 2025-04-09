<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-hospital-user"></i>
        </div>
        <h2>MEDICARE PRO <span class="header-accent">v2.0</span></h2>
        <p>Account Registration</p>
      </div>

      <form @submit.prevent="handleSignup" class="medical-form">
        <input type="text" v-model="honeypot" style="display: none;">

        <transition name="slide-fade">
          <div v-if="errorMessage" class="medical-error-alert">
            <i class="fas fa-exclamation-triangle"></i>
            {{ errorMessage }}
            <div v-if="isLocked" class="lock-timer">
              <i class="fas fa-lock"></i>
              Account creation locked for 15 minutes
            </div>
          </div>
        </transition>

        <!-- Input Groups -->
        <div class="input-group">
          <label>Full Name</label>
          <div class="input-field">
            <i class="fas fa-user-md"></i>
            <input 
              type="text" 
              v-model="formData.fullName"
              @input="clearError"
              placeholder="Dr. John Doe or Health Hospital"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label>Email</label>
          <div class="input-field">
            <i class="fas fa-envelope"></i>
            <input 
              type="email" 
              v-model="formData.email"
              @input="clearError"
              placeholder="example@institution.com"
              required
            >
          </div>
        </div>

        <div class="input-group">
          <label>Phone</label>
          <div class="input-field">
            <i class="fas fa-mobile-alt"></i>
            <input 
              type="tel" 
              v-model="formData.phone"
              @input="clearError"
              placeholder="(5__) ___ __ __"
              required
            >
          </div>
        </div>

        <div class="input-row">
          <div class="input-group">
            <label>Password</label>
            <div class="input-field">
              <i class="fas fa-lock"></i>
              <input
                type="password"
                v-model="formData.password"
                @input="clearError"
                placeholder="••••••••"
                required
              >
            </div>
          </div>

          <div class="input-group">
            <label>Confirm</label>
            <div class="input-field">
              <i class="fas fa-lock"></i>
              <input
                type="password"
                v-model="formData.passwordConfirm"
                @input="clearError"
                placeholder="••••••••"
                required
              >
            </div>
          </div>
        </div>

        <!-- Terms Checkbox -->
        <div class="terms-section">
          <label class="checkbox-container">
            <input type="checkbox" v-model="formData.agreeTerms">
            <span class="checkmark"></span>
            <span class="terms-text">
              I accept the <router-link to="/terms">terms of use</router-link>
            </span>
          </label>
        </div>

        <!-- Submit Button -->
        <button class="medical-btn" :disabled="isLoading || isLocked">
          <i class="fas fa-file-signature"></i>
          {{ isLoading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT' }}
          <div class="hover-effect"></div>
        </button>

        <!-- Bottom Links -->
        <div class="medical-links">
          <router-link to="/">
            <i class="fas fa-sign-in-alt"></i> Login
          </router-link>
        </div>
      </form>

      <!-- Security Footer -->
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
      formData: {
        fullName: '',
        email: '',
        phone: '',
        password: '',
        passwordConfirm: '',
        agreeTerms: false
      },
      honeypot: '',
      errorMessage: '',
      isLoading: false,
      signupAttempts: 0,
      isLocked: false,
      lockTimer: null
    }
  },
  methods: {
    clearError() {
      this.errorMessage = ''
    },
    sanitizeInputs() {
      // XSS prevention
      this.formData.fullName = this.formData.fullName
        .trim()
        .replace(/[<>"'&]/g, '')
      this.formData.email = this.formData.email.trim().toLowerCase()
      this.formData.password = this.formData.password
        .trim()
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
      this.formData.passwordConfirm = this.formData.passwordConfirm
        .trim()
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
      this.formData.phone = (this.formData.phone || '').replace(/\D/g, '')

    },
    validateForm() {

      const validations = [
        { 
          condition: !/^[a-zA-Z\u00C0-\u017F\s.]{2,50}$/.test(this.formData.fullName),
          message: 'Invalid name format (2-50 letters)'
        },
        {
          condition: !/^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,}$/.test(this.formData.email),
          message: 'Invalid institutional email format'
        },
        {
          condition: this.formData.password.length < 12 ||
                     !/[A-Z]/.test(this.formData.password) ||
                     !/[0-9]/.test(this.formData.password) ||
                     !/[!@#$%^&*]/.test(this.formData.password),
          message: 'Password must contain 12+ chars, 1 uppercase, 1 number, 1 special'
        },
        {
          condition: this.formData.password !== this.formData.passwordConfirm,
          message: 'Passwords do not match'
        },
        {
          condition: !/^\d{10,15}$/.test(this.formData.phone),
          message: 'Invalid phone format (10-15 digits)'
        },
        {
          condition: !this.formData.agreeTerms,
          message: 'You must accept terms & conditions'
        }
      ]

      return validations.find(v => v.condition)
    },
    async handleSignup() {
      if (this.honeypot !== '') return
      if (this.isLocked) {
        this.errorMessage = 'Account creation temporarily locked. Please try again later.'
        return
      }

      this.sanitizeInputs()
      const validationError = this.validateForm()
      
      if (validationError) {
        this.errorMessage = validationError.message
        return
      }

      this.isLoading = true
      this.clearError()

      try {
        const payload = {
          name: this.formData.fullName,
          email: this.formData.email,
          password: this.formData.password,
          phone: this.formData.phone
        }
        
        await this.$store.dispatch('medicalAuth/signup', payload)
        this.signupAttempts = 0
        this.$router.push('/signupverifycode')

      } catch (error) {
        this.signupAttempts++
        
        if (this.signupAttempts >= 3) {
          this.isLocked = true
          this.lockTimer = setTimeout(() => {
            this.isLocked = false
            this.signupAttempts = 0
          }, 900000) 
          this.errorMessage = 'Too many failed attempts. Account creation locked for 15 minutes.'
        } else {
          this.errorMessage = 'Registration failed. Please check your details and try again.'
        }
        
        console.error('Signup Error:', error.response?.data || error.message)
      } finally {
        this.isLoading = false
      }
    }
  },
  beforeUnmount() {
    clearTimeout(this.lockTimer)
  }
}
</script>

