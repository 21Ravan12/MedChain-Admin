<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="verify-pharmacists">
          <!-- Page Header with Search and Filter -->
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-prescription-bottle-alt header-icon"></i>
              <h1>Pharmacist Verification</h1>
              <span class="badge">{{ pendingCount }}</span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search pharmacists..."
                  @input="handleSearch"
                >
                <button v-if="searchQuery" class="clear-search" @click="clearSearch">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <select v-model="filterStatus" class="status-filter" @change="fetchPharmacists">
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
            <p>Loading pharmacists...</p>
          </div>

          <!-- Error State -->
          <div v-if="error" class="error-alert">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
            <button @click="fetchPharmacists" class="btn-retry">
              <i class="fas fa-redo"></i> Retry
            </button>
          </div>
          
          <!-- Pharmacist List -->
          <div class="verification-list">
            <div 
              v-for="pharmacist in filteredPharmacists" 
              :key="pharmacist.id" 
              class="verification-card"
              :class="pharmacist.status"
              @click="viewDetails(pharmacist)"
            >
              <div class="pharmacist-info">
                <div class="avatar">
                  <img 
                    :src="pharmacist.avatar || defaultAvatar" 
                    alt="Pharmacist Photo"
                    @error="handleImageError"
                    class="pharmacist-avatar"
                  >
                  <div class="status-indicator" :class="pharmacist.status"></div>
                </div>
                <div class="details">
                  <div class="name-credentials">
                    <h3>{{ pharmacist.name }}</h3>
                    <p class="credentials">
                      <i class="fas fa-graduation-cap"></i>
                      {{ pharmacist.position || 'Pharmacist' }}
                      <span v-if="pharmacist.licenseNumber" class="license-number">
                        • License: {{ pharmacist.licenseNumber }}
                      </span>
                    </p>
                  </div>
                  <div class="pharmacist-meta">
                    <div class="contact-info">
                      <p><i class="fas fa-envelope"></i> {{ pharmacist.email || 'No email' }}</p>
                      <p><i class="fas fa-phone"></i> {{ pharmacist.phone || 'Not provided' }}</p>
                    </div>
                    <div class="submission-info">
                      <div class="submission-date">
                        <i class="fas fa-calendar-alt"></i>
                        Submitted: {{ formatDate(pharmacist.submittedAt) }}
                      </div>
                      <div v-if="pharmacist.reviewedAt" class="review-date">
                        <i class="fas fa-check-circle"></i>
                        Reviewed: {{ formatDate(pharmacist.reviewedAt) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="verification-actions" @click.stop>
                <button 
                  v-if="pharmacist.status === 'pending'" 
                  @click.stop="approvePharmacist(pharmacist.id)" 
                  class="btn btn-success"
                  :disabled="processingApproval === pharmacist.id"
                >
                  <i class="fas fa-check"></i> 
                  <span>{{ processingApproval === pharmacist.id ? 'Processing...' : 'Approve' }}</span>
                </button>
                <button 
                  v-if="pharmacist.status === 'pending'" 
                  @click.stop="showRejectModal(pharmacist.id)" 
                  class="btn btn-danger"
                  :disabled="processingRejection === pharmacist.id"
                >
                  <i class="fas fa-times"></i> 
                  <span>{{ processingRejection === pharmacist.id ? 'Processing...' : 'Reject' }}</span>
                </button>
                <button 
                  @click.stop="viewDetails(pharmacist)" 
                  class="btn btn-info"
                >
                  <i class="fas fa-eye"></i> 
                  <span>Details</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!loading && filteredPharmacists.length === 0" class="empty-state">
            <i class="fas fa-prescription-bottle-alt"></i>
            <h3>No pharmacists found</h3>
            <p>Try adjusting your search or filter criteria</p>
            <button class="btn btn-primary" @click="resetFilters">
              <i class="fas fa-filter"></i> Reset Filters
            </button>
          </div>

          <!-- Pagination -->
          <div v-if="!loading && !error && pagination.totalPages > 1" class="pagination-controls">
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
            @submit="rejectPharmacist" 
            @cancel="showRejectReasonModal = false" 
          />
          
          <!-- Pharmacist Detail Modal -->
          <PharmacistDetailModal 
            v-if="selectedPharmacist" 
            :pharmacist="selectedPharmacist" 
            @close="selectedPharmacist = null" 
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

.verify-pharmacists {
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

.pharmacist-info {
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

.pharmacist-avatar {
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

.name-credentials {
  margin-bottom: 10px;
}

.details h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #2d3748;
  font-weight: 600;
}

.credentials {
  margin: 0;
  font-size: 14px;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 8px;
}

.credentials i {
  color: #2d6a4f;
}

.license-number {
  font-size: 13px;
  color: #718096;
}

.pharmacist-meta {
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
  
  .pharmacist-meta {
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
import RejectModal from '@/components/admin/verify/pharmacists/RejectModal.vue';
import PharmacistDetailModal from '@/components/admin/verify/pharmacists/PharmacistDetailModal.vue';
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';
import { debounce } from 'lodash';

export default {
  components: {
    RejectModal,
    PharmacistDetailModal,
    AdminSidebar,
    AdminNavbar
  },
  data() {
    return {
      filterStatus: 'pending',
      searchQuery: '',
      pharmacists: [],
      showRejectReasonModal: false,
      selectedPharmacist: null,
      pharmacistToReject: null,
      defaultAvatar: '/images/default-pharmacist.png',
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
    filteredPharmacists() {
      let filtered = this.pharmacists;
      
      // Filter by status
      if (this.filterStatus !== 'all') {
        filtered = filtered.filter(p => p.status === this.filterStatus);
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(query) ||
          p.position.toLowerCase().includes(query) ||
          p.email.toLowerCase().includes(query) ||
          (p.adminId && p.adminId.toLowerCase().includes(query))
        );
      }
      
      return filtered;
    },
    pendingCount() {
      return this.pharmacists.filter(p => p.status === 'pending').length;
    }
  },
  created() {
    this.fetchPharmacistAdmins();
    this.debouncedSearch = debounce(this.fetchPharmacistAdmins, 500);
  },
  methods: {
    async fetchPharmacistAdmins() {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$store.dispatch('admin/fetchUnverifiedPharmacists', {
          page: this.pagination.currentPage,
          perPage: this.pagination.perPage,
          status: this.filterStatus,
          search: this.searchQuery
        });
        
        this.pharmacists = response.data.data.map(admin => {
          let avatarData = this.defaultAvatar;
          try {
            if (admin.profile_image) {
              const avatarString = admin.profile_image.replace(/'/g, '"');
              const avatarObj = JSON.parse(avatarString);
              avatarData = "data:image/png;base64,"+avatarObj?.data;
            }
          } catch (e) {
            console.error('Error parsing avatar:', e);
          }

          return {
            id: admin.id,
            name: admin.name,
            position: admin.role || 'Not specified',
            PharmacistName: admin.Pharmacist_name || 'Not specified',
            email: admin.email,
            phone: admin.phone || 'Not provided',
            adminId: admin.license_number_encrypted || 'Not provided',
            status: admin.verified ? 'approved' : admin.rejection_reason ? 'rejected' : 'pending',
            avatar: avatarData,
            documents: admin.documents || [],
            submittedAt: admin.submission_date || new Date(),
            rejectionReason: admin.rejection_reason
          };
        });
        
        this.pagination = {
          currentPage: response.data.pagination.current_page || 1,
          totalPages: response.data.pagination.pages || 1,
          perPage: response.data.pagination.per_page || 10,
          totalItems: response.data.pagination.total || 0
        };
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to load pharmacists';
        console.error('Error fetching pharmacists:', error);
        this.$toast.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async approvePharmacist(pharmacistId) {
      this.processingApproval = pharmacistId;
      try {
        await this.$store.dispatch('admin/approve', {
          entityType: 'pharmacist',  
          entityId: pharmacistId,
        });

        await this.fetchPharmacistAdmins();
        this.$toast.success('Pharmacist approved successfully');
      } catch (error) {
        const errorMessage = error?.response?.data?.message 
          || error?.message 
          || 'An unexpected error occurred while approving the pharmacist.';
        this.$toast.error(errorMessage);
        console.error('Approval error:', error);
      } finally {
        this.processingApproval = null;
      }
    },
    
    showRejectModal(id) {
      this.pharmacistToReject = id;
      this.showRejectReasonModal = true;
    },
    
    async rejectPharmacist(rejectionReason) {
      if (!rejectionReason?.trim()) {
        this.$toast.error('Rejection reason is required');
        return false;
      }

      if (!this.pharmacistToReject) {
        this.$toast.error('No pharmacist selected for rejection');
        return false;
      }

      this.processingRejection = this.pharmacistToReject;
      this.showRejectReasonModal = false;

      try {
        await this.$store.dispatch('admin/reject', {
          entityId: this.pharmacistToReject,
          entityType: 'pharmacist',  
          description: rejectionReason.trim()
        });

        await this.fetchPharmacistAdmins();
        return true;
      } catch (error) {
        console.error('Pharmacist rejection failed:', error);
        
        const errorMessage = error.response?.data?.message 
          || error.message 
          || 'An error occurred while rejecting the pharmacist';
        
        this.$toast.error(errorMessage);
        return false;
      } finally {
        this.pharmacistToReject = null;
        this.processingRejection = null;
      }
    },
    
    viewDetails(pharmacist) {
      this.selectedPharmacist = { ...pharmacist };
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
      await this.fetchPharmacistAdmins();
    },
    
    handleSearch() {
      this.pagination.currentPage = 1;
      this.debouncedSearch();
    },
    
    handleImageError(event) {
      event.target.src = this.defaultAvatar;
    }
  }
}
</script>