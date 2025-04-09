<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="verify-hospitals">
          <!-- Page Header with Search and Filter -->
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-hospital header-icon"></i>
              <h1>Hospital Verification</h1>
              <span class="badge">{{ pendingCount }}</span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search hospitals..."
                  @input="handleSearch"
                >
                <button v-if="searchQuery" class="clear-search" @click="clearSearch">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <select v-model="filterStatus" class="status-filter" @change="fetchHospitals">
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
              <button class="btn btn-refresh" @click="refreshData">
                <i class="fas fa-sync-alt"></i>
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
            <p>Loading hospitals...</p>
          </div>

          <!-- Error State -->
          <div v-if="error" class="error-alert">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
            <button @click="fetchHospitals" class="btn-retry">
              <i class="fas fa-redo"></i> Retry
            </button>
          </div>
          
          <!-- Hospital List -->
          <div class="verification-list">
            <div 
              v-for="hospital in filteredHospitals" 
              :key="hospital.id" 
              class="verification-card"
              :class="hospital.status"
              @click="viewDetails(hospital)"
            >
              <div class="hospital-info">
                <div class="avatar">
                  <img 
                    :src="hospital.avatar || defaultHospital" 
                    alt="Hospital Logo"
                    @error="handleImageError"
                    class="hospital-logo"
                  >
                  <div class="status-indicator" :class="hospital.status"></div>
                </div>
                <div class="details">
                  <div class="name-type">
                    <h3>{{ hospital.name }}</h3>
                    <p class="type">
                      <i class="fas fa-building"></i>
                      {{ hospital.type || 'General Hospital' }} • {{ hospital.beds || 'N/A' }} beds
                    </p>
                  </div>
                  <div class="hospital-meta">
                    <div class="contact-info">
                      <p><i class="fas fa-envelope"></i> {{ hospital.email }}</p>
                      <p><i class="fas fa-phone"></i> {{ hospital.phone || 'Not provided' }}</p>
                      <p><i class="fas fa-map-marker-alt"></i> {{ hospital.address }}</p>
                    </div>
                    <div class="submission-info">
                      <div class="submission-date">
                        <i class="fas fa-calendar-alt"></i>
                        Submitted: {{ formatDate(hospital.submission_date) }}
                      </div>
                      <div v-if="hospital.reviewed_date" class="review-date">
                        <i class="fas fa-check-circle"></i>
                        Reviewed: {{ formatDate(hospital.reviewed_date) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="verification-actions" @click.stop>
                <button 
                  v-if="hospital.status === 'pending'" 
                  @click.stop="approveHospital(hospital.id)" 
                  class="btn btn-success"
                  :disabled="processingApproval === hospital.id"
                >
                  <i class="fas fa-check"></i> 
                  <span>{{ processingApproval === hospital.id ? 'Processing...' : 'Approve' }}</span>
                </button>
                <button 
                  v-if="hospital.status === 'pending'" 
                  @click.stop="showRejectModal(hospital.id)" 
                  class="btn btn-danger"
                  :disabled="processingRejection === hospital.id"
                >
                  <i class="fas fa-times"></i> 
                  <span>Reject</span>
                </button>
                <button 
                  @click.stop="viewDetails(hospital)" 
                  class="btn btn-info"
                >
                  <i class="fas fa-eye"></i> 
                  <span>Details</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!loading && filteredHospitals.length === 0" class="empty-state">
            <i class="fas fa-hospital"></i>
            <h3>No hospitals found</h3>
            <p>Try adjusting your search or filter criteria</p>
            <button class="btn btn-primary" @click="resetFilters">
              <i class="fas fa-filter"></i> Reset Filters
            </button>
          </div>
          
          <!-- Reject Modal -->
          <RejectModal 
            v-if="showRejectReasonModal" 
            @submit="rejectHospital" 
            @cancel="showRejectReasonModal = false" 
          />
          
          <!-- Hospital Detail Modal -->
          <HospitalDetailModal 
            v-if="selectedHospital" 
            :hospital="selectedHospital" 
            @close="selectedHospital = null" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@fortawesome/fontawesome-free/css/all.min.css';

/* Layout Styles */
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8faf9;
}

.admin-container {
  display: flex;
  flex: 1;
  margin-top: 70px;
}

.admin-content {
  flex: 1;
  padding: 30px;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  background-color: #f8faf9;
}

.admin-content.collapsed {
  margin-left: 80px;
}

.verify-hospitals {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Improved Header Styles */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.03);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-title h1 {
  margin: 0;
  font-size: 24px;
  color: #2d6a4f;
  font-weight: 600;
}

.header-icon {
  font-size: 24px;
  color: #2d6a4f;
}

.badge {
  background: #e76f51;
  color: white;
  border-radius: 12px;
  padding: 4px 10px;
  font-size: 14px;
  font-weight: 600;
  margin-left: 10px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-filter {
  position: relative;
  display: flex;
  align-items: center;
}

.search-filter i {
  position: absolute;
  left: 12px;
  color: #7b8a82;
}

.search-filter input {
  padding: 10px 15px 10px 40px;
  border: 1px solid #e8f0eb;
  border-radius: 6px;
  width: 250px;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: white;
  height: 40px;
}

.search-filter input:focus {
  outline: none;
  border-color: #2d6a4f;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.1);
}

.clear-search {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 5px;
}

.clear-search:hover {
  color: #e76f51;
}

.status-filter {
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #e8f0eb;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  height: 40px;
  min-width: 150px;
}

.status-filter:focus {
  outline: none;
  border-color: #2d6a4f;
}

.btn-refresh {
  padding: 10px;
  border-radius: 6px;
  background: #2d6a4f;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  background: #245c43;
  transform: rotate(180deg);
}

/* Loading State */
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2d6a4f;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  color: #4a5568;
  font-size: 16px;
}

/* Error State */
.error-alert {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 8px;
  margin-bottom: 20px;
}

.error-alert i {
  font-size: 20px;
}

.error-alert span {
  flex: 1;
}

.btn-retry {
  padding: 8px 15px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-retry:hover {
  background: #c82333;
}

/* Improved Card Styles */
.verification-list {
  display: grid;
  gap: 15px;
}

.verification-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(46, 106, 79, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;
  cursor: pointer;
}

.verification-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(46, 106, 79, 0.1);
}

.verification-card.pending {
  border-left-color: #ffc107;
}

.verification-card.approved {
  border-left-color: #28a745;
}

.verification-card.rejected {
  border-left-color: #dc3545;
}

.hospital-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 20px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
  border: 2px solid #f0f0f0;
  background-color: #f5f5f5;
}

.hospital-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-indicator.pending {
  background-color: #ffc107;
}

.status-indicator.approved {
  background-color: #28a745;
}

.status-indicator.rejected {
  background-color: #dc3545;
}

.details {
  flex: 1;
}

.name-type {
  margin-bottom: 10px;
}

.details h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #2d3748;
  font-weight: 600;
}

.type {
  margin: 0;
  font-size: 14px;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 8px;
}

.type i {
  color: #2d6a4f;
}

.hospital-meta {
  display: flex;
  gap: 30px;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.contact-info p {
  margin: 0;
  font-size: 14px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 5px;
}

.contact-info i {
  color: #7b8a82;
  width: 16px;
  text-align: center;
}

.submission-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.submission-date, .review-date {
  font-size: 13px;
  color: #a0aec0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.submission-date i, .review-date i {
  color: #b8c7ce;
}

/* Action Buttons */
.verification-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn span {
  display: inline-block;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-1px);
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover {
  background: #138496;
  transform: translateY(-1px);
}

.btn-primary {
  background: #2d6a4f;
  color: white;
}

.btn-primary:hover {
  background: #245c43;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 50px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(46, 106, 79, 0.05);
}

.empty-state i {
  font-size: 50px;
  color: #b8c7ce;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-weight: 600;
}

.empty-state p {
  margin: 0 0 20px 0;
  color: #718096;
}

/* Responsive Adjustments */
@media (max-width: 992px) {
  .verification-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .verification-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .hospital-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .admin-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-filter input {
    width: 100%;
  }
  
  .verification-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 576px) {
  .admin-content {
    padding: 15px;
  }
  
  .verification-card {
    padding: 15px;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
  }
  
  .btn span {
    display: none;
  }
  
  .btn i {
    margin-right: 0;
  }
}
</style>

<script>
import RejectModal from '@/components/admin/verify/hospitals/RejectModal.vue';
import HospitalDetailModal from '@/components/admin/verify/hospitals/HospitalDetailModal.vue';
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';

export default {
  components: {
    RejectModal,
    HospitalDetailModal,
    AdminSidebar,
    AdminNavbar
  },
  data() {
    return {
      filterStatus: 'pending',
      searchQuery: '',
      hospitals: [],
      loading: false,
      error: null,
      showRejectReasonModal: false,
      selectedHospital: null,
      hospitalToReject: null,
      defaultHospital: '/images/default-hospital.png',
      isSidebarCollapsed: false,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        perPage: 10,
        totalItems: 0
      }
    }
  },
  computed: {
    filteredHospitals() {
      let filtered = this.hospitals.map(hospital => {
        return {
          ...hospital,
          status: hospital.verified ? 'approved' : 
                 hospital.rejection_reason ? 'rejected' : 'pending'
        };
      });
      
      if (this.filterStatus !== 'all') {
        filtered = filtered.filter(h => h.status === this.filterStatus);
      }

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(h => 
          (h.name && h.name.toLowerCase().includes(query)) ||
          (h.type && h.type.toLowerCase().includes(query)) ||
          (h.email && h.email.toLowerCase().includes(query)) ||
          (h.license_number && h.license_number.toLowerCase().includes(query)) ||
          (h.address && h.address.toLowerCase().includes(query))
        );
      }
      
      return filtered;
    },
    pendingCount() {
      return this.hospitals.filter(h => !h.verified && !h.rejection_reason).length;
    }
  },
  watch: {
    filterStatus() {
      this.pagination.currentPage = 1;
      this.fetchHospitals();
    },
    'pagination.currentPage': 'fetchHospitals',
    'pagination.perPage': 'fetchHospitals'
  },
  async created() {
    await this.fetchHospitals();
  },
  methods: {
    async fetchHospitals() {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$store.dispatch('admin/fetchUnverifiedHospitals', {
          page: this.pagination.currentPage,
          perPage: this.pagination.perPage,
          status: this.filterStatus
        });
        console.log('Fetched hospitals:', response.data.data);
        this.hospitals = response.data.data.map(hospital => {
          let avatarData = this.defaultHospital;
          try {
            if (hospital.logo) {
              const logoString = hospital.logo.replace(/'/g, '"');
              const logoObj = JSON.parse(logoString);
              avatarData = logoObj?.data || this.defaultHospital;
            }
          } catch (e) {
            console.error('Error parsing logo:', e);
          }

          return {
            id: hospital.id,
            name: hospital.name,
            type: hospital.type,
            beds: hospital.beds,
            email: hospital.email,
            phone: hospital.phone,
            address: hospital.address,
            license_number: hospital.license_number,
            verified: hospital.verified,
            avatar: avatarData,
            documents: hospital.documents || [],
            submission_date: hospital.submission_date,
            established: hospital.established,
            operating_hours: hospital.operating_hours,
            emergency_service: hospital.emergency_service,
            medical_staff: hospital.medical_staff,
            rejection_reason: hospital.rejection_reason
          };
        });
        
        this.pagination = {
          currentPage: response.data.pagination.current_page || 1,
          totalPages: response.data.pagination.pages || 1,
          perPage: response.data.pagination.per_page || 10,
          totalItems: response.data.pagination.total || 0
        };
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to load hospitals';
        console.error('Error fetching hospitals:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async approveHospital(hospitalId) {
  try {
    await this.$store.dispatch('admin/approve', {
      entityType: 'hospital',  
      entityId: hospitalId,
    });

    const index = this.hospitals.findIndex(h => h.user_id === hospitalId);
    if (index !== -1) {
      this.hospitals[index].verified = true;
      this.hospitals[index].status_encrypted = 'approved'; 
    }
    
    await this.fetchHospitals();
  } catch (error) {
    const errorMessage = error?.response?.data?.message 
      || error?.message 
      || 'An unexpected error occurred while approving the hospital.';
    this.$toast.error(errorMessage);
    
    // Log the error for debugging
    console.error('Approval error:', error);
  }
},
    
    showRejectModal(id) {
      this.hospitalToReject = id;
      this.showRejectReasonModal = true;
    },
    
    async rejectHospital(rejectionReason) {
  if (!rejectionReason?.trim()) {
    this.$toast.error('Reddetme sebebi gereklidir');
    return false;
  }

  if (!this.hospitalToReject) {
    this.$toast.error('Reddedilecek hastane seçilmedi');
    return false;
  }

  try {
    this.$store.commit('admin/SET_LOADING', true);
    
    await this.$store.dispatch('admin/reject', {
      entityId: this.hospitalToReject,
      entityType: 'hospital',  
      description: rejectionReason.trim()
    });

    const hospitalIndex = this.hospitals.findIndex(h => h.id === this.hospitalToReject);
    if (hospitalIndex !== -1) {
      this.hospitals[hospitalIndex].verified = false;
      this.hospitals[hospitalIndex].rejection_reason = rejectionReason.trim();
    }

    this.showRejectReasonModal = false;
    this.hospitalToReject = null;
    
    await this.fetchHospitals();
    return true;
    
  } catch (error) {
    console.error('Hospital rejection failed:', error);
    
    const errorMessage = error.response?.data?.message 
      || error.message 
      || 'Hastane reddedilirken bir hata oluştu';
    
    this.$toast.error(errorMessage);
    return false;
    
  } finally {
    this.$store.commit('admin/SET_LOADING', false);
  }
},
    
    viewDetails(hospital) {
      this.selectedHospital = { ...hospital };
    },
    
    closeDetails() {
      this.selectedHospital = null;
    },
    
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return isNaN(date.getTime()) 
          ? 'Invalid date' 
          : date.toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            });
      } catch (e) {
        return 'Invalid date';
      }
    },
    
    async changePage(page) {
      if (page < 1 || page > this.pagination.totalPages) return;
      this.pagination.currentPage = page;
    }
  }
}
</script>
  