<template>
    <ul class="activity-feed">
      <li v-for="activity in activities" :key="activity.id" class="activity-item">
        <div class="activity-icon" :class="`type-${activity.type}`">
          <i :class="getActivityIcon(activity.type)"></i>
        </div>
        <div class="activity-content">
          <p>
            <strong>{{ activity.user }}</strong> {{ activity.action }}
          </p>
          <span class="activity-time">{{ activity.time }}</span>
        </div>
      </li>
    </ul>
  </template>
  
  <script>
  export default {
    props: {
      activities: {
        type: Array,
        required: true
      }
    },
    methods: {
      getActivityIcon(type) {
        const icons = {
          verification: 'fas fa-user-check',
          complaint: 'fas fa-exclamation-circle',
          system: 'fas fa-server',
          approval: 'fas fa-thumbs-up',
          rejection: 'fas fa-times-circle'
        };
        return icons[type] || 'fas fa-bell';
      }
    }
  }
  </script>
  
  <style scoped>
  .activity-feed {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .activity-item {
    display: flex;
    padding: 12px 0;
    transition: background-color 0.2s ease;
  }
  
  .activity-item:hover {
    background-color: #f8faf7;
  }
  
  .activity-item:not(:last-child) {
    border-bottom: 1px solid #e8f0eb;
  }
  
  .activity-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    color: white;
    flex-shrink: 0;
    font-size: 14px;
  }
  
  .activity-content {
    flex: 1;
  }
  
  .activity-content p {
    margin: 0 0 4px;
    color: #2d6a4f;
    font-size: 14px;
    line-height: 1.4;
  }
  
  .activity-content strong {
    font-weight: 600;
  }
  
  .activity-time {
    font-size: 12px;
    color: #7b8a82;
    display: block;
  }
  
  /* Activity Type Colors */
  .type-verification {
    background: #52b788;
  }
  
  .type-complaint {
    background: #e76f51;
  }
  
  .type-system {
    background: #40916c;
  }
  
  .type-approval {
    background: #2d6a4f;
  }
  
  .type-rejection {
    background: #ff9e00;
  }
  </style>