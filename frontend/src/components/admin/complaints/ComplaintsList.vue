<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="manage-complaints">
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-exclamation-triangle header-icon"></i>
              <h1>Complaints Management</h1>
              <span class="badge">{{ openComplaintsCount }}</span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search complaints..."
                >
              </div>
              <select v-model="filterStatus" class="status-filter">
                <option value="all">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>
          
          <div class="complaints-list">
            <div 
              v-for="complaint in filteredComplaints" 
              :key="complaint.id" 
              class="complaint-card"
              :class="complaint.status"
            >
              <div class="complaint-info">
                <div class="complaint-meta">
                  <span class="complaint-id">#{{ complaint.id }}</span>
                  <span class="complaint-type">{{ complaint.type }}</span>
                  <span class="complaint-date">
                    <i class="fas fa-calendar-alt"></i>
                    {{ formatDate(complaint.date) }}
                  </span>
                </div>
                
                <div class="parties">
                  <div class="party complainant">
                    <i class="fas fa-user-circle"></i>
                    <div>
                      <h4>Complainant</h4>
                      <p>{{ complaint.complainant.name }} ({{ complaint.complainant.type }})</p>
                    </div>
                  </div>
                  <div class="party against">
                    <i class="fas fa-user-slash"></i>
                    <div>
                      <h4>Against</h4>
                      <p>{{ complaint.against.name }} ({{ complaint.against.type }})</p>
                    </div>
                  </div>
                </div>
                
                <div class="complaint-preview">
                  <p>{{ truncateText(complaint.details, 100) }}</p>
                </div>
              </div>
              
              <div class="complaint-actions">
                <div class="status-indicator" :class="complaint.status">
                  {{ formatStatus(complaint.status) }}
                </div>
                <button 
                  @click="viewComplaint(complaint.id)" 
                  class="btn btn-primary"
                >
                  <i class="fas fa-eye"></i> View Details
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="filteredComplaints.length === 0" class="empty-state">
            <i class="fas fa-exclamation-circle"></i>
            <h3>No complaints found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
          
          <ComplaintDetailModal 
            v-if="selectedComplaint" 
            :complaint="selectedComplaint" 
            @resolve="resolveComplaint" 
            @close="selectedComplaint = null" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ComplaintDetailModal from '@/components/admin/complaints/ComplaintDetailModal.vue';
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';

export default {
  components: {
    ComplaintDetailModal,
    AdminNavbar,
    AdminSidebar
  },
  data() {
    return {
      filterStatus: 'open',
      searchQuery: '',
      complaints: [
        {
          id: 1,
          type: 'Data Privacy',
          complainant: { name: 'Patient A', type: 'patient' },
          against: { name: 'Hospital X', type: 'hospital' },
          date: '2023-05-10',
          status: 'open',
          details: 'Patient claims their data was shared without consent with third parties without authorization. The patient discovered this when receiving marketing calls referencing their medical history.',
          messages: [
            {
              sender: 'Patient A',
              date: '2023-05-10T14:30:00',
              content: 'I never authorized sharing my medical information with anyone!'
            },
            {
              sender: 'Support Team',
              date: '2023-05-11T09:15:00',
              content: 'We are investigating this matter and will get back to you shortly.'
            }
          ]
        },
        {
          id: 2,
          type: 'Service Quality',
          complainant: { name: 'Pharmacist B', type: 'staff' },
          against: { name: 'Dr. Smith', type: 'doctor' },
          date: '2023-05-15',
          status: 'in_progress',
          details: 'Pharmacist reports consistently receiving incomplete prescriptions from this doctor, causing delays in patient care.',
          messages: []
        },
        {
          id: 3,
          type: 'Billing Issue',
          complainant: { name: 'Patient C', type: 'patient' },
          against: { name: 'Pharmacy Y', type: 'pharmacy' },
          date: '2023-05-18',
          status: 'resolved',
          details: 'Patient was charged twice for the same medication. Issue has been resolved with refund processed.',
          messages: [],
          resolution: 'Duplicate charge confirmed. Refund processed on 2023-05-20.'
        }
      ],
      selectedComplaint: null,
      isSidebarCollapsed: false
    }
  },
  computed: {
    filteredComplaints() {
      let filtered = this.complaints;
      
      // Filter by status
      if (this.filterStatus !== 'all') {
        filtered = filtered.filter(c => c.status === this.filterStatus);
      }
      
      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(c => 
          c.type.toLowerCase().includes(query) ||
          c.complainant.name.toLowerCase().includes(query) ||
          c.against.name.toLowerCase().includes(query) ||
          c.details.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    },
    openComplaintsCount() {
      return this.complaints.filter(c => c.status === 'open').length;
    }
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    formatStatus(status) {
      return status.replace('_', ' ');
    },
    truncateText(text, length) {
      return text.length > length ? text.substring(0, length) + '...' : text;
    },
    viewComplaint(id) {
      this.selectedComplaint = this.complaints.find(c => c.id === id);
    },
    resolveComplaint(resolution) {
      const index = this.complaints.findIndex(c => c.id === this.selectedComplaint.id);
      this.complaints[index].status = 'resolved';
      this.complaints[index].resolution = resolution;
      this.complaints[index].resolvedAt = new Date().toISOString();
      this.selectedComplaint = null;
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    }
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.admin-container {
  display: flex;
  flex: 1;
  padding-top: 70px; /* Matches navbar height */
}

.admin-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  z-index: 975;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.admin-sidebar {
  position: fixed;
  left: 0;
  bottom: 0;
  z-index: 1000;
  transition: width 0.3s ease;
}


.admin-content {
  margin-left: 240px;
  flex: 1;
  padding: 20px;
  transition: margin-left 0.3s ease;
  background: #f5f7fa;
}

.admin-content.collapsed {
  margin-left: 60px;
}

.manage-complaints {
  padding: 20px;
}

.complaints-list {
  display: grid;
  gap: 15px;
}

.complaint-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border-left: 4px solid;
}

.complaint-card.open {
  border-left-color: #ffc107;
}

.complaint-card.in_progress {
  border-left-color: #17a2b8;
}

.complaint-card.resolved {
  border-left-color: #28a745;
}

.complaint-info {
  flex: 1;
}

.complaint-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.complaint-id {
  font-weight: bold;
  color: #343a40;
}

.complaint-type {
  background: #e9ecef;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.complaint-date {
  color: #6c757d;
  font-size: 14px;
}

.parties {
  display: flex;
  gap: 30px;
  margin-bottom: 15px;
}

.party {
  display: flex;
  align-items: center;
  gap: 10px;
}

.party i {
  font-size: 20px;
}

.party.complainant i {
  color: #17a2b8;
}

.party.against i {
  color: #dc3545;
}

.party h4 {
  font-size: 14px;
  margin: 0;
  color: #6c757d;
}

.party p {
  margin: 0;
  font-weight: 500;
}

.complaint-preview {
  color: #495057;
  line-height: 1.5;
}

.complaint-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  min-width: 150px;
}

.status-indicator {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.status-indicator.open {
  background-color: #fff3cd;
  color: #856404;
}

.status-indicator.in_progress {
  background-color: #cce5ff;
  color: #004085;
}

.status-indicator.resolved {
  background-color: #d4edda;
  color: #155724;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-state i {
  font-size: 50px;
  margin-bottom: 15px;
  color: #adb5bd;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #495057;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-title h1 {
  margin: 0;
  font-size: 24px;
}

.header-icon {
  font-size: 24px;
  color: #6c757d;
}

.badge {
  background: #dc3545;
  color: white;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-filter {
  position: relative;
}

.search-filter i {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-filter input {
  padding: 8px 15px 8px 35px;
  border-radius: 4px;
  border: 1px solid #ced4da;
  width: 250px;
}

.status-filter {
  padding: 8px 15px;
  border-radius: 4px;
  border: 1px solid #ced4da;
  background: white;
}

.btn {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0069d9;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-outline {
  background: transparent;
  border: 1px solid #007bff;
  color: #007bff;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
}

.btn-icon {
  background: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-icon:hover {
  background: #007bff;
  color: white;
}

.section-header {
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #495057;
}

.divider {
  height: 1px;
  background: #e9ecef;
  margin: 20px 0;
}
</style>