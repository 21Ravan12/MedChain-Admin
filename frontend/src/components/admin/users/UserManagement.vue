<template>
  <div class="admin-layout">
    <AdminNavbar @toggle-sidebar="toggleSidebar" />
    <div class="admin-container">
      <AdminSidebar 
        :collapsed="isSidebarCollapsed" 
        @toggle-collapse="toggleSidebar"
      />
      <main class="admin-content" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="user-management">
          <div class="page-header">
            <div class="header-title">
              <i class="fas fa-users-cog header-icon"></i>
              <h1>User Management</h1>
              <span class="badge">{{ totalUsers }}</span>
              <span class="filter-indicator" v-if="filterRole !== 'all' || searchQuery">
                <i class="fas fa-filter"></i> Filters applied
                <button class="btn btn-link btn-sm" @click="resetFilters">Reset</button>
              </span>
            </div>
            <div class="header-controls">
              <div class="search-filter">
                <i class="fas fa-search"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search users..."
                  @input="debounceSearch"
                  aria-label="Search users"
                >
                <button 
                  v-if="searchQuery" 
                  class="btn btn-icon btn-clear" 
                  @click="searchQuery = ''; searchUsers()"
                  aria-label="Clear search"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="select-wrapper">
                <select 
                  v-model="filterRole" 
                  class="role-filter" 
                  @change="filterUsers"
                  aria-label="Filter by role"
                >
                  <option value="all">All Roles</option>
                  <option value="admin">Admin</option>
                  <option value="doctor">Doctor</option>
                  <option value="pharmacist">Pharmacist</option>
                  <option value="patient">Patient</option>
                </select>
                <i class="fas fa-chevron-down"></i>
              </div>
              <button 
                class="btn btn-primary btn-add-user" 
                @click="showAddUserModal"
                aria-label="Add new user"
              >
                <i class="fas fa-plus"></i> Add User
              </button>
              <button 
                class="btn btn-outline-secondary btn-reset-filters" 
                @click="confirmResetFilters"
                aria-label="Reset filters"
              >
                <i class="fas fa-redo"></i> Reset
              </button>
            </div>
          </div>
          
          <div class="card">
            <div class="card-header" v-if="filteredUsers.length > 0">
              <div class="results-count">
                Showing {{ rangeStart }}-{{ rangeEnd }} of {{ totalUsers }} users
                <span v-if="filterRole !== 'all' || searchQuery">(Filtered: {{ filteredUsers.length }})</span>
              </div>
              <div class="table-actions">
                <button 
                  class="btn btn-icon btn-sm" 
                  @click="exportToCSV"
                  title="Export to CSV"
                >
                  <i class="fas fa-file-export"></i>
                </button>
                <button 
                  class="btn btn-icon btn-sm" 
                  @click="refreshData"
                  title="Refresh data"
                >
                  <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
                </button>
              </div>
            </div>
            
            <div class="table-responsive">
              <table class="users-table" aria-label="User management table">
                <thead>
                  <tr>
                    <th @click="sortBy('id')">
                      ID <i class="fas" :class="sortIcon('id')"></i>
                    </th>
                    <th @click="sortBy('name')">
                      User <i class="fas" :class="sortIcon('name')"></i>
                    </th>
                    <th @click="sortBy('email')">
                      Email <i class="fas" :class="sortIcon('email')"></i>
                    </th>
                    <th @click="sortBy('role')">
                      Role <i class="fas" :class="sortIcon('role')"></i>
                    </th>
                    <th @click="sortBy('status')">
                      Status <i class="fas" :class="sortIcon('status')"></i>
                    </th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in paginatedUsers" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>
                      <router-link :to="`/admin/users/${user.id}`" class="user-info">
                        <img 
                          :src="user.avatar || defaultAvatar" 
                          :alt="`Avatar of ${user.name}`" 
                          class="user-avatar"
                          loading="lazy"
                        >
                        <span>{{ user.name }}</span>
                        <i 
                          v-if="user.role === 'admin'" 
                          class="fas fa-shield-alt admin-badge" 
                          title="Administrator"
                        ></i>
                      </router-link>
                    </td>
                    <td>
                      <a :href="`mailto:${user.email}`">{{ user.email }}</a>
                    </td>
                    <td>
                      <span class="role-badge" :class="user.role">
                        {{ formatRole(user.role) }}
                      </span>
                    </td>
                    <td>
                      <span class="status-badge" :class="user.status">
                        <i :class="statusIcon(user.status)"></i>
                        {{ capitalizeFirstLetter(user.status) }}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          class="btn btn-icon btn-edit" 
                          @click="editUser(user.id)"
                          aria-label="Edit user"
                        >
                          <i class="fas fa-edit"></i>
                        </button>
                        <button 
                          class="btn btn-icon" 
                          :class="user.status === 'active' ? 'btn-warning' : 'btn-success'"
                          @click="toggleUserStatus(user.id)"
                          :aria-label="user.status === 'active' ? 'Deactivate user' : 'Activate user'"
                        >
                          <i :class="user.status === 'active' ? 'fas fa-user-slash' : 'fas fa-user-check'"></i>
                        </button>
                        <dropdown-menu>
                          <template #trigger>
                            <button class="btn btn-icon btn-more" aria-label="More actions">
                              <i class="fas fa-ellipsis-v"></i>
                            </button>
                          </template>
                          <dropdown-item @click="sendPasswordReset(user.id)">
                            <i class="fas fa-key"></i> Reset Password
                          </dropdown-item>
                          <dropdown-item @click="impersonateUser(user.id)" v-if="user.role !== 'admin'">
                            <i class="fas fa-user-secret"></i> Impersonate
                          </dropdown-item>
                          <dropdown-item @click="confirmDeleteUser(user.id)" class="danger">
                            <i class="fas fa-trash"></i> Delete
                          </dropdown-item>
                        </dropdown-menu>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="empty-state" v-if="filteredUsers.length === 0">
              <i class="fas fa-user-times"></i>
              <h3>No users found</h3>
              <p>Try adjusting your search or filter criteria</p>
              <button class="btn btn-primary" @click="resetFilters">
                Reset Filters
              </button>
            </div>
            
            <div class="card-footer" v-if="totalPages > 1">
              <div class="pagination-info">
                Showing {{ rangeStart }}-{{ rangeEnd }} of {{ totalFilteredUsers }} results
              </div>
              <div class="pagination-controls">
                <select 
                  v-model="itemsPerPage" 
                  @change="changeItemsPerPage"
                  class="items-per-page"
                  aria-label="Items per page"
                >
                  <option value="5">5 per page</option>
                  <option value="10">10 per page</option>
                  <option value="25">25 per page</option>
                  <option value="50">50 per page</option>
                </select>
                <button 
                  class="btn btn-icon" 
                  :disabled="currentPage === 1"
                  @click="changePage(1)"
                  aria-label="First page"
                >
                  <i class="fas fa-angle-double-left"></i>
                </button>
                <button 
                  class="btn btn-icon" 
                  :disabled="currentPage === 1"
                  @click="changePage(currentPage - 1)"
                  aria-label="Previous page"
                >
                  <i class="fas fa-angle-left"></i>
                </button>
                <div class="page-numbers">
                  <button 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="btn btn-icon"
                    :class="{ 'active': page === currentPage }"
                    @click="changePage(page)"
                    :aria-label="`Page ${page}`"
                  >
                    {{ page }}
                  </button>
                </div>
                <button 
                  class="btn btn-icon" 
                  :disabled="currentPage === totalPages"
                  @click="changePage(currentPage + 1)"
                  aria-label="Next page"
                >
                  <i class="fas fa-angle-right"></i>
                </button>
                <button 
                  class="btn btn-icon" 
                  :disabled="currentPage === totalPages"
                  @click="changePage(totalPages)"
                  aria-label="Last page"
                >
                  <i class="fas fa-angle-double-right"></i>
                </button>
              </div>
            </div>
          </div>
          
          <AddUserModal 
            v-if="showAddModal" 
            @save="addUser" 
            @cancel="closeAddModal" 
          />
          
          <EditUserModal 
            v-if="selectedUser" 
            :user="selectedUser" 
            @save="updateUser" 
            @cancel="closeEditModal" 
          />
          
          <ConfirmationModal 
            v-if="showDeleteConfirmation" 
            title="Confirm User Deletion"
            :message="deleteConfirmationMessage"
            confirm-text="Delete User"
            cancel-text="Cancel"
            variant="danger"
            @confirm="deleteUser"
            @cancel="cancelDelete"
          />
        </div>
      </main>
    </div>
    
    <ToastNotifications />
  </div>
</template>

<script>
import AdminNavbar from '@/components/admin/dashboard/components/AdminNavbar.vue';
import AdminSidebar from '@/components/admin/dashboard/components/AdminSideBar.vue';
import debounce from 'lodash/debounce';
import AddUserModal from '@/components/admin/users/AddUserModal.vue';
import EditUserModal from '@/components/admin/users/EditUserModal.vue';
import ConfirmationModal from '@/components/admin/users/ConfirmationModal.vue';
import DropdownMenu from '@/components/admin/users/DropdownMenu.vue';
import DropdownItem from '@/components/admin/users/DropdownItem.vue';
import ToastNotifications from '@/components/admin/users/ToastNotifications.vue';

export default {
  components: {
    AdminNavbar,
    AdminSidebar,
    AddUserModal,
    EditUserModal,
    ConfirmationModal,
    DropdownMenu,
    DropdownItem,
    ToastNotifications
  },
  data() {
    return {
      users: [],
      searchQuery: '',
      filterRole: 'all',
      currentPage: 1,
      itemsPerPage: 10,
      showAddModal: false,
      selectedUser: null,
      showDeleteConfirmation: false,
      userToDelete: null,
      isSidebarCollapsed: false,
      defaultAvatar: '/images/avatars/default-user.png',
      sortField: 'id',
      sortDirection: 'asc',
      isRefreshing: false,
      isLoading: false,
      error: null
    }
  },
  computed: {
    filteredUsers() {
      let filtered = this.users;
      
      if (this.filterRole !== 'all') {
        filtered = filtered.filter(user => user.role === this.filterRole);
      }
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(user => 
          user.name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          user.id.toString().includes(query)
        );
      }
      
      return filtered.sort((a, b) => {
        let modifier = this.sortDirection === 'desc' ? -1 : 1;
        if (a[this.sortField] < b[this.sortField]) return -1 * modifier;
        if (a[this.sortField] > b[this.sortField]) return 1 * modifier;
        return 0;
      });
    },
    totalFilteredUsers() {
      return this.filteredUsers.length;
    },
    totalUsers() {
      return this.users.length;
    },
    totalPages() {
      return Math.ceil(this.totalFilteredUsers / this.itemsPerPage);
    },
    paginatedUsers() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredUsers.slice(start, end);
    },
    rangeStart() {
      return (this.currentPage - 1) * this.itemsPerPage + 1;
    },
    rangeEnd() {
      const end = this.currentPage * this.itemsPerPage;
      return end > this.totalFilteredUsers ? this.totalFilteredUsers : end;
    },
    visiblePages() {
      const range = [];
      const half = Math.floor(5 / 2);
      let start = this.currentPage - half;
      let end = this.currentPage + half;
      
      if (start < 1) {
        start = 1;
        end = 5;
      }
      
      if (end > this.totalPages) {
        end = this.totalPages;
        start = Math.max(1, end - 5 + 1);
      }
      
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    },
    deleteConfirmationMessage() {
      const user = this.users.find(u => u.id === this.userToDelete);
      return user ? `Are you sure you want to permanently delete ${user.name} (${user.email})?` : '';
    }
  },
  async created() {
    await this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await this.$store.dispatch('admin/fetchUsers', {
          page: this.currentPage,
          limit: this.itemsPerPage,
          role: this.filterRole !== 'all' ? this.filterRole : undefined,
          search: this.searchQuery || undefined,
          sortField: this.sortField,
          sortDirection: this.sortDirection
        });
        
        this.users = response.data.users;
        // If your API returns pagination info, you might want to use it:
        // this.totalUsers = response.data.total;
        // this.currentPage = response.data.currentPage;
        // this.itemsPerPage = response.data.perPage;
        
      } catch (error) {
        this.error = error.message || 'Failed to fetch users';
        this.$toast.error(this.error);
      } finally {
        this.isLoading = false;
      }
    },
    
    async refreshData() {
      this.isRefreshing = true;
      try {
        await this.fetchUsers();
        this.$toast.info('User data refreshed');
      } catch (error) {
        this.$toast.error('Failed to refresh data');
      } finally {
        this.isRefreshing = false;
      }
    },
    
    async addUser(newUser) {
      try {
        const response = await this.$store.dispatch('admin/addUser', newUser);
        this.users.unshift(response.data.user);
        this.$toast.success(`User ${newUser.name} added successfully`);
        this.closeAddModal();
      } catch (error) {
        this.$toast.error(error.message || 'Failed to add user');
      }
    },
    
    async updateUser(updatedUser) {
      try {
        const response = await this.$store.dispatch('admin/updateUser', {
          id: updatedUser.id,
          userData: updatedUser
        });
        
        const index = this.users.findIndex(user => user.id === updatedUser.id);
        if (index !== -1) {
          this.users.splice(index, 1, response.data.user);
          this.$toast.success('User updated successfully');
        }
        this.closeEditModal();
      } catch (error) {
        this.$toast.error(error.message || 'Failed to update user');
      }
    },
    
    async deleteUser() {
      try {
        await this.$store.dispatch('admin/deleteUser', this.userToDelete);
        this.users = this.users.filter(u => u.id !== this.userToDelete);
        
        const user = this.users.find(u => u.id === this.userToDelete);
        if (user) {
          this.$toast.success(`User ${user.name} deleted successfully`);
        }
        
        this.cancelDelete();
      } catch (error) {
        this.$toast.error(error.message || 'Failed to delete user');
      }
    },
    
    async toggleUserStatus(userId) {
      try {
        const user = this.users.find(user => user.id === userId);
        if (!user) return;
        
        const newStatus = user.status === 'active' ? 'inactive' : 'active';
        await this.$store.dispatch('admin/updateUserStatus', {
          id: userId,
          status: newStatus
        });
        
        user.status = newStatus;
        this.$toast.success(
          `User ${user.name} ${newStatus === 'active' ? 'activated' : 'deactivated'}`
        );
      } catch (error) {
        this.$toast.error(error.message || 'Failed to update user status');
      }
    },
    
    async sendPasswordReset(userId) {
      try {
        await this.$store.dispatch('admin/sendPasswordReset', userId);
        const user = this.users.find(u => u.id === userId);
        if (user) {
          this.$toast.info(`Password reset email sent to ${user.email}`);
        }
      } catch (error) {
        this.$toast.error(error.message || 'Failed to send password reset');
      }
    },
    
    async impersonateUser(userId) {
      try {
        await this.$store.dispatch('admin/impersonateUser', userId);
        const user = this.users.find(u => u.id === userId);
        if (user) {
          this.$toast.warning(`Impersonating ${user.name}`);
        }
      } catch (error) {
        this.$toast.error(error.message || 'Failed to impersonate user');
      }
    },

    // Other existing methods remain the same...
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    formatRole(role) {
      const roles = {
        admin: 'Administrator',
        doctor: 'Doctor',
        pharmacist: 'Pharmacist',
        patient: 'Patient'
      };
      return roles[role] || role;
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    statusIcon(status) {
      return {
        active: 'fas fa-check-circle',
        inactive: 'fas fa-times-circle',
        pending: 'fas fa-hourglass-half',
        suspended: 'fas fa-ban'
      }[status];
    },
    sortIcon(field) {
      if (this.sortField !== field) return 'fa-sort';
      return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },
    sortBy(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortDirection = 'asc';
      }
      this.fetchUsers();
    },
    debounceSearch: debounce(function() {
      this.searchUsers();
    }, 300),
    searchUsers() {
      this.currentPage = 1;
      this.fetchUsers();
    },
    filterUsers() {
      this.currentPage = 1;
      this.fetchUsers();
    },
    resetFilters() {
      this.searchQuery = '';
      this.filterRole = 'all';
      this.currentPage = 1;
      this.sortField = 'id';
      this.sortDirection = 'asc';
      this.fetchUsers();
      this.$toast.success('All filters have been reset');
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        this.fetchUsers();
      }
    },
    changeItemsPerPage() {
      this.currentPage = 1;
      this.fetchUsers();
    },
    showAddUserModal() {
      this.showAddModal = true;
    },
    closeAddModal() {
      this.showAddModal = false;
    },
    editUser(userId) {
      this.selectedUser = { ...this.users.find(user => user.id === userId) };
    },
    closeEditModal() {
      this.selectedUser = null;
    },
    confirmDeleteUser(userId) {
      this.userToDelete = userId;
      this.showDeleteConfirmation = true;
    },
    cancelDelete() {
      this.userToDelete = null;
      this.showDeleteConfirmation = false;
    },
    exportToCSV() {
      this.$toast.success('Export started. Download will begin shortly.');
    },
    confirmResetFilters() {
      this.$toast.info('Are you sure you want to reset all filters?', {
        action: {
          text: 'Confirm',
          onClick: () => this.resetFilters()
        }
      });
    }
  }
}
</script>

<style scoped>
:root {
  --primary: #4361ee;
  --primary-light: #5d75f0;
  --primary-dark: #3a56d4;
  --primary-transparent: rgba(67, 97, 238, 0.1);
  
  --secondary: #6c757d;
  --secondary-light: #7a8288;
  --secondary-dark: #5f686f;
  --secondary-transparent: rgba(108, 117, 125, 0.1);
  
  --success: #28a745;
  --success-light: #3eb356;
  --success-dark: #23903d;
  --success-transparent: rgba(40, 167, 69, 0.1);
  
  --danger: #dc3545;
  --danger-light: #e04a59;
  --danger-dark: #c82333;
  --danger-transparent: rgba(220, 53, 69, 0.1);
  
  --warning: #ffc107;
  --warning-light: #ffc927;
  --warning-dark: #e0a800;
  --warning-transparent: rgba(255, 193, 7, 0.1);
  
  --info: #17a2b8;
  --info-light: #2eafc4;
  --info-dark: #138496;
  --info-transparent: rgba(23, 162, 184, 0.1);
  
  --light: #f8f9fa;
  --dark: #343a40;
  --light-bg: #f8f9fa;
  --border-color: #e9ecef;
  --border-radius: 0.375rem;
  --transition-base: all 0.2s ease-in-out;
}

.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-container {
  display: flex;
  flex: 1;
  padding-top: 4rem;
}

.admin-content {
  flex: 1;
  padding: 1.5rem;
  margin-left: 16rem;
  transition: margin-left 0.3s ease;
}

.admin-content.collapsed {
  margin-left: 5rem;
}

@media (max-width: 991.98px) {
  .admin-content {
    margin-left: 5rem;
  }
}

.user-management {
  padding: 1.5rem;
}

.card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.card-header, .card-footer {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--light-bg);
  border-bottom: 1px solid var(--border-color);
}

.card-footer {
  border-top: 1px solid var(--border-color);
  border-bottom: none;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .page-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.header-title h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark);
}

.header-title .badge {
  background: var(--primary);
  color: white;
  border-radius: 50%;
  width: 1.75rem;
  height: 1.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-filter {
  position: relative;
  flex-grow: 1;
  min-width: 200px;
}

.search-filter i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary);
}

.search-filter input {
  padding: 0.5rem 2rem 0.5rem 2.25rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  width: 100%;
  transition: var(--transition-base);
}

.search-filter input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-transparent);
}

.select-wrapper {
  position: relative;
  min-width: 150px;
}

.select-wrapper select {
  appearance: none;
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  width: 100%;
  background-color: white;
  cursor: pointer;
}

.select-wrapper i {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-base);
  border: 1px solid transparent;
  border-radius: 5px;
}

.btn-primary {
  background-color: var(--primary);
  border-color: var(--primary);
}

.btn-primary:hover {
  background-color: var(--secondary);
  color: white;
}

.btn-outline-secondary {
  background-color: transparent;
  color: var(--secondary);
  border-color: var(--secondary);
}

.btn-outline-secondary:hover {
  background-color: var(--secondary);
  color: white;
}

.btn-add-user {
  white-space: nowrap;
}

.btn-reset-filters {
  white-space: nowrap;
}

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th, .users-table td {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.users-table th {
  background-color: var(--light-bg);
  font-weight: 600;
  cursor: pointer;
  position: relative;
}

.users-table th:hover {
  background-color: #f1f1f1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
}

.role-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.role-badge.admin {
  background-color: var(--primary-transparent);
  color: var(--primary-dark);
}

.role-badge.doctor {
  background-color: var(--success-transparent);
  color: var(--success-dark);
}

.role-badge.pharmacist {
  background-color: var(--info-transparent);
  color: var(--info-dark);
}

.role-badge.patient {
  background-color: var(--secondary-transparent);
  color: var(--secondary-dark);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.active {
  background-color: var(--success-transparent);
  color: var(--success);
}

.status-badge.inactive {
  background-color: var(--danger-transparent);
  color: var(--danger);
}

.status-badge.pending {
  background-color: var(--warning-transparent);
  color: var(--warning-dark);
}

.status-badge.suspended {
  background-color: var(--secondary-transparent);
  color: var(--secondary-dark);
}

.action-buttons {
  display: flex;
  gap: 0.375rem;
}

.btn-icon {
  width: 2rem;
  height: 2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition-base);
  background-color: transparent;
  border: none;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-edit {
  color: var(--primary);
}

.btn-warning {
  color: var(--warning-dark);
}

.btn-success {
  color: var(--success-dark);
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--secondary);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--secondary-light);
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: var(--dark);
}

.empty-state p {
  margin-bottom: 1.5rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-numbers button.active {
  background-color: var(--primary);
  color: white;
}

.items-per-page {
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
}

.filter-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--secondary);
  margin-left: 0.5rem;
}

.filter-indicator i {
  color: var(--primary);
}

.results-count {
  font-size: 0.875rem;
  color: var(--secondary);
}

.table-actions {
  display: flex;
  gap: 0.5rem;
}

.admin-badge {
  color: var(--primary);
  margin-left: 0.25rem;
  font-size: 0.75rem;
}

@media (max-width: 767.98px) {
  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filter,
  .select-wrapper,
  .btn-add-user,
  .btn-reset-filters {
    width: 100%;
  }
  
  .users-table {
    display: block;
  }
  
  .users-table thead {
    display: none;
  }
  
  .users-table tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
  }
  
  .users-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .users-table td:last-child {
    border-bottom: none;
  }
  
  .users-table td::before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 1rem;
    color: var(--secondary);
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}
</style>