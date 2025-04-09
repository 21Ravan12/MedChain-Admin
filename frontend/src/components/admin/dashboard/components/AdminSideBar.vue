<template>
  <div class="admin-sidebar" :class="{ collapsed: collapsed }">
    <div class="sidebar-header">
      <div v-if="!collapsed" class="logo-container">
        <i class="fas fa-shield-alt logo-icon"></i>
        <h3>MedChain Admin</h3>
      </div>
      <i v-else class="fas fa-shield-alt logo-icon collapsed"></i>
    </div>
    
    <div class="sidebar-scroll">
      <ul class="sidebar-menu">
        <li>
          <router-link to="/admin/dashboard" class="menu-item" active-class="active">
            <i class="fas fa-tachometer-alt"></i>
            <span v-if="!collapsed">Dashboard</span>
            <div v-if="!collapsed" class="menu-tooltip"></div>
          </router-link>
        </li>
        
        <!-- Verification Section -->
        <li class="menu-section">
          <template v-if="!collapsed">
            <span>Verification</span>
            <i class="fas fa-chevron-down"></i>
          </template>
          <i v-else class="fas fa-user-check"></i>
        </li>
        <li>
          <router-link to="/admin/verify/doctors" class="menu-item" active-class="active">
            <i class="fas fa-user-md"></i>
            <span v-if="!collapsed">Doctors</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.doctors.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Doctors</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/hospitals" class="menu-item" active-class="active">
            <i class="fas fa-hospital"></i>
            <span v-if="!collapsed">Hospitals</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.hospitals.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Hospitals</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/hospitals/admins" class="menu-item" active-class="active">
            <i class="fas fa-shield-alt"></i>
            <span v-if="!collapsed">Hospital Admins</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.hospital_admins.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Hospital Admins</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/pharmacies" class="menu-item" active-class="active">
            <i class="fas fa-prescription-bottle-alt"></i>
            <span v-if="!collapsed">Pharmacies</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.pharmacies.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Pharmacies</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/pharmacies/admins" class="menu-item" active-class="active">
            <i class="fas fa-user-cog"></i>
            <span v-if="!collapsed">Pharmacy Admins</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.pharmacy_admins.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Pharmacy Admins</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/pharmacists" class="menu-item" active-class="active">
            <i class="fas fa-user-nurse"></i> 
            <span v-if="!collapsed">Pharmacists</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.pharmacists.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Pharmacists</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/patients" class="menu-item" active-class="active">
            <i class="fas fa-procedures"></i>
            <span v-if="!collapsed">Patients</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.patients.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Patients</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/verify/admins" class="menu-item" active-class="active">
            <i class="fas fa-shield-alt"></i>
            <span v-if="!collapsed">Admins</span>
            <span v-if="!collapsed" class="badge">{{ stats.verification_stats.admins.unverified }}</span>
            <div class="menu-tooltip" v-if="collapsed">Admins</div>
          </router-link>
        </li>
        
        <!-- Complaints Section -->
        <li class="menu-section">
          <template v-if="!collapsed">
            <span>Complaints</span>
            <i class="fas fa-chevron-down"></i>
          </template>
          <i v-else class="fas fa-exclamation-triangle"></i>
        </li>
        <li>
          <router-link to="/admin/complaints" class="menu-item" active-class="active">
            <i class="fas fa-comment-dots"></i>
            <span v-if="!collapsed">All Complaints</span>
            <span v-if="!collapsed" class="badge danger">{{ stats.unresolvedComplaints }}</span>
            <div class="menu-tooltip" v-if="collapsed">Complaints</div>
          </router-link>
        </li>
        
        <!-- Additional Menu Items -->
        <li class="menu-section">
          <template v-if="!collapsed">
            <span>Management</span>
            <i class="fas fa-chevron-down"></i>
          </template>
          <i v-else class="fas fa-cog"></i>
        </li>
        <li>
          <router-link to="/admin/users" class="menu-item" active-class="active">
            <i class="fas fa-users-cog"></i>
            <span v-if="!collapsed">User Management</span>
            <div class="menu-tooltip" v-if="collapsed">Users</div>
          </router-link>
        </li>
        <li>
          <router-link to="/admin/blockchain" class="menu-item" active-class="active">
            <i class="fas fa-link"></i>
            <span v-if="!collapsed">Blockchain</span>
            <div class="menu-tooltip" v-if="collapsed">Blockchain</div>
          </router-link>
        </li>
      </ul>
    </div>
    
    <div class="sidebar-footer" @click="$emit('toggle-collapse')">
      <i :class="collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      <span v-if="!collapsed">Collapse Menu</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    collapsed: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      stats: {
        verification_stats: {
          approved_total: 0,
          unverified_total: 0,
          admins: {
            approved: 0,
            unverified: 0
          },
          patients: {
            approved: 0,
            unverified: 0
          },
          hospitals: {
            approved: 0,
            unverified: 0
          },
          pharmacies: {
            approved: 0,
            unverified: 0
          },
          doctors: {
            approved: 0,
            unverified: 0
          },
          pharmacists: {
            approved: 0,
            unverified: 0
          },
          hospital_admins: {
            approved: 0,
            unverified: 0
          },
          pharmacy_admins: {
            approved: 0,
            unverified: 0
          },
          error: null
        },
        unresolvedComplaints: 0,
        blockchainStatus: 'Checking...'
      }
    }
  },
  methods: {
    async fetchCounts() {
      this.loading = true;
      this.error = null;
      
      try {
        const statsResponse = await this.$store.dispatch('admin/fetchDashboardStats');
        
        if (statsResponse.data?.verification_stats) {
          this.stats.verification_stats = statsResponse.data.verification_stats;
        }
        
        if (statsResponse.data?.unresolvedComplaints !== undefined) {
          this.stats.unresolvedComplaints = statsResponse.data.unresolvedComplaints;
        }
        
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        this.error = err.message || 'Failed to load dashboard data';
        
        if (process.env.NODE_ENV === 'development') {
          console.warn('Using placeholder data due to error');
          this.stats = {
            verification_stats: {
              approved_total: 152,
              unverified_total: 48,
              admins: {
                approved: 5,
                unverified: 3
              },
              patients: {
                approved: 45,
                unverified: 15
              },
              hospitals: {
                approved: 12,
                unverified: 5
              },
              pharmacies: {
                approved: 18,
                unverified: 8
              },
              doctors: {
                approved: 42,
                unverified: 12
              },
              pharmacists: {
                approved: 15,
                unverified: 3
              },
              hospital_admins: {
                approved: 8,
                unverified: 2
              },
              pharmacy_admins: {
                approved: 7,
                unverified: 0
              },
              error: null
            },
            unresolvedComplaints: 7,
            blockchainStatus: 'Healthy (mock)'
          };
        }
      } finally {
        this.loading = false;
      }
    }
  },
  created() {
    this.fetchCounts();
    
    this.refreshInterval = setInterval(() => {
      if (!document.hidden) { 
        this.fetchCounts();
      }
    }, 300000); // Refresh every 5 minutes
  },
  beforeDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
}
</script>

<style scoped>
@import '@fortawesome/fontawesome-free/css/all.min.css';

.admin-sidebar {
  width: 240px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background: white;
  color: #2d6a4f;
  transition: width 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e8f0eb;
  box-shadow: 2px 0 10px rgba(46, 106, 79, 0.05);
}

.admin-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e8f0eb;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70px;
  flex-shrink: 0;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
  color: #2d6a4f;
}

.logo-icon.collapsed {
  font-size: 28px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2d6a4f;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 15px 0;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #5e6e66;
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:hover {
  background: #f1f8f5;
  color: #2d6a4f;
}

.menu-item.active {
  background: #e8f5f0;
  color: #2d6a4f;
  border-left: 4px solid #2d6a4f;
}

.menu-item i {
  font-size: 16px;
  margin-right: 15px;
  color: #7b8a82;
  transition: all 0.2s ease;
  width: 20px;
  text-align: center;
}

.menu-item:hover i,
.menu-item.active i {
  color: #2d6a4f;
}

.admin-sidebar.collapsed .menu-item i {
  margin-right: 0;
  font-size: 18px;
}

.menu-item span {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.menu-tooltip {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: #2d6a4f;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 100;
  margin-left: 15px;
}

.menu-tooltip::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-right: 5px solid #2d6a4f;
}

.admin-sidebar.collapsed .menu-item:hover .menu-tooltip {
  opacity: 1;
  visibility: visible;
  margin-left: 20px;
}

.badge {
  margin-left: auto;
  background: #52b788;
  color: white;
  border-radius: 10px;
  max-width: 50px;
  padding: 3px 0px;
  font-size: 11px;
  font-weight: 600;
  text-align: center;
}

.badge.danger {
  background: #e76f51;
}

.menu-section {
  padding: 10px 20px;
  font-size: 12px;
  text-transform: uppercase;
  color: #7b8a82;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-section:hover {
  color: #2d6a4f;
}

.menu-section i {
  font-size: 12px;
  color: #b8c7ce;
  margin-right: 9.5px;
}

.admin-sidebar.collapsed .menu-section {
  justify-content: center;
  padding: 15px 0;
}

.admin-sidebar.collapsed .menu-section i {
  font-size: 18px;
  color: #7b8a82;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #e8f0eb;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #7b8a82;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.sidebar-footer:hover {
  color: #2d6a4f;
  background: #f1f8f5;
}

.sidebar-footer i {
  font-size: 16px;
}

.sidebar-footer span {
  font-size: 13px;
  font-weight: 500;
}

.admin-sidebar.collapsed .sidebar-footer span {
  display: none;
}

/* Scrollbar styling */
.sidebar-scroll::-webkit-scrollbar {
  width: 6px;
}

.sidebar-scroll::-webkit-scrollbar-track {
  background: #f1f8f5;
}

.sidebar-scroll::-webkit-scrollbar-thumb {
  background: #b8c7ce;
  border-radius: 3px;
}

.sidebar-scroll::-webkit-scrollbar-thumb:hover {
  background: #7b8a82;
}
</style>