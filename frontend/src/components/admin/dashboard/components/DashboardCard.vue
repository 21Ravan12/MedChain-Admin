<template>
  <router-link :to="route || '#'" class="dashboard-card" :class="`card-${color}`">
    <div class="card-icon">
      <i :class="iconClass"></i>
    </div>
    <div class="card-content">
      <h3>{{ title }}</h3>
      <p>{{ formattedValue }}</p>
    </div>
  </router-link>
</template>

<script>
export default {
  props: {
    title: String,
    value: [String, Number],
    icon: String,
    color: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'accent', 'success', 'danger', 'info'].includes(value)
    },
    route: String
  },
  computed: {
    iconClass() {
      // Map icon names to Font Awesome classes
      const iconMap = {
        'verified': 'fas fa-check-circle',
        'alert': 'fas fa-exclamation-triangle',
        'users': 'fas fa-users',
        'link': 'fas fa-link',
        'doctor': 'fas fa-user-md',
        'hospital': 'fas fa-hospital',
        'pharmacy': 'fas fa-prescription-bottle-alt',
        'patient': 'fas fa-procedures',
        'complaint': 'fas fa-comment-dots'
      };
      return iconMap[this.icon] || `fas fa-${this.icon}`;
    },
    formattedValue() {
      // Format numbers with commas if they're numbers
      return typeof this.value === 'number' 
        ? this.value.toLocaleString() 
        : this.value;
    }
  }
}
</script>

<style scoped>
.dashboard-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(46, 106, 79, 0.08);
  border: 1px solid #e8f0eb;
  height: 100%;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(46, 106, 79, 0.12);
  border-color: #d4e4dd;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  color: white;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.dashboard-card:hover .card-icon {
  transform: scale(1.1);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 500;
  color: #7b8a82;
}

.card-content p {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #2d6a4f;
  line-height: 1.2;
}

/* Color Variants */
.card-primary .card-icon {
  background: #52b788;
  background: linear-gradient(135deg, #52b788 0%, #40916c 100%);
}

.card-secondary .card-icon {
  background: #ff9e00;
  background: linear-gradient(135deg, #ff9e00 0%, #ff9100 100%);
}

.card-accent .card-icon {
  background: #95d5b2;
  background: linear-gradient(135deg, #95d5b2 0%, #74c69d 100%);
}

.card-success .card-icon {
  background: #2d6a4f;
  background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
}

.card-danger .card-icon {
  background: #e76f51;
  background: linear-gradient(135deg, #e76f51 0%, #e63946 100%);
}

.card-info .card-icon {
  background: #3498db;
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
}

@media (max-width: 768px) {
  .dashboard-card {
    padding: 18px;
  }
  
  .card-icon {
    width: 54px;
    height: 54px;
    font-size: 24px;
    margin-right: 16px;
  }
  
  .card-content h3 {
    font-size: 14px;
  }
  
  .card-content p {
    font-size: 22px;
  }
}
</style>