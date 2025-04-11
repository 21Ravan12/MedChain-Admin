<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="verify-pharmacies">
          <!-- Page Header with Search and Filter -->
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-prescription-bottle-alt header-icon"></i>
              <h1>Pharmacy Verification</h1>
              <span class="badge">{{ pendingCount }}</span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search pharmacies..."
                  @input="handleSearch"
                />
                <button v-if="searchQuery" class="clear-search" @click="clearSearch">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <select v-model="filterStatus" class="status-filter" @change="fetchPharmacies">
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
            <p>Loading pharmacies...</p>
          </div>

          <!-- Error State -->
          <div v-if="error" class="error-alert">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
            <button @click="fetchPharmacies" class="btn-retry">
              <i class="fas fa-redo"></i> Retry
            </button>
          </div>
          
          <!-- Pharmacy List -->
          <div class="verification-list">
            <div 
              v-for="pharmacy in filteredPharmacies" 
              :key="pharmacy.id" 
              class="verification-card"
              :class="pharmacy.status"
              @click="viewDetails(pharmacy)"
            >
              <!-- Ensure this passes the pharmacy object -->
              <div class="pharmacy-info">
                <div class="avatar">
                  <img 
                    :src="pharmacy.avatar || defaultPharmacy" 
                    alt="Pharmacy Logo"
                    @error="handleImageError"
                    class="pharmacy-logo"
                  />
                  <div class="status-indicator" :class="pharmacy.status"></div>
                </div>
                <div class="details">
                  <div class="name-type">
                    <h3>{{ pharmacy.name }}</h3>
                    <p class="type">
                      <i class="fas fa-prescription-bottle-alt"></i>
                      {{ pharmacy.type || 'Community Pharmacy' }}
                    </p>
                  </div>
                  <div class="pharmacy-meta">
                    <div class="contact-info">
                      <p><i class="fas fa-envelope"></i> {{ pharmacy.email || 'No email' }}</p>
                      <p><i class="fas fa-phone"></i> {{ pharmacy.phone || 'Not provided' }}</p>
                      <p><i class="fas fa-map-marker-alt"></i> {{ pharmacy.address }}</p>
                    </div>
                    <div class="submission-info">
                      <div class="submission-date">
                        <i class="fas fa-calendar-alt"></i>
                        Submitted: {{ formatDate(pharmacy.submittedAt) }}
                      </div>
                      <div v-if="pharmacy.reviewedAt" class="review-date">
                        <i class="fas fa-check-circle"></i>
                        Reviewed: {{ formatDate(pharmacy.reviewedAt) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="verification-actions" @click.stop>
                <button 
                  v-if="pharmacy.status === 'pending'" 
                  @click.stop="approvePharmacy(pharmacy.id)" 
                  class="btn btn-success"
                  :disabled="processingApproval === pharmacy.id"
                >
                  <i class="fas fa-check"></i> 
                  <span>{{ processingApproval === pharmacy.id ? 'Processing...' : 'Approve' }}</span>
                </button>
                <button 
                  v-if="pharmacy.status === 'pending'" 
                  @click.stop="showRejectModal(pharmacy.id)" 
                  class="btn btn-danger"
                  :disabled="processingRejection === pharmacy.id"
                >
                  <i class="fas fa-times"></i> 
                  <span>Reject</span>
                </button>
                <button 
                  @click.stop="viewDetails(pharmacy)" 
                  class="btn btn-info"
                >
                  <i class="fas fa-eye"></i> 
                  <span>Details</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Reject Modal -->
          <RejectModal 
            v-if="showRejectReasonModal" 
            @submit="rejectPharmacy" 
            @cancel="showRejectReasonModal = false" 
          />
          
          <!-- Pharmacy Detail Modal -->
          <PharmacyDetailModal 
            v-if="selectedPharmacy" 
            :pharmacy="selectedPharmacy" 
            @close="selectedPharmacy = null" 
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

.verify-pharmacies {
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

.pharmacy-info {
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

.pharmacy-logo {
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

.pharmacy-meta {
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
  
  .pharmacy-meta {
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
import RejectModal from '@/components/admin/verify/pharmacies/RejectModal.vue';
import PharmacyDetailModal from '@/components/admin/verify/pharmacies/PharmacyDetailModal.vue';
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';

export default {
  components: {
    RejectModal,
    PharmacyDetailModal,
    AdminSidebar,
    AdminNavbar
  },
  data() {
    return {
      filterStatus: 'pending',
      searchQuery: '',
      pharmacies: [],
      showRejectReasonModal: false,
      selectedPharmacy: null,
      pharmacyToReject: null,
      defaultPharmacy: '/images/default-pharmacy.png',
      isSidebarCollapsed: false,
      loading: false,
      error: null,
      processingRejection: null,
      processingApproval: null,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        perPage: 10,
        totalItems: 0
      }
    }
  },
  computed: {
    filteredPharmacies() {
      let filtered = this.pharmacies;
      
      if (this.filterStatus !== 'all') {
        filtered = filtered.filter(p => p.status === this.filterStatus);
      }
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(query) ||
          p.type.toLowerCase().includes(query) ||
          p.email.toLowerCase().includes(query) ||
          p.licenseNumber.toLowerCase().includes(query) ||
          p.address.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    },
    pendingCount() {
      return this.pharmacies.filter(p => p.status === 'pending').length;
    }
  },
  created() {
    this.fetchPharmacies();
  },
  methods: {
    async fetchPharmacies() {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$store.dispatch('admin/fetchUnverifiedPharmacies', {
          page: this.pagination.currentPage,
          perPage: this.pagination.perPage,
          status: this.filterStatus
        });
        
        this.pharmacies = response.data.data.map(pharmacy => {
          console.log(pharmacy);
          let avatarData = this.defaultPharmacy;
          try {
            if (pharmacy.logo) {
              const logoString = pharmacy.logo.replace(/'/g, '"');
              const logoObj = JSON.parse(logoString);
              avatarData = logoObj?.data || this.defaultPharmacy;
            }
            if (
              pharmacy.documents &&
              Array.isArray(pharmacy.documents) &&
              pharmacy.documents[0]?.license &&
              typeof pharmacy.documents[0].license === 'string' &&
              pharmacy.documents[0]?.accreditation &&
              typeof pharmacy.documents[0].accreditation === 'string'
            ) {
              const licenseString = pharmacy.documents[0].license.replace(/'/g, '"');
              const accreditationString = pharmacy.documents[0].accreditation.replace(/'/g, '"');

              const licenseObj = JSON.parse(licenseString);
              const accreditationObj = JSON.parse(accreditationString);

              pharmacy.documents[0].license = licenseObj;
              pharmacy.documents[0].accreditation = accreditationObj;
            }
          } catch (e) {
            console.error('Error parsing logo:', e);
          }

          return {
            id: pharmacy.id,
            name: pharmacy.name,
            type: pharmacy.type,
            email: pharmacy.email,
            phone: pharmacy.phone,
            address: pharmacy.address,
            licenseNumber: pharmacy.license_number,
            status: pharmacy.verified ? 'approved' : pharmacy.rejection_reason ? 'rejected' : 'pending',
            avatar: avatarData,
            documents: pharmacy.documents || [],
            submittedAt: pharmacy.submission_date,
            established: pharmacy.established,
            operating_hours: pharmacy.operating_hours,
            rejection_reason: pharmacy.rejection_reason
          };
        });
        
        this.pagination = {
          currentPage: response.data.pagination.current_page || 1,
          totalPages: response.data.pagination.pages || 1,
          perPage: response.data.pagination.per_page || 10,
          totalItems: response.data.pagination.total || 0
        };
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to load pharmacies';
        console.error('Error fetching pharmacies:', error);
        this.$toast.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async approvePharmacy(id) {
      try {
        await this.$store.dispatch('admin/approve', {
          entityType: 'pharmacy',
          entityId: id,
        });

        const index = this.pharmacies.findIndex(p => p.id === id);
        if (index !== -1) {
          this.pharmacies[index].status = 'approved';
        }
        
        await this.fetchPharmacies();
      } catch (error) {
        const errorMessage = error?.response?.data?.message 
          || error?.message 
          || 'An unexpected error occurred while approving the pharmacy.';
        this.$toast.error(errorMessage);
        console.error('Approval error:', error);
      }
    },
    showRejectModal(id) {
      this.pharmacyToReject = id;
      this.showRejectReasonModal = true;
    },
    async rejectPharmacy(reason) {
      if (!reason?.trim()) {
        return false;
      }

      if (!this.pharmacyToReject) {
        return false;
      }

      try {
        this.loading = true;
        
        await this.$store.dispatch('admin/reject', {
          entityId: this.pharmacyToReject,
          entityType: 'pharmacy',
          description: reason.trim()
        });

        const pharmacyIndex = this.pharmacies.findIndex(p => p.id === this.pharmacyToReject);
        if (pharmacyIndex !== -1) {
          this.pharmacies[pharmacyIndex].status = 'rejected';
          this.pharmacies[pharmacyIndex].rejection_reason = reason.trim();
        }

        this.showRejectReasonModal = false;
        this.pharmacyToReject = null;
        
        await this.fetchPharmacies();
        return true;
        
      } catch (error) {
        console.error('Pharmacy rejection failed:', error);
        
        const errorMessage = error.response?.data?.message 
          || error.message 
          || 'An error occurred while rejecting the pharmacy';
        
        return false;
        
      } finally {
        this.loading = false;
      }
    },
    viewDetails(pharmacy) {
      this.selectedPharmacy = pharmacy; // Set the selected pharmacy
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  }
}
</script>
