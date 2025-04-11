<template>
    <div class="patient-detail-modal">
      <div class="modal-overlay" @click.self="$emit('close')"></div>
      <div class="modal-content">
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
        
        <div class="patient-header">
          <div class="avatar-container">
            <div class="avatar">
              <img :src="patient.avatar || defaultAvatar" alt="Patient Photo">
              <div class="verification-badge" :class="patient.status">
                <i :class="statusIcon"></i>
              </div>
            </div>
          </div>
          
          <div class="header-info">
            <h2>{{ patient.fullName }}</h2>
            <div class="demographics">
              <i class="fas fa-user"></i>
              {{ patient.age }} years • {{ patient.gender }}
            </div>
            
            <div class="contact-info">
              <div class="contact-item">
                <i class="fas fa-envelope"></i>
                <span>{{ patient.email }}</span>
              </div>
              <div class="contact-item">
                <i class="fas fa-id-card"></i>
                <span>Patient ID: {{ patient.patientId }}</span>
              </div>
              <div class="contact-item" v-if="patient.phone">
                <i class="fas fa-phone"></i>
                <span>{{ patient.phone }}</span>
              </div>
              <div class="contact-item">
                <i class="fas fa-calendar-alt"></i>
                <span>Registered: {{ formatDate(patient.registrationDate) }}</span>
              </div>
            </div>
          </div>
        </div>
    
        <div class="documents-section" v-if="patient.documents && patient.documents.length">
          <div class="section-header">
            <h3><i class="fas fa-file-alt"></i> Verification Documents</h3>
            <span class="badge">{{ patient.documents.length }}</span>
          </div>
          <div class="document-list">
            <div v-for="(doc, index) in patient.documents" :key="index" class="document-item">
              <div class="document-info">
                <i class="fas fa-file-pdf document-icon"></i>
                <span class="document-name">{{ doc }}</span>
              </div>
              <div class="document-actions">
                <button class="btn btn-outline" @click="viewDocument(doc)">
                  <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-outline" @click="downloadDocument(doc)">
                  <i class="fas fa-download"></i> Download
                </button>
              </div>
            </div>
          </div>
        </div>
  
        <div class="rejection-section" v-if="patient.rejectionReason">
          <div class="section-header warning">
            <h3><i class="fas fa-exclamation-triangle"></i> Rejection Details</h3>
          </div>
          <div class="rejection-content">
            <div class="rejection-meta">
              <span class="rejection-date">Rejected on: {{ formatDate(patient.rejectionDate) }}</span>
              <span class="rejected-by">By: {{ patient.rejectedBy || 'Administrator' }}</span>
            </div>
            <div class="rejection-reason">
              <p>{{ patient.rejectionReason }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      patient: {
        type: Object,
        required: true
      }
    },
    data() {
      return {
        defaultAvatar: '/images/default-patient.png'
      }
    },
    computed: {
      statusIcon() {
        return {
          'pending': 'fas fa-hourglass-half',
          'approved': 'fas fa-check-circle',
          'rejected': 'fas fa-times-circle'
        }[this.patient.status]
      }
    },
    methods: {
      viewDocument(document) {
        console.log('Viewing document:', document)
        // Implement document viewing logic
      },
      downloadDocument(document) {
        console.log('Downloading document:', document)
        // Implement document download logic
      },
      downloadProfile() {
        console.log('Downloading patient profile')
        // Implement profile download logic
      },
      formatDate(date) {
        if (!date) return 'N/A'
        return new Date(date).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      }
    }
  }
  </script>

<style scoped>
@import '@fortawesome/fontawesome-free/css/all.min.css';

.patient-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 20px;
  color: #95a5a6;
  cursor: pointer;
  padding: 5px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e74c3c;
}

.patient-header {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  border: 3px solid #ecf0f1;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.verification-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border: 2px solid white;
}

.verification-badge.pending {
  background-color: #f39c12;
}

.verification-badge.approved {
  background-color: #2ecc71;
}

.verification-badge.rejected {
  background-color: #e74c3c;
}

.header-info {
  flex: 1;
}

.header-info h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #2c3e50;
}

.specialization {
  font-size: 18px;
  color: #3498db;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.contact-info {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #34495e;
}

.contact-item i {
  color: #7f8c8d;
  width: 20px;
  text-align: center;
}

.divider {
  height: 1px;
  background: #ecf0f1;
  margin: 25px 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.section-header.warning h3 {
  color: #e74c3c;
}

.section-header i {
  font-size: 20px;
}

.badge {
  background: #3498db;
  color: white;
  border-radius: 12px;
  padding: 3px 10px;
  font-size: 14px;
  font-weight: 600;
}

.document-list {
  display: grid;
  gap: 12px;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8fafb;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.document-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.document-icon {
  font-size: 24px;
  color: #e74c3c;
}

.document-name {
  font-weight: 500;
  color: #2c3e50;
}

.document-actions {
  display: flex;
  gap: 10px;
}

.rejection-section {
  background: #fef2f2;
  border-radius: 8px;
  padding: 20px;
  margin-top: 25px;
}

.rejection-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 15px;
}

.rejection-reason {
  background: white;
  padding: 15px;
  border-radius: 6px;
  font-size: 15px;
  line-height: 1.6;
  color: #2c3e50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  background: white;
  border: 1px solid #bdc3c7;
  color: #34495e;
}

.btn-icon:hover {
  background: #f8f9fa;
}

.btn-outline {
  background: white;
  border: 1px solid #3498db;
  color: #3498db;
}

.btn-outline:hover {
  background: #f0f8ff;
}

.btn-success {
  background: #2ecc71;
  border: none;
  color: white;
}

.btn-success:hover {
  background: #27ae60;
}

.btn-danger {
  background: #e74c3c;
  border: none;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .patient-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .contact-info {
    grid-template-columns: 1fr;
  }
  
  .document-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .document-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
