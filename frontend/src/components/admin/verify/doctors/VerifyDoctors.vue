<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="verify-doctors">
          <!-- Page Header with Search and Filter -->
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-user-md header-icon"></i>
              <h1>Doctor Verification</h1>
              <span class="badge">{{ pendingCount }}</span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search doctors..."
                  @input="handleSearch"
                >
                <button v-if="searchQuery" class="clear-search" @click="clearSearch">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <select v-model="filterStatus" class="status-filter" @change="fetchDoctors">
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
            <p>Loading doctors...</p>
          </div>

          <!-- Error State -->
          <div v-if="error" class="error-alert">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
            <button @click="fetchDoctors" class="btn-retry">
              <i class="fas fa-redo"></i> Retry
            </button>
          </div>
          
          <!-- Doctor List -->
          <div class="verification-list">
            <div 
              v-for="doctor in filteredDoctors" 
              :key="doctor.id" 
              class="verification-card"
              :class="doctor.status"
              @click="viewDetails(doctor)"
            >
              <div class="doctor-info">
                <div class="avatar">
                  <img 
                    :src="doctor.avatar || defaultDoctorImage" 
                    :alt="`Dr. ${doctor.fullName}`"
                    @error="handleImageError"
                    class="doctor-avatar"
                  >
                  <div class="status-indicator" :class="doctor.status"></div>
                </div>
                <div class="details">
                  <div class="name-specialty">
                    <h3>Dr. {{ doctor.fullName }}</h3>
                    <p class="specialty">
                      <i class="fas fa-stethoscope"></i>
                      {{ doctor.specialization || 'General Practitioner' }}
                    </p>
                  </div>
                  <div class="doctor-meta">
                    <div class="contact-info">
                      <p><i class="fas fa-envelope"></i> {{ doctor.email }}</p>
                      <p><i class="fas fa-id-card"></i> {{ doctor.licenseNumber || 'License not provided' }}</p>
                    </div>
                    <div class="submission-info">
                      <div class="submission-date">
                        <i class="fas fa-calendar-alt"></i>
                        Submitted: {{ formatDate(doctor.submittedAt) }}
                      </div>
                      <div v-if="doctor.reviewedAt" class="review-date">
                        <i class="fas fa-check-circle"></i>
                        Reviewed: {{ formatDate(doctor.reviewedAt) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="verification-actions" @click.stop>
                <button 
                  v-if="doctor.status === 'pending'" 
                  @click.stop="approveDoctor(doctor.id)" 
                  class="btn btn-success"
                  :disabled="processingApproval === doctor.id"
                >
                  <i class="fas fa-check"></i> 
                  <span>{{ processingApproval === doctor.id ? 'Processing...' : 'Approve' }}</span>
                </button>
                <button 
                  v-if="doctor.status === 'pending'" 
                  @click.stop="showRejectModal(doctor.id)" 
                  class="btn btn-danger"
                  :disabled="processingRejection === doctor.id"
                >
                  <i class="fas fa-times"></i> 
                  <span>{{ processingRejection === doctor.id ? 'Processing...' : 'Reject' }}</span>
                </button>
                <button 
                  @click.stop="viewDetails(doctor)" 
                  class="btn btn-info"
                >
                  <i class="fas fa-eye"></i> 
                  <span>Details</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!loading && filteredDoctors.length === 0" class="empty-state">
            <i class="fas fa-user-md"></i>
            <h3>No doctors found</h3>
            <p>Try adjusting your search or filter criteria</p>
            <button class="btn btn-primary" @click="resetFilters">
              <i class="fas fa-filter"></i> Reset Filters
            </button>
          </div>

          <!-- Pagination -->
          <div v-if="pagination.totalPages > 1" class="pagination-controls">
            <button 
              @click="changePage(pagination.currentPage - 1)" 
              :disabled="pagination.currentPage === 1"
              class="pagination-btn"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            <div class="page-info">
              Page {{ pagination.currentPage }} of {{ pagination.totalPages }}
            </div>
            <button 
              @click="changePage(pagination.currentPage + 1)" 
              :disabled="pagination.currentPage === pagination.totalPages"
              class="pagination-btn"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          
          <!-- Reject Modal -->
          <RejectModal 
            v-if="showRejectReasonModal" 
            @submit="rejectDoctor" 
            @cancel="showRejectReasonModal = false" 
          />
          
          <!-- Doctor Detail Modal -->
          <DoctorDetailModal 
            v-if="selectedDoctor" 
            :doctor="selectedDoctor" 
            @close="selectedDoctor = null" 
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

.verify-doctors {
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

.doctor-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
  border: 2px solid #f0f0f0;
}

.doctor-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: #f5f5f5;
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

.name-specialty {
  margin-bottom: 10px;
}

.details h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #2d3748;
  font-weight: 600;
}

.specialty {
  margin: 0;
  font-size: 14px;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 8px;
}

.specialty i {
  color: #2d6a4f;
}

.doctor-meta {
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

/* Pagination */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 20px 0;
}

.pagination-btn {
  padding: 8px 15px;
  border: 1px solid #e8f0eb;
  border-radius: 6px;
  background: white;
  color: #2d6a4f;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn:hover:not(:disabled) {
  background: #f1f8f5;
  border-color: #2d6a4f;
}

.pagination-btn:disabled {
  color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.7;
}

.page-info {
  padding: 8px 15px;
  color: #4a5568;
  font-size: 14px;
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
  
  .doctor-meta {
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
  
  .pagination-controls {
    flex-direction: column;
    gap: 10px;
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
    width: 60px;
    height: 60px;
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
import RejectModal from '@/components/admin/verify/doctors/RejectModal.vue';
import DoctorDetailModal from '@/components/admin/verify/doctors/DoctorDetailModal.vue';
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';
import debounce from 'lodash/debounce';

export default {
  components: {
    RejectModal,
    DoctorDetailModal,
    AdminSidebar,
    AdminNavbar
  },
  data() {
    return {
      filterStatus: 'pending',
      searchQuery: '',
      doctors: [],
      showRejectReasonModal: false,
      selectedDoctor: null,
      doctorToReject: null,
      defaultAvatar: '/images/default-doctor.png',
      isSidebarCollapsed: false,
      loading: false,
      error: null,
      processingApproval: null,
      processingRejection: null,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        perPage: 10,
        totalItems: 0
      }
    }
  },
  computed: {
    filteredDoctors() {
      let filtered = this.doctors;
      
      // Filter by status
      if (this.filterStatus !== 'all') {
        filtered = filtered.filter(d => d.status === this.filterStatus);
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(d => 
          d.fullName.toLowerCase().includes(query) ||
          d.specialization.toLowerCase().includes(query) ||
          d.email.toLowerCase().includes(query) ||
          d.licenseNumber.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    },
    pendingCount() {
      return this.doctors.filter(d => d.status === 'pending').length;
    }
  },
  created() {
    this.fetchDoctors();
    this.debouncedSearch = debounce(this.fetchDoctors, 500);
  },
  methods: {
    async fetchDoctors() {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$store.dispatch('admin/fetchUnverifiedDoctors', {
          page: this.pagination.currentPage,
          perPage: this.pagination.perPage,
          status: this.filterStatus,
          search: this.searchQuery
        });
        
        this.doctors = response.data.data.map(doctor => {
          console.log(doctor);
          let avatarData = this.defaultAvatar;
          try {
            if (doctor.profile_image && typeof doctor.profile_image === 'string') {
              const avatarString = doctor.profile_image.replace(/'/g, '"');
              const avatarObj = JSON.parse(avatarString);
              avatarData = "data:image/png;base64," + avatarObj?.data;
            }
            if (
              doctor.documents &&
              Array.isArray(doctor.documents) &&
              doctor.documents[0]?.license &&
              typeof doctor.documents[0].license === 'string'
            ) {
              const documentString = doctor.documents[0].license.replace(/'/g, '"');
              const documentObj = JSON.parse(documentString);
              doctor.documents[0].license = documentObj;
            }
          } catch (e) {
            console.error('Error parsing avatar or document:', e);
          }
          
          return {
            id: doctor.id,
            fullName: doctor.name,
            specialization: doctor.specialty || 'Not specified',
            email: doctor.email,
            licenseNumber: doctor.license_number || 'Not provided',
            status: doctor.verified ? 'approved' : doctor.rejection_reason ? 'rejected' : 'pending',
            avatar: avatarData,
            documents: doctor.documents || [],
            submittedAt: doctor.submission_date,
            rejectionReason: doctor.rejection_reason
          };
        });

        this.pagination = {
          currentPage: response.data.pagination.current_page || 1,
          totalPages: response.data.pagination.pages || 1,
          perPage: response.data.pagination.per_page || 10,
          totalItems: response.data.pagination.total || 0
        };
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to load doctors';
        console.error('Error fetching doctors:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async approveDoctor(doctorId) {
      this.processingApproval = doctorId;
      try {
        await this.$store.dispatch('admin/approve', {
          entityType: 'doctor',  
          entityId: doctorId,
        });

        await this.fetchDoctors();
      } catch (error) {
        const errorMessage = error?.response?.data?.message 
          || error?.message 
          || 'An unexpected error occurred while approving the doctor.';
        this.$toast.error(errorMessage);
        console.error('Approval error:', error);
      } finally {
        this.processingApproval = null;
      }
    },
    
    showRejectModal(id) {
      this.doctorToReject = id;
      this.showRejectReasonModal = true;
    },
    
    async rejectDoctor(rejectionReason) {
      if (!rejectionReason?.trim()) {
        this.$toast.error('Rejection reason is required');
        return false;
      }

      if (!this.doctorToReject) {
        this.$toast.error('No doctor selected for rejection');
        return false;
      }

      this.processingRejection = this.doctorToReject;
      this.showRejectReasonModal = false;

      try {
        await this.$store.dispatch('admin/reject', {
          entityId: this.doctorToReject,
          entityType: 'doctor',  
          description: rejectionReason.trim()
        });

        await this.fetchDoctors();
        return true;
        
      } catch (error) {
        console.error('Doctor rejection failed:', error);
        
        const errorMessage = error.response?.data?.message 
          || error.message 
          || 'An error occurred while rejecting the doctor';
        
        this.$toast.error(errorMessage);
        return false;
        
      } finally {
        this.doctorToReject = null;
        this.processingRejection = null;
      }
    },
    
    viewDetails(doctor) {
      this.selectedDoctor = { ...doctor };
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
      await this.fetchDoctors();
    },
    
    handleSearch() {
      this.debouncedSearch();
    },
    
    handleImageError(event) {
      event.target.src = this.defaultAvatar;
    }
  }
}
</script>
