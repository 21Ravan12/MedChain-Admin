import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    withCredentials: true
})

export default {
  namespaced: true,
  state: () => ({
    user: null,  
    loading: false,
    error: null
  }),
  mutations: {
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_USER(state, user) {  
      state.user = user
    }
  },
  actions: {
    async fetchProfile({ commit, dispatch, rootState }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
    
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/profile', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json', 
            'Content-Type': 'application/json' 
          },
          withCredentials: true 
        });
        commit('SET_USER', response.data.admin_profile);
        return response;
    
      } catch (error) {
        let errorMessage = 'Failed to load profile';
    
        if (error.response) {
          switch (error.response.status) {
            case 403:
              errorMessage = error.response.data?.message || 'CSRF token invalid';
              break;
            case 415:
              errorMessage = 'Invalid Content-Type header';
              break;
            case 422:
              errorMessage = error.response.data?.message || 'Validation failed';
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

    async fetchDashboardStats({ commit, dispatch, rootState }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
    
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/dashboard-stats', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json', 
            'Content-Type': 'application/json' 
          },
          withCredentials: true 
        });
    
        console.log('Dashboard Stats:', response.data);
        return response;
    
      } catch (error) {
        let errorMessage = 'Failed to load dashboard statistics';
    
        if (error.response) {
          switch (error.response.status) {
            case 403:
              errorMessage = error.response.data?.message || 'Not authorized to access dashboard stats';
              break;
            case 415:
              errorMessage = 'Invalid Content-Type header';
              break;
            case 500:
              errorMessage = 'Server error while retrieving dashboard stats';
              break;
            default:
              errorMessage = error.response.data?.message || errorMessage;
          }
        } else if (error.message === 'No auth token found') {
          errorMessage = 'Authentication required';
        }
    
        commit('SET_ERROR', errorMessage);
        throw error;
    
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchRecentActivities({ commit, dispatch, rootState }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
    
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/profile', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json', 
            'Content-Type': 'application/json' 
          },
          withCredentials: true 
        });
        commit('SET_USER', response.data.admin_profile);
        return response;
    
      } catch (error) {
        let errorMessage = 'Failed to load profile';
    
        if (error.response) {
          switch (error.response.status) {
            case 403:
              errorMessage = error.response.data?.message || 'CSRF token invalid';
              break;
            case 415:
              errorMessage = 'Invalid Content-Type header';
              break;
            case 422:
              errorMessage = error.response.data?.message || 'Validation failed';
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

    async fetchUnverifiedHospitals({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-hospital', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Hospitals:', response.data);
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

    async fetchUnverifiedPharmacies({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-pharmacy', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Pharmacies:', response.data);
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

    async fetchUnverifiedDoctors({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-doctor', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Doctors:', response.data);
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

    async fetchUnverifiedHospitalAdmins({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-hospital-admin', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Hospital Admins:', response.data);
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

    async fetchUnverifiedPharmacyAdmins({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-pharmacy-admins', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Pharmacy Admin:', response.data);
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

    async fetchUnverifiedPharmacists({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-pharmacist', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Pharmacist:', response.data);
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

    async fetchUnverifiedPatients({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-patient', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Patients:', response.data);
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

    async fetchUnverifiedAdmins({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-admins', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Unverified Admins:', response.data);
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

    async approve({ commit, dispatch }, payload) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      try {
        const authToken = localStorage.getItem('authToken')
        if (!authToken) throw new Error('No auth token found')  
    
        const response = await api.post(
          'api/admin/approve',
          { 
            entity_type: payload.entityType,  
            entity_id: payload.entityId,
            status: payload.status || 'approved', 
            description: payload.description || '' 
          },
          {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json' 
            }
          }
        )
    
        return response
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        
        let errorMessage = 'Onaylama işlemi başarısız oldu'
        
        const errorMapping = {
          'invalid entity type': 'Geçersiz varlık türü',
          'entity not found': 'Kayıt bulunamadı',
          'admin not found': 'Yetkisiz işlem',
          'missing required fields': 'Eksik bilgi gönderildi'
        }
    
        Object.entries(errorMapping).forEach(([key, value]) => {
          if (serverMessage.toLowerCase().includes(key)) {
            errorMessage = value
          }
        })
    
        if (error.response?.status === 419) {
          await dispatch('getCsrfToken')
          return dispatch('approve', payload)
        }
    
        commit('SET_ERROR', errorMessage)
        throw error
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async reject({ commit, dispatch }, payload) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      try {
        if (!payload || typeof payload !== 'object') {
          throw new Error('Geçersiz istek verisi')
        }
        
        const { entityType, entityId, description = '' } = payload
        if (!entityType || !entityId) {
          throw new Error('Eksik bilgi gönderildi')
        }
    
        const authToken = localStorage.getItem('authToken')
        if (!authToken) {
          await dispatch('logout')
          throw new Error('Oturum sona erdi. Lütfen tekrar giriş yapın')
        }  
        
        const response = await api.post(
          'api/admin/reject',
          { 
            entity_type: entityType,  
            entity_id: entityId,
            status: 'rejected', // Always set to rejected for this endpoint
            description: description
          },
          {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json' 
            }
          }
        )
        
        return response.data
    
      } catch (error) {
        const serverMessage = error.response?.data?.message || ''
        
        let errorMessage = 'Reddetme işlemi başarısız oldu'
        
        const errorMapping = {
          'invalid entity type': 'Geçersiz varlık türü',
          'entity not found': 'Kayıt bulunamadı',
          'admin not found': 'Yetkisiz işlem',
          'missing required fields': 'Eksik bilgi gönderildi',
          'content-type must be application/json': 'Geçersiz istek formatı',
          'no data provided': 'Eksik bilgi gönderildi'
        }
        
        Object.entries(errorMapping).forEach(([key, value]) => {
          if (serverMessage.toLowerCase().includes(key)) {
            errorMessage = value
          }
        })
        
        if (error.response?.status === 419) {
          await dispatch('getCsrfToken')
          return dispatch('reject', payload)
        }
        
        if (error.response?.status === 401) {
          await dispatch('logout')
          errorMessage = 'Oturum sona erdi. Lütfen tekrar giriş yapın'
        }
        
        commit('SET_ERROR', errorMessage)
        throw error
    
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchUsers({ commit, dispatch }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) throw new Error('No auth token found');
    
        const response = await api.get('api/admin/unverified-doctor', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        console.log('Data:', response.data);
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