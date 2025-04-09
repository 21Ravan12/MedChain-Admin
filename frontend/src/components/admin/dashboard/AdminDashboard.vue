<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <AdminSidebar 
      :collapsed="isSidebarCollapsed" 
      @toggle-collapse="toggleSidebar"
    />
    
    <div class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="dashboard-container">
        <div class="dashboard-header">
          <h1>MedChain Admin Dashboard</h1>
          <div class="welcome-message">
            <span>Welcome back, <strong>Admin</strong></span>
            <span class="current-date">{{ currentDate }}</span>
          </div>
        </div>

        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>

        <div v-if="error" class="error-message">
          <p>⚠️ Error loading dashboard data: {{ error }}</p>
          <button @click="fetchDashboardData" class="retry-button">Retry</button>
        </div>
        
        <!-- Summary Cards -->
        <div class="summary-cards" v-if="!loading && !error">
          <DashboardCard 
            title="Pending Verifications" 
            :value="totalPendingVerifications" 
            icon="verified" 
            color="primary"
            route="/admin/verify/doctors"
            :loading="loading"
          />
          <DashboardCard 
            title="Unresolved Complaints" 
            :value="dashboardStats.unresolvedComplaints" 
            icon="alert" 
            color="secondary"
            route="/admin/complaints"
            :loading="loading"
          />
          <DashboardCard 
            title="Total Users" 
            :value="dashboardStats.verification_stats.approved_total" 
            icon="users" 
            color="accent"
            :loading="loading"
          />
          <DashboardCard 
            title="Blockchain Health" 
            :value="dashboardStats.blockchainStatus" 
            icon="link" 
            color="success"
            :loading="loading"
          />
        </div>
        
        <!-- Recent Activity and Verification Queue -->
        <div class="dashboard-grid" v-if="!loading && !error">
          <div class="recent-activity">
            <div class="section-header">
              <h2>Recent Activity</h2>
              <router-link to="/admin/activity" class="view-all">View All</router-link>
            </div>
            <ActivityFeed 
              :activities="recentActivities" 
              :loading="loading"
            />
          </div>
          
          <div class="verification-queue">
            <div class="section-header">
              <h2>Verification Queue</h2>
              <router-link to="/admin/verify" class="view-all">View All</router-link>
            </div>
            <VerificationQueue 
              :pendingDoctors="dashboardStats.pendingDoctors"
              :pendingHospitals="dashboardStats.pendingHospitals"
              :pendingPharmacies="dashboardStats.pendingPharmacies"
              :pendingPatients="dashboardStats.pendingPatients"
              @navigate="navigateToVerification"
              :loading="loading"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';
import DashboardCard from '@/components/admin/dashboard/components/DashboardCard.vue';
import ActivityFeed from '@/components/admin/dashboard/components/ActivityFeed.vue';
import VerificationQueue from '@/components/admin/dashboard/components/VerificationQueue.vue';

export default {
  components: {
    AdminNavbar,
    AdminSidebar,
    DashboardCard,
    ActivityFeed,
    VerificationQueue
  },
  data() {
    return {
      isSidebarCollapsed: false,
      loading: false,
      error: null,
      dashboardStats: {
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
      },
      recentActivities: [],
    };
  },
  computed: {
    totalPendingVerifications() {
      return this.dashboardStats.verification_stats?.unverified_total || 0;
    },
    totalApprovedUsers() {
      return this.dashboardStats.verification_stats?.approved_total || 0;
    },
    currentDate() {
      return new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    }
  },
  methods: {
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    navigateToVerification(type) {
      this.$router.push(`/admin/verify/${type}`);
    },
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      
      try {
        const statsResponse = await this.$store.dispatch('admin/fetchDashboardStats');
        
        if (statsResponse.data?.verification_stats) {
          this.dashboardStats = {
            verification_stats: {
              approved_total: statsResponse.data?.verification_stats?.approved_total || 0,
              unverified_total: statsResponse.data?.verification_stats?.unverified_total || 0,
              admins: {
                approved: statsResponse.data?.verification_stats?.admins?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.admins?.unverified || 0
              },
              patients: {
                approved: statsResponse.data?.verification_stats?.patients?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.patients?.unverified || 0
              },
              hospitals: {
                approved: statsResponse.data?.verification_stats?.hospitals?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.hospitals?.unverified || 0
              },
              pharmacies: {
                approved: statsResponse.data?.verification_stats?.pharmacies?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.pharmacies?.unverified || 0
              },
              doctors: {
                approved: statsResponse.data?.verification_stats?.doctors?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.doctors?.unverified || 0
              },
              pharmacists: {
                approved: statsResponse.data?.verification_stats?.pharmacists?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.pharmacists?.unverified || 0
              },
              hospital_admins: {
                approved: statsResponse.data?.verification_stats?.hospital_admins?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.hospital_admins?.unverified || 0
              },
              pharmacy_admins: {
                approved: statsResponse.data?.verification_stats?.pharmacy_admins?.approved || 0,
                unverified: statsResponse.data?.verification_stats?.pharmacy_admins?.unverified || 0
              },
              error: null
            },
            unresolvedComplaints: 7,
            blockchainStatus: 'Healthy (mock)'
          };
        }
        
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        this.error = err.message || 'Failed to load dashboard data';
        
        if (process.env.NODE_ENV === 'development') {
          console.warn('Using placeholder data due to error');
          this.dashboardStats = {
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
          this.recentActivities = [
            {
              id: 1,
              user: 'Dr. Smith',
              action: 'Registration submitted',
              time: '10 minutes ago',
              type: 'doctor'
            },
            {
              id: 2,
              user: 'General Hospital',
              action: 'Verification requested',
              time: '45 minutes ago',
              type: 'hospital'
            }
          ];
        }
      } finally {
        this.loading = false;
      }
    }
  },
  created() {
    this.fetchDashboardData();
    
    this.refreshInterval = setInterval(() => {
      if (!document.hidden) { 
        this.fetchDashboardData();
      }
    }, 300000); // Refresh every 5 minutes
  },
  beforeDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8faf7;
}

.admin-content {
  margin-left: 240px;
  padding: 30px;
  transition: margin-left 0.3s ease;
  flex: 1;
  background-color: #f8faf7;
  position: relative;
}

.admin-content.collapsed {
  margin-left: 80px;
}

.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
  margin-top: 80px;
}

.dashboard-header h1 {
  color: #2d6a4f;
  font-size: 2rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.welcome-message {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #5e6e66;
}

.welcome-message strong {
  color: #2d6a4f;
  font-weight: 500;
}

.current-date {
  font-size: 0.9rem;
  color: #7b8a82;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2px;
  margin-bottom: 60px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.recent-activity, .verification-queue {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(46, 106, 79, 0.08);
  border: 1px solid #e8f0eb;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h2 {
  margin: 0;
  color: #2d6a4f;
  font-size: 1.3rem;
  font-weight: 500;
}

.view-all {
  color: #40916c;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.view-all:hover {
  color: #2d6a4f;
  text-decoration: underline;
}

@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .admin-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .admin-content {
    margin-left: 0;
    padding-bottom: 80px;
  }
  
  .admin-content.collapsed {
    margin-left: 0;
  }
  
  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 576px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 1.5rem;
  }
}
</style>