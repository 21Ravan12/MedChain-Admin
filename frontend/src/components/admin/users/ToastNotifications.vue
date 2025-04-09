<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div 
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`toast-${toast.type}`"
        @click="removeToast(toast.id)"
      >
        <div class="toast-icon">
          <i :class="iconClass(toast.type)"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click.stop="removeToast(toast.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
let toastId = 0;

export default {
  name: 'ToastNotifications',
  data() {
    return {
      toasts: []
    }
  },
  methods: {
    addToast({ type = 'info', title, message, timeout = 5000 }) {
      const id = toastId++;
      const toast = { id, type, title, message };
      
      this.toasts.push(toast);
      
      if (timeout !== false) {
        setTimeout(() => {
          this.removeToast(id);
        }, timeout);
      }
      
      return id;
    },
    removeToast(id) {
      this.toasts = this.toasts.filter(toast => toast.id !== id);
    },
    iconClass(type) {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      };
      return icons[type] || icons.info;
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1100;
  width: 350px;
  max-width: 100%;
}

.toast {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.375rem;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.1);
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
  }
  
  &.toast-success::before {
    background-color: #28a745;
  }
  
  &.toast-error::before {
    background-color: #dc3545;
  }
  
  &.toast-warning::before {
    background-color: #ffc107;
  }
  
  &.toast-info::before {
    background-color: #17a2b8;
  }
}

.toast-icon {
  font-size: 1.25rem;
  margin-right: 1rem;
  flex-shrink: 0;
  
  .toast-success & {
    color: #28a745;
  }
  
  .toast-error & {
    color: #dc3545;
  }
  
  .toast-warning & {
    color: #ffc107;
  }
  
  .toast-info & {
    color: #17a2b8;
  }
}

.toast-content {
  flex-grow: 1;
}

.toast-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.toast-message {
  font-size: 0.875rem;
  color: #6c757d;
}

.toast-close {
  margin-left: 1rem;
  color: #6c757d;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  padding: 0;
  line-height: 1;
  
  &:hover {
    opacity: 1;
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>