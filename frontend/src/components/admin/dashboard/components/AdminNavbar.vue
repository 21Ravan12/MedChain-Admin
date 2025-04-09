<template>
  <nav class="admin-navbar">
    <button class="sidebar-toggle" @click="$emit('toggle-sidebar')">
      <i class="icon-menu"></i>
    </button>
    
    <div class="navbar-right">
      <div class="notifications" @click="toggleNotifications">
        <i class="icon-bell"></i>
        <span class="badge" v-if="unreadNotifications > 0">{{ unreadNotifications }}</span>
        <transition name="fade-slide">
          <div class="notification-dropdown" v-if="showNotifications" v-click-outside="closeNotifications">
            <div class="notification-header">
              <h4>Notifications</h4>
              <span class="mark-read" @click.stop="markAllAsRead">Mark all as read</span>
            </div>
            <div class="notification-list">
              <template v-if="loadingNotifications">
                <div class="notification-loading">
                  <i class="icon-loader spin"></i> Loading notifications...
                </div>
              </template>
              <template v-else>
                <div 
                  class="notification-item" 
                  v-for="notification in notifications" 
                  :key="notification.id"
                  :class="{ 'unread': !notification.read }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-icon" :class="notification.type">
                    <i :class="notificationIcon(notification.type)"></i>
                  </div>
                  <div class="notification-content">
                    <p>{{ notification.message }}</p>
                    <span class="notification-time">{{ formatTime(notification.time) }}</span>
                  </div>
                </div>
                <div class="empty-notifications" v-if="notifications.length === 0">
                  <i class="icon-bell-off"></i>
                  <p>No new notifications</p>
                </div>
              </template>
            </div>
            <router-link to="/admin/notifications" class="view-all" @click.native="showNotifications = false">
              View All Notifications
            </router-link>
          </div>
        </transition>
      </div>
      
      <div class="admin-profile" @click="toggleProfileDropdown">
        <template v-if="loadingProfile">
          <div class="avatar-loading"></div>
        </template>
        <template v-else>
          <img 
            :src="user.avatar" 
            alt="Admin Avatar" 
            class="avatar" 
            @error="handleImageError"
          >
          <span class="admin-name">{{ user.name }}</span>
          <i class="icon-chevron-down" :class="{ 'rotate': showProfileDropdown }"></i>
          <transition name="fade-slide">
            <div class="profile-dropdown" v-if="showProfileDropdown" v-click-outside="closeProfileDropdown">
              <div class="profile-info">
                <img 
                  :src="user.avatar" 
                  alt="Admin Avatar" 
                  class="dropdown-avatar"
                  @error="handleImageError"
                >
                <div class="profile-text">
                  <h4>{{ user.name }}</h4>
                  <p>{{ user.role }}</p>
                  <span class="profile-email">{{ user.email }}</span>
                </div>
              </div>
              <div class="dropdown-menu">
                <router-link 
                  to="/admin/profile" 
                  class="dropdown-item"
                  @click.native="showProfileDropdown = false"
                >
                  <i class="icon-user"></i> My Profile
                </router-link>
                <router-link 
                  to="/admin/settings" 
                  class="dropdown-item"
                  @click.native="showProfileDropdown = false"
                >
                  <i class="icon-settings"></i> Settings
                </router-link>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout" @click="logout">
                  <i class="icon-logout"></i> Logout
                </button>
              </div>
            </div>
          </transition>
        </template>
      </div>
    </div>
  </nav>
</template>

<script>
import admin from '@/store/modules/admin';

export default {
  data() {
    return {
      user: {
        name: '',
        avatar: '',
        role: '',
        email: ''
      },
      showNotifications: false,
      showProfileDropdown: false,
      loadingProfile: true,
      loadingNotifications: false,
      notifications: [],
      defaultAvatar: '/images/default-avatar.png',
      error: null
    };
  },
  computed: {
    unreadNotifications() {
      return this.notifications.filter(n => !n.read).length;
    }
  },
  methods: {
    async fetchProfileData() {
  this.loadingProfile = true;
  try {
    const response = await this.$store.dispatch('admin/fetchProfile');

    const adminProfileImageString = response.data.admin_profile.profile_image;
    const correctedString = adminProfileImageString.replace(/'/g, '"');
    const adminProfileImage = JSON.parse(correctedString);    

    let avatarData = adminProfileImage 
      ? adminProfileImage.data
      : this.defaultAvatar;

    this.user = {
      name: response.data.admin_profile.name || 'Admin User',
      avatar: avatarData || this.defaultAvatar,
      role: response.data.admin_profile.role || 'Administrator',
      email: response.data.admin_profile.email || ''
    };
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    this.error = error.message || 'Failed to load profile data';
    this.user = {
      name: 'Admin User',
      avatar: this.defaultAvatar,
      role: 'Administrator',
      email: ''
    };
  } finally {
    this.loadingProfile = false;
  }

    },
    async fetchNotifications() {
      this.loadingNotifications = true;
      try {
        const response = await this.$store.dispatch('notifications/fetch');
        this.notifications = response.data.map(notification => ({
          id: notification.id,
          message: notification.message,
          type: notification.type || 'info',
          time: new Date(notification.created_at),
          read: notification.read,
          route: notification.route || null
        }));
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
        this.notifications = [
          {
            id: 1,
            message: 'New doctor registration approved',
            type: 'success',
            time: new Date(Date.now() - 120000),
            read: false,
            route: '/admin/verify/doctors'
          }
        ];
      } finally {
        this.loadingNotifications = false;
      }
    },

    toggleNotifications() {
      this.showNotifications = !this.showNotifications;
      this.showProfileDropdown = false;
      if (this.showNotifications && this.notifications.length === 0) {
        this.fetchNotifications();
      }
    },

    toggleProfileDropdown() {
      this.showProfileDropdown = !this.showProfileDropdown;
      this.showNotifications = false;
    },

    async markAsRead() {
      try {
        await this.$store.dispatch('notifications/markAsRead');
        this.notifications = this.notifications.map(n => ({ ...n, read: true }));
      } catch (error) {
        console.error('Failed to mark notifications as read:', error);
      }
    },

    async markAllAsRead() {
      try {
        await this.$store.dispatch('notifications/markAllAsRead');
        this.notifications = this.notifications.map(n => ({ ...n, read: true }));
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error);
      }
    },

    handleNotificationClick(notification) {
      if (notification.route) {
        this.$router.push(notification.route);
      }
      this.showNotifications = false;
      if (!notification.read) {
        this.$store.dispatch('notifications/markAsRead', notification.id);
        notification.read = true;
      }
    },

    notificationIcon(type) {
      const icons = {
        success: 'icon-check',
        warning: 'icon-alert',
        error: 'icon-x',
        info: 'icon-info'
      };
      return icons[type] || 'icon-bell';
    },

    formatTime(date) {
      const seconds = Math.floor((new Date() - date) / 1000);
      if (seconds < 60) return `${seconds} seconds ago`;
      if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
      if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
      return `${Math.floor(seconds / 86400)} days ago`;
    },

    handleImageError(e) {
      e.target.src = this.defaultAvatar;
    },

    async logout() {
      try {
        await this.$store.dispatch('auth/logout');
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout failed:', error);
        this.$notify({
          type: 'error',
          title: 'Logout Error',
          text: 'Failed to logout. Please try again.'
        });
      }
    },

    setupRealTimeNotifications() {
      if (this.$cable) {
        this.notificationChannel = this.$cable.subscriptions.create(
          'NotificationsChannel',
          {
            received: (data) => {
              this.notifications.unshift({
                id: data.id,
                message: data.message,
                type: data.type || 'info',
                time: new Date(),
                read: false,
                route: data.route
              });
            }
          }
        );
      } else {
        this.notificationInterval = setInterval(() => {
          //this.fetchNotifications();
        }, 60000); 
      }
    }
  },
  async created() {
    await this.fetchProfileData();
    this.profileUpdateInterval = setInterval(() => {
      //this.fetchProfileData();
    }, 300000); // Every 5 minutes
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!this.$el.contains(e.target)) {
        this.showNotifications = false;
        this.showProfileDropdown = false;
      }
    });
    this.setupRealTimeNotifications();
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside);
    clearInterval(this.profileUpdateInterval);
    if (this.notificationChannel) {
      this.notificationChannel.unsubscribe();
    }
    if (this.notificationInterval) {
      clearInterval(this.notificationInterval);
    }
  }
};
</script>

<style scoped>
.admin-navbar {
  height: 70px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 25px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  border-bottom: 1px solid #f0f2f5;
}

.sidebar-toggle {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #4a6b57;
  padding: 10px;
  transition: all 0.2s ease;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-toggle:hover {
  background: #f5f7fa;
  color: #3a8d6e;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notifications {
  position: relative;
  cursor: pointer;
  color: #5e6e66;
  transition: all 0.2s ease;
  padding: 8px;
  border-radius: 6px;
  height: 40px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notifications:hover {
  color: #3a8d6e;
  background: #f5f7fa;
}

.notifications i {
  font-size: 20px;
}

.notifications .badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border: 2px solid white;
}

.notification-dropdown {
  position: absolute;
  top: 50px;
  right: 0;
  width: 360px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 0;
  z-index: 1100;
  border: 1px solid #f0f2f5;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
}

.notification-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.mark-read {
  color: #3a8d6e;
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

.mark-read:hover {
  color: #2d6a4f;
}

.notification-list {
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 14px 20px;
  transition: all 0.2s ease;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
}

.notification-item.unread {
  background-color: #f8faf7;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
  font-size: 18px;
}

.notification-icon.success {
  background: #e6f7ed;
  color: #28a745;
}

.notification-icon.warning {
  background: #fff8e6;
  color: #ffc107;
}

.notification-icon.error {
  background: #ffebee;
  color: #dc3545;
}

.notification-icon.info {
  background: #e7f5ff;
  color: #17a2b8;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-content p {
  margin: 0 0 4px;
  color: #2d3748;
  font-size: 14px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 12px;
  color: #718096;
  display: block;
}

.view-all {
  display: block;
  text-align: center;
  padding: 12px;
  color: #3a8d6e;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  border-top: 1px solid #f0f2f5;
  transition: background 0.2s;
}

.view-all:hover {
  background: #f5f7fa;
  text-decoration: none;
}

.empty-notifications {
  padding: 30px 20px;
  text-align: center;
  color: #a0aec0;
}

.empty-notifications i {
  font-size: 24px;
  margin-bottom: 10px;
  display: block;
  color: #cbd5e0;
}

.empty-notifications p {
  margin: 0;
  font-size: 14px;
}

.admin-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
  padding: 6px 10px;
  border-radius: 8px;
  transition: all 0.2s ease;
  height: 40px;
}

.admin-profile:hover {
  background: #f5f7fa;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f2f5;
}

.dropdown-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0f2f5;
}

.admin-name {
  font-weight: 500;
  color: #2d3748;
  font-size: 14px;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-profile i {
  color: #a0aec0;
  font-size: 14px;
  transition: all 0.2s ease;
}

.admin-profile i.rotate {
  transform: rotate(180deg);
}

.profile-dropdown {
  position: absolute;
  top: 56px;
  right: 0;
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 0;
  z-index: 1100;
  border: 1px solid #f0f2f5;
  overflow: hidden;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  text-align: center;
  background: linear-gradient(to right, #f8faf7, #ffffff);
  border-bottom: 1px solid #f0f2f5;
}

.profile-text {
  margin-top: 12px;
}

.profile-text h4 {
  margin: 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.profile-text p {
  margin: 4px 0 0;
  color: #4a5568;
  font-size: 13px;
}

.profile-email {
  display: block;
  color: #718096;
  font-size: 12px;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.dropdown-menu {
  padding: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  color: #4a5568;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dropdown-item i {
  margin-right: 12px;
  font-size: 16px;
  color: #a0aec0;
  width: 20px;
  text-align: center;
}

.dropdown-item:hover {
  background: #f5f7fa;
  color: #3a8d6e;
}

.dropdown-item:hover i {
  color: #3a8d6e;
}

.dropdown-divider {
  height: 1px;
  background: #f0f2f5;
  margin: 8px 0;
}

.logout {
  color: #e53e3e;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
}

.logout:hover {
  background: #fff5f5;
  color: #e53e3e;
}

.logout i {
  color: #e53e3e;
}

/* Animations */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Loading states */
.avatar-loading {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f2f5;
  animation: pulse 1.5s infinite;
}

.notification-loading {
  padding: 20px;
  text-align: center;
  color: #a0aec0;
  font-size: 13px;
}

.notification-loading i {
  margin-right: 8px;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style> 