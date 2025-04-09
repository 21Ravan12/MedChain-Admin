<template>
    <div class="complaint-detail-modal">
      <div class="modal-overlay" @click.self="$emit('close')"></div>
      <div class="modal-content">
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
        
        <div class="complaint-header">
          <div class="header-info">
            <h2>Complaint #{{ complaint.id }}</h2>
            <div class="complaint-meta">
              <span class="complaint-type">{{ complaint.type }}</span>
              <span class="complaint-date">
                <i class="fas fa-calendar-alt"></i>
                {{ formatDate(complaint.date) }}
              </span>
              <span class="status-indicator" :class="complaint.status">
                {{ formatStatus(complaint.status) }}
              </span>
            </div>
          </div>
        </div>
  
        <div class="divider"></div>
  
        <div class="parties-section">
          <div class="section-header">
            <h3><i class="fas fa-users"></i> Parties Involved</h3>
          </div>
          <div class="parties-grid">
            <div class="party-card complainant">
              <div class="party-header">
                <i class="fas fa-user-circle"></i>
                <h4>Complainant</h4>
              </div>
              <div class="party-details">
                <p><strong>Name:</strong> {{ complaint.complainant.name }}</p>
                <p><strong>Type:</strong> {{ complaint.complainant.type }}</p>
              </div>
            </div>
            
            <div class="party-card against">
              <div class="party-header">
                <i class="fas fa-user-slash"></i>
                <h4>Against</h4>
              </div>
              <div class="party-details">
                <p><strong>Name:</strong> {{ complaint.against.name }}</p>
                <p><strong>Type:</strong> {{ complaint.against.type }}</p>
              </div>
            </div>
          </div>
        </div>
  
        <div class="details-section">
          <div class="section-header">
            <h3><i class="fas fa-info-circle"></i> Complaint Details</h3>
          </div>
          <div class="details-content">
            <p>{{ complaint.details }}</p>
          </div>
        </div>
  
        <div class="messages-section" v-if="complaint.messages && complaint.messages.length">
          <div class="section-header">
            <h3><i class="fas fa-comments"></i> Communication</h3>
          </div>
          <div class="messages-list">
            <div v-for="(message, index) in complaint.messages" :key="index" class="message">
              <div class="message-header">
                <span class="sender">{{ message.sender }}</span>
                <span class="date">{{ formatDateTime(message.date) }}</span>
              </div>
              <div class="message-content">
                <p>{{ message.content }}</p>
              </div>
            </div>
          </div>
        </div>
  
        <div class="resolution-section" v-if="complaint.resolution">
          <div class="section-header">
            <h3><i class="fas fa-check-circle"></i> Resolution</h3>
          </div>
          <div class="resolution-content">
            <p>{{ complaint.resolution }}</p>
            <p class="resolution-date">
              <i class="fas fa-calendar-check"></i>
              Resolved on: {{ formatDate(complaint.resolvedAt) }}
            </p>
          </div>
        </div>
  
        <div class="modal-footer" v-if="complaint.status !== 'resolved'">
          <button class="btn btn-success" @click="markAsResolved">
            <i class="fas fa-check"></i> Mark as Resolved
          </button>
          <button class="btn btn-primary" @click="addMessage">
            <i class="fas fa-reply"></i> Add Response
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      complaint: {
        type: Object,
        required: true
      }
    },
    methods: {
      formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      },
      formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
      formatStatus(status) {
        return status.replace('_', ' ');
      },
      markAsResolved() {
        this.$emit('resolve', 'Complaint resolved by administrator');
      },
      addMessage() {
        // Implementation for adding messages
      }
    }
  }
  </script>
  
  <style scoped>
  .complaint-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 800px;
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .close-btn {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 20px;
    color: #6c757d;
    cursor: pointer;
  }
  
  .complaint-header {
    margin-bottom: 20px;
  }
  
  .complaint-header h2 {
    margin: 0;
    color: #343a40;
  }
  
  .complaint-meta {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 10px;
    color: #6c757d;
  }
  
  .complaint-type {
    background: #e9ecef;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 14px;
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
  
  .divider {
    height: 1px;
    background: #e9ecef;
    margin: 20px 0;
  }
  
  .section-header {
    margin-bottom: 15px;
  }
  
  .section-header h3 {
    margin: 0;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .section-header i {
    color: #6c757d;
  }
  
  .parties-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .party-card {
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  
  .party-card.complainant {
    border-left: 4px solid #17a2b8;
  }
  
  .party-card.against {
    border-left: 4px solid #dc3545;
  }
  
  .party-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  
  .party-header i {
    font-size: 20px;
  }
  
  .party-header h4 {
    margin: 0;
  }
  
  .party-card.complainant .party-header i {
    color: #17a2b8;
  }
  
  .party-card.against .party-header i {
    color: #dc3545;
  }
  
  .party-details p {
    margin: 5px 0;
  }
  
  .details-content {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 30px;
    line-height: 1.6;
  }
  
  .messages-list {
    margin-bottom: 30px;
  }
  
  .message {
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e9ecef;
  }
  
  .message:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 14px;
  }
  
  .sender {
    font-weight: 500;
  }
  
  .date {
    color: #6c757d;
  }
  
  .message-content {
    background: #f8f9fa;
    padding: 10px 15px;
    border-radius: 8px;
  }
  
  .resolution-content {
    background: #d4edda;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 30px;
  }
  
  .resolution-date {
    margin-top: 10px;
    font-size: 14px;
    color: #155724;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
  </style>