<template>
  <div class="medical-container">
    <div class="medical-card">
      <div class="medical-header">
        <div class="icon-container">
          <i class="fas fa-user-tag"></i>
        </div>
        <h2>MEDICARE PRO <span class="header-accent">v2.0</span></h2>
        <p>Select Your Role</p>
      </div>

      <div class="medical-form">
        <!-- Honeypot field moved outside of form -->
        <input type="text" v-model="honeypot" style="display: none;">

        <transition name="slide-fade">
          <div v-if="errorMessage" class="medical-error-alert">
            <i class="fas fa-exclamation-triangle"></i>
            {{ errorMessage }}
          </div>
        </transition>

        <!-- Role Selection -->
        <div class="role-grid">
          <RoleCard 
            v-for="role in roles" 
            :key="role.value"
            :role="role"
            :selected="formData.role === role.value"
            @click="selectRole(role.value)"
          />
        </div>

        <!-- Dynamic Role Fields -->
        <template v-if="formData.role">
          <HospitalForm 
            v-if="formData.role === 'hospital'" 
            v-model="formData.hospital"
            @update:logo="handleLogoUpload"
            @update:license="handleLicenseUpload"
            @update:accreditation="handleAccreditationUpload"
          />

          <AdminForm
            v-if="formData.role === 'admin'"
            v-model="formData.admin"
            @error="handleError"
          />
          
          <PatientForm 
            v-if="formData.role === 'patient'" 
            v-model="formData.patient"
          />

          <DoctorForm 
            v-if="formData.role === 'doctor'" 
            v-model="formData.doctor"
            :hospitals="hospitals"
          />

          <HospitalAdminForm 
            v-if="formData.role === 'hospitalAdmin'" 
            v-model="formData.hospitalAdmin"
            :hospitals="hospitals"
          />

          <PharmacyForm 
            v-if="formData.role === 'pharmacy'" 
            v-model="formData.pharmacy"
          />

          <PharmacistForm
            v-if="formData.role === 'pharmacist'" 
            v-model="formData.pharmacist"
            :pharmacies="pharmacies"
          />
          
          <PharmacyAdminForm
            v-if="formData.role === 'pharmacyAdmin'"
            v-model="formData.pharmacyAdmin"
            :pharmacies="pharmacies"
          />

        </template>

        <!-- Submit Button - now using @click instead of form submit -->
        <button 
          class="medical-btn" 
          :disabled="isLoading"
          @click="handleRegistration"
        >
          <i class="fas fa-check-circle"></i>
          {{ isLoading ? 'PROCESSING...' : 'COMPLETE REGISTRATION' }}
          <div class="hover-effect"></div>
        </button>

        <div class="medical-links">   
          <router-link to="/signup" class="security-link">
            <i class="fas fa-user-plus"></i> Sign Up
          </router-link>       
        </div>
      </div>

      <!-- Security Footer -->
      <div class="medical-security">
        <i class="fas fa-shield-alt"></i>
        <span>HIPAA Compliant • AES-256 Encryption • Role-Based Access Control</span>
      </div>
    </div>
  </div>
</template>

<script>
import RoleCard from './RoleCard.vue';
import HospitalForm from './HospitalForm.vue';
import PatientForm from './PatientForm.vue';
import DoctorForm from './DoctorForm.vue';
import HospitalAdminForm from './HospitalAdminForm.vue';
import PharmacyForm from './PharmacyForm.vue';
import AdminForm from './AdminForm.vue';
import PharmacistForm from './PharmacistForm.vue';
import PharmacyAdminForm from './PharmacyAdminForm.vue';

export default {
  components: {
    RoleCard,
    HospitalForm,
    PatientForm,
    DoctorForm,
    HospitalAdminForm,
    AdminForm,
    PharmacyForm,
    PharmacistForm,
    PharmacyAdminForm
  },
  data() {
    return {
      roles: [
        { value: 'hospital', label: 'Hospital', icon: 'fas fa-hospital' },
        { value: 'hospitalAdmin', label: 'Hospital Admin', icon: 'fas fa-user-shield' },
        { value: 'admin', label: 'Admin', icon: 'fas fa-shield-alt' },
        { value: 'doctor', label: 'Doctor', icon: 'fas fa-user-md' },
        { value: 'pharmacy', label: 'Pharmacy', icon: 'fas fa-prescription-bottle' },
        { value: 'pharmacyAdmin', label: 'Pharmacies Admins', icon: 'fas fa-user-cog' },
        { value: 'pharmacist', label: 'Pharmacist', icon: 'fas fa-user-nurse' },
        { value: 'patient', label: 'Patient', icon: 'fas fa-user-injured' },
      ],
      hospitals: [],
      pharmacies: [],
      formData: {
        role: '',
        patient: {
          birthyear: null,         
          id_proof: '',            
          insurance: '',           
          medical_history: '',     
          blood_type: '',          
          profile_image: null      
        },
        doctor: {
          license_number: '',       
          specialty: '',           
          hospital_id: '',         
          degree: '',              
          available_hours: '',     
          languages: '',           
          profile_image: null      
        },
        hospitalAdmin: {
          hospital_id: '',        
          admin_id: '',           
          department: '',          
          qualifications: [],      
          access_level: '',        
          employment_verification: false,  
          profile_image: null ,     
          hospital_name: ''        
        },
        admin: {
          profileImage: null,
          securityLevel: 'standard',
        },
        pharmacy: {
          license_number: '',      
          address: '',             
          established: null,       
          type: '',
          logo: null,             
          operating_hours: '',     
          inventory_size: null,    
          accreditation: '',       
          prescriptions_filled: null,
          pharmacists_count: null  
        },
        hospital: {
          logo: null,
          type: '',
          beds: null,
          established: '',
          address: '',
          license_number: '',
          license_document: null,
          accreditation_document: null,
          operating_hours: '',
          emergency_services: true,
          medical_staff: null
        },
        pharmacist: {
          pharmacy_id: '',        
          access_level: 'standard',         
          pharmacist_cert: null,     
          profile_image: null       
        },
        pharmacyAdmin: {
          pharmacy_id: '',         
          admin_id: '',        
          access_level: 'standard',         
          pharmacist_cert: null,     
          profile_image: null        
        }
      },
      honeypot: '',
      errorMessage: '',
      isLoading: false,
      signupAttempts: 0,
      isLocked: false,
      lockTimer: null,
      logoFileName: '',
      licenseFileName: '',
      accreditationFileName: '',
    }
  },
  async mounted() {
    await this.fetchHospitals();
    await this.fetchPharmacies();
  },
  methods: {
    clearError() {
      this.errorMessage = '';
    },
    
    sanitizeInput(input) {
      if (typeof input === 'string') {
        let sanitized = input.trim();
        sanitized = sanitized.replace(/[<>"'&\\/]/g, '');
        const div = document.createElement('div');
        div.textContent = sanitized;
        return div.innerHTML;
      }
      return input;
    },
    
    validateLicenseNumber(licenseNumber) {
      return /^[A-Za-z0-9-]{6,20}$/.test(licenseNumber);
    },
    
    validateYear(year) {
      if (!year) return false;
      if (typeof year === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(year)) {
        year = parseInt(year.split('-')[0], 10);
      }
      if (isNaN(year)) return false;
      const currentYear = new Date().getFullYear();
      return year >= 1800 && year <= currentYear;
    },
    
    validateBeds(beds) {
      return Number.isInteger(beds) && beds > 0;
    },
    
    validateForm() {
  if (!this.formData.role) {
    return 'Please select a role';
  }

  if (this.honeypot !== '') {
    return 'Invalid form submission';
  }

  const roleData = this.formData[this.formData.role];
  const validations = {
    patient: () => {
      if (!this.formData.patient.blood_type) return 'Blood type is required';
      if (!this.formData.patient.medical_history) return 'Medical history is required';
      if (this.formData.patient.medical_history.length < 10) return 'Medical history must be at least 10 characters';
      if (!this.formData.patient.insurance) return 'Insurance is required';
      if (!this.formData.patient.birthyear) return 'Birth year is required';
      if (!this.formData.patient.id_proof) return 'ID proof is required';
      return null;
    },
    doctor: () => {
      if (!this.formData.doctor.license_number) return 'License number is required';
      if (!this.validateLicenseNumber(this.formData.doctor.license_number)) return 'Invalid license number format';
      if (!this.formData.doctor.specialty) return 'Specialty is required';
      if (!this.formData.doctor.hospital_id) return 'Hospital selection is required';
      if (!this.formData.doctor.degree) return 'Degree is required';
      if (!this.formData.doctor.available_hours) return 'Available hours are required';
      if (!this.formData.doctor.languages) return 'Languages are required';
      return null;
    },
    hospitalAdmin: () => {
      if (!this.formData.hospitalAdmin.hospital_id) return 'Hospital selection is required';
      if (!this.formData.hospitalAdmin.department) return 'Department is required';
      if (!this.formData.hospitalAdmin.admin_id) return 'Admin ID is required';
      if (!this.formData.hospitalAdmin.access_level) return 'Access level is required';
      if (!this.formData.hospitalAdmin.hospital_name) return 'Hospital name is required';
      return null;
    },
    admin: () => {
      if (!this.formData.admin.profileImage) return 'Profile Image is required';
      if (!this.formData.admin.securityLevel) return 'Security level is required';
      return null;
    },
    pharmacy: () => {
      if (!this.formData.pharmacy.license_number) return 'Pharmacy license is required';
      if (!this.validateLicenseNumber(this.formData.pharmacy.license_number)) return 'Invalid license number format';
      if (!this.formData.pharmacy.address) return 'Address is required';
      if (!this.formData.pharmacy.established) return 'Establishment year is required';
      if (!this.formData.pharmacy.operating_hours) return 'Operating hours are required';
      return null;
    },
    hospital: () => {
      if (!this.formData.hospital.license_number) return 'License number is required';
      if (!this.validateLicenseNumber(this.formData.hospital.license_number)) return 'Invalid license number format';
      if (this.formData.hospital.beds && !this.validateBeds(this.formData.hospital.beds)) return 'Invalid number of beds';
      if (this.formData.hospital.established && !this.validateYear(this.formData.hospital.established)) {
        return 'Invalid establishment year';
      }
      if (!this.formData.hospital.type) return 'Hospital type is required';
      if (!this.formData.hospital.address) return 'Address is required';
      if (!this.formData.hospital.operating_hours) return 'Operating hours are required';
      return null;
    },
    pharmacist: () => {
      if (!this.formData.pharmacist.license_number) return 'License number is required';
      if (!this.formData.pharmacist.pharmacy_id) return 'Pharmacy ID is required';
      return null;
    },
    pharmacyAdmin: () => {
      if (!this.formData.pharmacyAdmin.admin_id) return 'Admin ID is required';
      if (!this.formData.pharmacyAdmin.access_level) return 'Access level is required';
      return null;
    }
  };

  return validations[this.formData.role]?.() || null;
},
    
    selectRole(role) {
      this.formData.role = role;
      this.clearError();
    },
    
    async fetchHospitals() {
  try {
    this.isLoading = true;
    
    const response = await this.$store.dispatch('medicalAuth/fetchVerifiedHospitals');

    this.hospitals = response.data.data;
    
  } catch (error) {
    console.error('Error fetching hospitals:', error);
    this.errorMessage = 'Failed to load hospitals. Please try again later.';
  } finally {
    this.isLoading = false;
  }
},
    
async fetchPharmacies() {
  try {
    this.isLoading = true;
    
    const response = await this.$store.dispatch('medicalAuth/fetchVerifiedPharmacies');

    this.pharmacies = response.data.data;
    
  } catch (error) {
    console.error('Error fetching pharmacies:', error);
    this.errorMessage = 'Failed to load pharmacies. Please try again later.';
  } finally {
    this.isLoading = false;
  }
},

    async handleRegistration() {
      if (this.honeypot !== '' || this.isLocked) {
        this.errorMessage = this.isLocked 
          ? 'Account creation temporarily locked. Please try again later.'
          : 'Invalid form submission';
        return;
      }

      const validationError = this.validateForm();
      if (validationError) {
        this.errorMessage = validationError;
        return;
      }

      this.isLoading = true;
      this.clearError();

      try {
        const payload = JSON.parse(JSON.stringify({
          role: this.formData.role,
          ...this.formData[this.formData.role],
          timestamp: new Date().toISOString()
        }));

        console.log('Registration Payload:', payload);
        
        this.$store.dispatch('medicalAuth/selectRole', {
          credentials: payload,
          router: this.$router
        });
        
        this.signupAttempts = 0;    
      } catch (error) {
        this.signupAttempts++;
        if (this.signupAttempts >= 3) {
          this.isLocked = true;
          this.lockTimer = setTimeout(() => {
            this.isLocked = false;
            this.signupAttempts = 0;
          }, 900000); 
          this.errorMessage = 'Too many failed attempts. Account creation locked for 15 minutes.';
        } else {
          this.errorMessage = error.response?.data?.message || 
                            'Registration failed. Please check your details and try again.';
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    handleProfileImageUpload(file) {
      this.logoFileName = file.name;
      this.formData[formData.role].profileImage = file;
    },

    handleLogoUpload(file) {
      this.logoFileName = file.name;
      this.formData.hospital.logo = file;
    },
    
    handleLicenseUpload(file) {
      this.licenseFileName = file.name;
      this.formData.hospital.license_document = file;
    },
    
    handleAccreditationUpload(file) {
      this.accreditationFileName = file.name;
      this.formData.hospital.accreditation_document = file;
    }
  },
  beforeUnmount() {
    clearTimeout(this.lockTimer);
  }
}
</script>