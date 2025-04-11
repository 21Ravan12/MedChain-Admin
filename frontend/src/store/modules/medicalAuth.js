import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true
})

export default {
  namespaced: true,
  state: () => ({
    user: null,
    csrfToken: null,
    redis_key: null,
    loading: false,
    error: null
  }),
  mutations: {
    SET_CSRF_TOKEN(state, token) {
      state.csrfToken = token
    },
    SET_USER(state, user) {
      state.user = user
    },
    SET_REDIS_KEY(state, key) {
      state.redis_key = key
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async getCsrfToken({ commit }) {
      try {
        const response = await api.get('api/auth/get-csrf-token', {
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        
        commit('SET_CSRF_TOKEN', response.data.token)
        return response.data.token
        
      } catch (error) {
        commit('SET_ERROR', 'CSRF token alınamadı: ' + (error.response?.data?.message || error.message))
        throw error
      }
    },

    async signup({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        let formattedPhone = credentials.phone.replace(/[^\d+]/g, '')
        if (!formattedPhone.startsWith('+')) {
          formattedPhone = `+${formattedPhone}`
        }
    
        const transformedCredentials = {
          email: credentials.email.toLowerCase().trim(),
          password: credentials.password,
          name: credentials.name.trim(),
          telephone: formattedPhone
        }
    
        const response = await api.post('api/auth/register', transformedCredentials, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': this.state.medicalAuth.csrfToken
          }
        })
    
        commit('SET_USER', response.data.user)
        localStorage.setItem('authToken', response.data.token)
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`

        commit('SET_REDIS_KEY', response.data.redis_key)
    
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''

        let errorMessage = 'Kayıt işlemi başarısız'
    
        const errorMapping = {
          'Geçersiz e-posta formatı': 'Geçerli bir e-posta adresi girin',
          'Parola gereksinimleri': 'Şifre 12+ karakter, 1 büyük harf ve rakam içermeli',
          'telefon numarası': '+90 ile başlamalı (örn: +905551234567)'
        }
    
        Object.entries(errorMapping).forEach(([key, value]) => {
          if (serverMessage.includes(key)) errorMessage = value
        })
    
        if (error.response?.status === 419) {
          await dispatch('getCsrfToken')
          return dispatch('signup', credentials)
        }
    
        commit('SET_ERROR', serverMessage)
        throw error
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async completeRegistration({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        const payload = {
          redis_key: this.state.medicalAuth.redis_key,
          code: credentials.code.toString().trim()
        }
    
        const response = await api.post(
          'api/auth/complete-registration',
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': this.state.medicalAuth.csrfToken 
            },
            withCredentials: true
          }
        )
    
        commit('SET_USER', response.data.user)
        
        commit('SET_REDIS_KEY', response.data.redis_key)
    
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        let errorMessage = 'Doğrulama işlemi başarısız'
    
        const errorMapping = {
          'Invalid CSRF token': 'Geçersiz güvenlik anahtarı', 
          'Invalid or expired code': 'Geçersiz veya süresi dolmuş kod',
          'Invalid code': 'Yanlış doğrulama kodu',
          'Missing registration ID': 'Eksik kayıt bilgisi',
          'User already exists': 'Bu kullanıcı zaten kayıtlı',
          'Invalid registration data': 'Geçersiz kayıt verisi'
        }
    
        const matchedKey = Object.keys(errorMapping).find(key => 
          serverMessage.includes(key)
        )
        errorMessage = matchedKey ? errorMapping[matchedKey] : errorMessage
    
        if (error.response?.status === 403 && serverMessage.includes('CSRF')) {
          await dispatch('getCsrfToken')
          return dispatch('completeRegistration', credentials)
        }
    
        if (error.response?.status === 400) {
          errorMessage = 'Geçersiz istek formatı'
        }
    
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async selectRole({ commit, dispatch }, { credentials, router }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
    
      try {
        await dispatch('getCsrfToken');
    
        const requestData = {
          redis_key: this.state.medicalAuth.redis_key,
          role: credentials.role,
          ...(credentials.roleDetails || {})
        };
        
        const roleDataMappings = {
          patient: (data) => ({
            birthyear: data?.birthyear,
            id_proof: data?.id_proof,
            insurance: data?.insurance,
            profile_image: data?.profile_image || null,
            medical_history: data?.medical_history || '',
            blood_type: data?.blood_type || ''
          }),
          doctor: (data) => ({
            license_number: data?.license_number,
            specialty: data?.specialty,
            hospital_id: data?.hospital_id,
            degree: data?.degree,
            license_document: data?.license_document,
            profile_image: data?.profile_image || null,
            available_hours: data?.available_hours || '',
            languages: data?.languages || []
          }),
          hospitalAdmin: (data) => ({
            hospital_id: data?.hospital_id,
            admin_id: data?.admin_id,
            department: data?.department,
            license_document: data?.license_document,
            qualifications: data?.qualifications,
            profile_image: data?.profile_image || null,
            access_level: data?.access_level || 'basic',
            employment_verification: data?.employment_verification || null
          }),
          hospital: (data) => ({
            license_number: data?.license_number,
            address: data?.address,
            established: data?.established,
            type: data?.type,
            logo: data?.logo || null,
            beds: data?.beds || 0,
            operating_hours: data?.operating_hours || '',
            emergency_services: data?.emergency_services || false,
            accreditation: data?.accreditation_document || null,
            license: data?.license_document || null,
            medical_staff: data?.medical_staff || 0,
          }),
          pharmacy: (data) => ({
            license_number: data?.license_number,
            address: data?.address,
            type: data?.type,
            established: data?.established,
            logo: data?.logo || null,
            operating_hours: data?.operating_hours || '',
            inventory_size: data?.inventory_size || 0,
            accreditation: data?.accreditation || null,
            accreditation: data?.accreditation_document || null,
            license: data?.license_document || null,
            prescriptions_filled: data?.prescriptions_filled || 0,
            pharmacists_count: data?.pharmacists_count || 0
          }),
          pharmacyAdmin: (data) => ({
            pharmacy_id: data?.pharmacy_id,
            admin_id: data?.admin_id,
            profile_image: data?.profile_image || null,
            access_level: data?.access_level || 'basic',
            pharmacist_cert: data?.pharmacist_cert || null
          }),
          pharmacist: (data) => ({
            license_number: data?.license_number,
            pharmacy_id: data?.pharmacy_id,
            profile_image: data?.profile_image || null,
            pharmacist_cert: data?.pharmacist_cert || null
          }),
          admin: (data) => ({
            security_level: data?.securityLevel,
            profile_image: data?.profileImage || null,
            audit_access: data?.auditAccess || false
          })
        };
        
        const roleData = credentials.roleDetails || credentials;
        
        if (credentials.role && roleDataMappings[credentials.role]) {
          Object.assign(requestData, roleDataMappings[credentials.role](roleData));
        }
        console.log('Request data:', requestData);  
        const headers = {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.state.medicalAuth.csrfToken
        };
        
        const response = await api.post('api/auth/select-role', requestData, { headers });
    
        router.push('/');

      } catch (error) {
        let errorMessage = 'Role selection failed';
        const serverMessage = error.response?.data?.message || error.message;
    
        const errorMapping = {
          'Missing information': 'Please fill all required fields',
          'Invalid role selection': 'Please select a valid role',
          'Invalid hospital reference': 'Selected hospital not found',
          'Session expired': 'Session expired, please start again',
          'CSRF token': 'Security token expired, refreshing...',
          'User already registered': 'Account already exists',
          'Invalid file type': 'Please upload valid document types',
          'File size exceeded': 'File size exceeds maximum limit'
        };
    
        for (const [key, value] of Object.entries(errorMapping)) {
          if (serverMessage.includes(key)) {
            errorMessage = value;
            break;
          }
        }
    
        if (error.response?.status === 419) {
          await dispatch('getCsrfToken');
          errorMessage = 'Please try again';
        }
    
        commit('SET_ERROR', errorMessage);
        throw new Error(errorMessage);
    
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async resendVerificationCode({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        const payload = {
          redis_key: this.state.medicalAuth.redis_key, 
          type: credentials.type.toString()
        }

        const response = await api.post(
          'api/auth/resend-verification-code', 
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': this.state.medicalAuth.csrfToken 
            },
            withCredentials: true 
          }
        )
    
        commit('SET_USER', response.data.user)
        localStorage.setItem('authToken', response.data.token)
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`

        commit('SET_REDIS_KEY', response.data.redis_key)
    
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        let errorMessage = 'Doğrulama işlemi başarısız'
    
        const errorMapping = {
          'Invalid or expired code': 'Geçersiz veya süresi dolmuş kod',
          'Invalid code': 'Yanlış doğrulama kodu',
          'Missing registration ID': 'Eksik kayıt bilgisi',
          'User already exists': 'Bu kullanıcı zaten kayıtlı',
          'Invalid registration data': 'Geçersiz kayıt verisi'
        }
    
        const matchedKey = Object.keys(errorMapping).find(key => 
          serverMessage.includes(key)
        )
        errorMessage = matchedKey ? errorMapping[matchedKey] : errorMessage
    
        if (error.response?.status === 403 && serverMessage.includes('CSRF')) {
          await dispatch('getCsrfToken')
        }
    
        if (error.response?.status === 400) {
          errorMessage = 'Geçersiz istek formatı'
        }
    
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async login({ commit, dispatch }, { credentials, router }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
    
      try {
        await dispatch('getCsrfToken');
        const csrfToken = this.state.medicalAuth.csrfToken;
        if (!csrfToken) throw new Error('CSRF token not available');
    
        const payload = {
          email: credentials.email.toLowerCase().trim(),
          password: credentials.password,
        };
    
        const response = await api.post('api/auth/login', payload, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
    
        if (response.status === 403 && response.data?.message === "Account inactive") {
          commit('SET_ERROR', {
            title: 'Hesap Aktif Değil',
            message: response.data.description || 'Hesabınız aktif değil veya doğrulanmamış'
          });
          return;
        }
    
        if (response.status === 202) {
          commit('SET_MFA_REQUIRED', true);
          commit('SET_PENDING_USER', {
            ...response.data,
            email: payload.email
          });
          return {
            requiresMfa: true,
            mfaKey: response.data.mfa_key,
            authLevel: response.data.auth_level
          };
        }
    
        if (response.status === 200 || response.status === 201) {
          const authToken = response.data.token;
          localStorage.setItem('authToken', authToken);
          api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
      
          commit('SET_USER', response.data.user);
      
          const roleRoutes = {
            admin: { name: 'admindashboardview' },
            hospitalAdmin: { name: 'verifyhospitaladminview' },
            doctor: { name: 'verifydoctorsview' },
            patient: { name: 'verifypatientsview' },
            pharmacy: { name: 'verifypharmaciesview' },
            hospital: { name: 'verifyhospitalsview' }
          };
      
          const route = roleRoutes[response.data.user.role] || { name: 'home' };
          await router.push(route);
      
          return response.data;
        }
    
      } catch (error) {
        let errorMessage = 'Doğrulama işlemi başarısız';
        const serverMessage = error.response?.data?.message || '';
        
        const errorMapping = {
          'Invalid credentials': 'Geçersiz e-posta veya şifre',
          'Account not verified': 'Lütfen hesabınızı doğrulayın',
          'Invalid CSRF token': 'Geçersiz güvenlik belirteci',
          'Too many attempts': 'Çok fazla deneme yaptınız. Lütfen bekleyin.',
          'MFA required': 'İki adımlı doğrulama gerekiyor',
          'MFA failed': 'Doğrulama kodu hatalı',
          '422': 'Geçersiz istek verisi',
          'Account inactive': 'Hesabınız aktif değil' // Added for inactive accounts
        };
    
        if (error.response?.status === 403) {
          if (serverMessage.includes('CSRF')) {
            await dispatch('getCsrfToken');
            return dispatch('login', { credentials, router });
          }
          // Handle inactive account error from backend
          if (serverMessage === 'Account inactive') {
            errorMessage = errorMapping['Account inactive'] + 
              (error.response.data?.description ? `: ${error.response.data.description}` : '');
          }
        }
        else if (error.response?.status === 429) {
          errorMessage = errorMapping['Too many attempts'];
        } 
        else if (error.response?.status === 422) {
          errorMessage = errorMapping['422'] + ': ' + 
            (error.response.data?.errors?.join(', ') || serverMessage);
        }
        else {
          errorMessage = errorMapping[serverMessage] || 
                       error.response?.data?.error || 
                       errorMessage;
        }
    
        commit('SET_ERROR', errorMessage);
        console.error('Login error:', error.response?.data || error.message);
        throw error;
    
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async requestPasswordReset({ commit, dispatch }, email) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        const normalizedEmail = email.toLowerCase().trim()
    
        const response = await api.post(
          'api/auth/request-password-reset',
          { email: normalizedEmail },
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': this.state.medicalAuth.csrfToken
            }
          }
        )
    
        commit('SET_REDIS_KEY', response.data.redis_key)
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        
        let errorMessage = 'Şifre sıfırlama isteği gönderilemedi'
        
        const errorMapping = {
          'user not found': 'Bu e-posta ile kayıtlı kullanıcı bulunamadı',
          'reset limit exceeded': 'Günlük maksimum deneme limitine ulaşıldı',
          'invalid email format': 'Geçersiz e-posta formatı'
        }
    
        Object.entries(errorMapping).forEach(([key, value]) => {
          if (serverMessage.toLowerCase().includes(key)) {
            errorMessage = value
          }
        })
    
        if (error.response?.status === 419) {
          await dispatch('getCsrfToken')
          return dispatch('requestPasswordReset', email)
        }
    
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async verifyCode({ commit, dispatch }, credentials) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        const payload = {
          redis_key: this.state.medicalAuth.redis_key, 
          code: credentials.code.toString().trim()
        }
    
        const response = await api.post(
          'api/auth/verify-reset-code', 
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': this.state.medicalAuth.csrfToken 
            },
            withCredentials: true 
          }
        )
    
        commit('SET_USER', response.data.user)
        
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        let errorMessage = 'Doğrulama işlemi başarısız'
    
        const errorMapping = {
          'Invalid or expired code': 'Geçersiz veya süresi dolmuş kod',
          'Invalid code': 'Yanlış doğrulama kodu',
          'Missing registration ID': 'Eksik kayıt bilgisi',
          'User already exists': 'Bu kullanıcı zaten kayıtlı',
          'Invalid registration data': 'Geçersiz kayıt verisi'
        }
    
        const matchedKey = Object.keys(errorMapping).find(key => 
          serverMessage.includes(key)
        )
        errorMessage = matchedKey ? errorMapping[matchedKey] : errorMessage
    
        if (error.response?.status === 403 && serverMessage.includes('CSRF')) {
          await dispatch('getCsrfToken')
          return dispatch('completeRegistration', credentials)
        }
    
        if (error.response?.status === 400) {
          errorMessage = 'Geçersiz istek formatı'
        }
    
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async updatePassword({ commit, dispatch, state }, { newPassword }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
    
      try {
        await dispatch('getCsrfToken')
    
        if (!newPassword || !this.state.medicalAuth.redis_key) {
          commit('SET_ERROR', 'Eksik bilgi girdiniz')
          throw new Error('Missing required fields')
        }
    
        const payload = {
          redis_key: this.state.medicalAuth.redis_key,
          new_password: newPassword.toString().trim()
        }
    
        const response = await api.post(
          'api/auth/reset-password',
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': this.state.medicalAuth.csrfToken
            },
            withCredentials: true
          }
        )
    
        commit('SET_REDIS_KEY', null)
        commit('SET_USER', response.data.user)
        
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        let errorMessage = 'Şifre güncelleme başarısız'
    
        const errorMapping = {
          'Invalid or expired session': 'Geçersiz veya süresi dolmuş oturum',
          'Security verification failed': 'Güvenlik doğrulaması başarısız',
          'Password requirements': 'Şifre 12+ karakter, 1 büyük harf ve rakam içermeli',
          'User not found': 'Kullanıcı bulunamadı',
          'expired registration session': 'Oturum süresi doldu'
        }
    
        const matchedKey = Object.keys(errorMapping).find(key => 
          serverMessage.toLowerCase().includes(key.toLowerCase())
        )
        
        if (error.response?.status === 403 && serverMessage.includes('CSRF')) {
          await dispatch('getCsrfToken')
          return dispatch('updatePassword', { password })
        }
    
        if (matchedKey) {
          errorMessage = errorMapping[matchedKey]
        } else if (error.response?.status === 400) {
          errorMessage = 'Geçersiz istek formatı'
        }
    
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchVerifiedHospitals({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await dispatch('getCsrfToken')
        const csrfToken = this.state.medicalAuth.csrfToken;
        if (!csrfToken) throw new Error('CSRF token not available');
    
        const response = await api.get('api/admin/verified-hospital', {
          headers: {
            'Accept': 'application/json',
            'X-CSRF-Token': csrfToken
          },
          withCredentials: true
        });
        console.log('verified Hospitals:', response);
        return response;
    
      } catch (error) {
        let errorMessage = 'Failed to load unverified entities';
        
        if (error.response) {
          switch (error.response.status) {
            case 403:
              errorMessage = error.response.data?.message || 'CSRF token invalid';
              dispatch('handleCsrfError');
              break;
            case 401:
              errorMessage = 'Unauthorized access';
              dispatch('logout');
              break;
            default:
              errorMessage = error.response.data?.message || errorMessage;
          }
        }
        
        commit('SET_ERROR', errorMessage);
        throw error;
    
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchVerifiedPharmacies({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await dispatch('getCsrfToken')
        const csrfToken = this.state.medicalAuth.csrfToken;
        if (!csrfToken) throw new Error('CSRF token not available');
    
        const response = await api.get('api/admin/verified-pharmacy', {
          headers: {
            'Accept': 'application/json',
            'X-CSRF-Token': csrfToken
          },
          withCredentials: true
        });
        console.log('verified Pharmacies:', response);
        return response;
    
      } catch (error) {
        let errorMessage = 'Failed to load unverified entities';
        
        if (error.response) {
          switch (error.response.status) {
            case 403:
              errorMessage = error.response.data?.message || 'CSRF token invalid';
              dispatch('handleCsrfError');
              break;
            case 401:
              errorMessage = 'Unauthorized access';
              dispatch('logout');
              break;
            default:
              errorMessage = error.response.data?.message || errorMessage;
          }
        }
        
        commit('SET_ERROR', errorMessage);
        throw error;
    
      } finally {
        commit('SET_LOADING', false);
      }
    },
  },
  getters: {
    isAuthenticated: state => !!state.user,
    currentUser: state => state.user,
    authError: state => state.error
  }
}
