<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-shield-alt"></i>
        </div>
        <h2>MEDICARE PRO <span>v2.0</span></h2>
        <p>Two-Factor Verification</p>
      </div>

      <form @submit.prevent="handleVerify" class="medical-form">
        <input type="text" v-model="honeypot" style="display: none;">

        <div class="input-group">
          <label>Verification Code</label>
          <div class="input-field">
            <i class="fas fa-key"></i>
            <input
              type="text"
              v-model="verificationCode"
              placeholder="Enter code"
              required
              @input="clearError"
              :class="{ 'input-error': errorMessage }"
            >
          </div>
          <transition name="slide-fade">
            <div v-if="errorMessage" class="error-message">
              <i class="fas fa-exclamation-circle"></i>
              {{ errorMessage }}
              <div v-if="isLocked" class="lock-timer">
                <i class="fas fa-lock"></i>
                Verification locked for 5 minutes
              </div>
            </div>
          </transition>
        </div>

        <button class="medical-btn" :disabled="isLoading || isLocked">
          <i class="fas fa-check-circle"></i>
          {{ isLoading ? 'VERIFYING...' : 'VERIFY CODE' }}
          <div class="hover-effect"></div>
        </button>

        <div class="medical-links">
          <p class="resend-text">
            Didn't receive code? 
            <a href="#" @click.prevent="resendCode" :disabled="!resendEnabled">
              Resend Code
              <span v-if="countdown > 0">({{ countdown }}s)</span>
            </a>
          </p>
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
      verificationCode: '',
      honeypot: '',
      isLoading: false,
      errorMessage: '',
      countdown: 30,
      resendEnabled: false,
      verificationAttempts: 0,
      isLocked: false,
      lockTimer: null,
      resendAttempts: 0
    }
  },
  methods: {
    clearError() {
      this.errorMessage = ''
    },
    startCountdown() {
      this.countdown = 30
      const timer = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--
        } else {
          clearInterval(timer)
          this.resendEnabled = true
        }
      }, 1000)
    },
    async resendCode() {
      if (!this.resendEnabled || this.resendAttempts >= 3) return
      
      try {
        this.resendEnabled = false
        this.resendAttempts++
        
        await this.$store.dispatch('medicalAuth/resendVerificationCode', {
          type: 'register'
        })
        
        this.startCountdown()
        this.errorMessage = 'New verification code sent successfully'
      } catch (error) {
        this.errorMessage = 'Failed to resend code. Please try again later.'
      }
    },
    async handleVerify() {
      if (this.honeypot !== '') return
            
      if (this.isLocked) {
        this.errorMessage = 'Verification temporarily locked. Please try again later.'
        return
      }

      this.isLoading = true
      this.clearError()

      try {
        await this.$store.dispatch('medicalAuth/completeRegistration', {
          code: this.verificationCode
        })
        
        this.verificationAttempts = 0
        this.$router.push('/selectroleview')
      } catch (error) {
        this.verificationAttempts++
        
        if (this.verificationAttempts >= 3) {
          this.isLocked = true
          this.lockTimer = setTimeout(() => {
            this.isLocked = false
            this.verificationAttempts = 0
          }, 300000)
          this.errorMessage = 'Too many failed attempts. Verification locked for 5 minutes.'
        } else {
          this.errorMessage = 'Verification failed. Please check your code and try again.'
        }
      } finally {
        this.isLoading = false
      }
    }
  },
  mounted() {
    this.startCountdown()
  },
  beforeUnmount() {
    clearTimeout(this.lockTimer)
  }
}
</script>
