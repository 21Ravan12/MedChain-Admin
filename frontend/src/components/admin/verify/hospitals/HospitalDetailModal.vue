<template>
  <div class="hospital-detail-modal">
    <div class="modal-overlay" @click.self="$emit('close')"></div>
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
      
      <div class="hospital-header">
        <div class="avatar-container">
          <div class="avatar">
            <img :src="hospital.avatar || defaultHospital" :alt="hospital.name + ' Logo'">
            <div class="verification-badge" :class="hospital.status">
              <i :class="statusIcon"></i>
            </div>
          </div>
        </div>
        
        <div class="header-info">
          <h2>{{ hospital.name }}</h2>
          <div class="type">
            <i class="fas fa-hospital"></i>
            {{ hospital.type }}
            <span class="beds-badge">
              <i class="fas fa-procedures"></i> {{ hospital.beds }} beds
            </span>
          </div>
          
          <div class="contact-info">
            <div class="contact-item">
              <i class="fas fa-envelope"></i>
              <a :href="`mailto:${hospital.email}`">{{ hospital.email }}</a>
            </div>
            <div class="contact-item">
              <i class="fas fa-phone"></i>
              <a :href="`tel:${hospital.phone}`">{{ hospital.phone }}</a>
            </div>
            <div class="contact-item">
              <i class="fas fa-map-marker-alt"></i>
              <a :href="mapsLink" target="_blank">{{ hospital.address }}</a>
            </div>
            <div class="contact-item">
              <i class="fas fa-id-card"></i>
              <span>License: {{ hospital.license_number }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="hospital-details">
        <div class="detail-section">
          <h3><i class="fas fa-info-circle"></i> Hospital Information</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label><i class="fas fa-calendar-check"></i> Established</label>
              <p>{{ formatDate(hospital.established) || 'Not specified' }}</p>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-user-md"></i> Medical Staff</label>
              <p>{{ hospital.medical_staff || 'Not specified' }}</p>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-ambulance"></i> Emergency Services</label>
              <p>{{ hospital.emergency_services ? 'Available' : 'Not available' }}</p>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-clock"></i> Operating Hours</label>
              <p>{{ hospital.operating_hours || '24/7' }}</p>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="hospital.facilities && hospital.facilities.length">
          <h3><i class="fas fa-procedures"></i> Facilities & Services</h3>
          <div class="facilities-list">
            <span class="facility-tag" v-for="(facility, index) in hospital.facilities" :key="index">
              {{ facility }}
            </span>
          </div>
        </div>

        <div class="detail-section documents-section">
          <h3><i class="fas fa-file-alt"></i> Verification Documents</h3>
          <div class="document-list">
            <div class="document-item" v-if="hospital.license_document">
              <div class="document-info">
                <i class="fas" :class="getDocumentIcon(hospital.license_document)"></i>
                <span class="document-name">{{ hospital.license_document.name }}</span>
              </div>
              <div class="document-actions">
                <button class="btn btn-outline" @click="viewDocument(hospital.license_document)">
                  <i class="fas fa-eye"></i> Preview
                </button>
                <button class="btn btn-outline" @click="downloadDocument(hospital.license_document)">
                  <i class="fas fa-download"></i> Download
                </button>
              </div>
            </div>
            
            <div class="document-item" v-if="hospital.accreditation_document">
              <div class="document-info">
                <i class="fas" :class="getDocumentIcon(hospital.accreditation_document)"></i>
                <span class="document-name">{{ hospital.accreditation_document.name }}</span>
              </div>
              <div class="document-actions">
                <button class="btn btn-outline" @click="viewDocument(hospital.accreditation_document)">
                  <i class="fas fa-eye"></i> Preview
                </button>
                <button class="btn btn-outline" @click="downloadDocument(hospital.accreditation_document)">
                  <i class="fas fa-download"></i> Download
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="rejection-section" v-if="hospital.rejectionReason">
          <div class="section-header warning">
            <h3><i class="fas fa-exclamation-triangle"></i> Rejection Details</h3>
          </div>
          <div class="rejection-content">
            <div class="rejection-meta">
              <span class="rejection-date">Rejected on: {{ formatDate(hospital.rejectionDate) }}</span>
              <span class="rejected-by">By: {{ hospital.rejectedBy || 'Administrator' }}</span>
            </div>
            <div class="rejection-reason">
              <p>{{ hospital.rejectionReason }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer" v-if="hospital.status === 'pending'">
        <button class="btn btn-success" @click="$emit('approve', hospital.id)">
          <i class="fas fa-check"></i> Approve Hospital
        </button>
        <button class="btn btn-danger" @click="$emit('reject', hospital.id)">
          <i class="fas fa-times"></i> Reject Verification
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    hospital: {
      type: Object,
      required: true,
      default: () => ({
        logo: {},
        license_document: {},
        accreditation_document: {},
        facilities: []
      })
    }
  },
  data() {
    return {
      defaultHospital: '/images/default-hospital.png'
    }
  },
  computed: {
    statusIcon() {
      return {
        'pending': 'fas fa-hourglass-half',
        'approved': 'fas fa-check-circle',
        'rejected': 'fas fa-times-circle'
      }[this.hospital.status] || 'fas fa-question-circle'
    },
    mapsLink() {
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(this.hospital.address)}`
    }
  },
  methods: {
    getDocumentIcon(doc) {
      if (!doc || !doc.name) return 'fa-file-alt'
      
      const ext = doc.name.split('.').pop().toLowerCase()
      return {
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'jpg': 'fa-file-image',
        'png': 'fa-file-image',
        'jpeg': 'fa-file-image'
      }[ext] || 'fa-file-alt'
    },
    formatDate(date) {
      if (!date) return null
      try {
        return new Date(date).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch (e) {
        return date 
      }
    },
    viewDocument(document) {
      if (document && document.data) {
        window.open(document.data, '_blank')
      }
    },
    downloadDocument(document) {
      if (document && document.data) {
        const link = document.createElement('a')
        link.href = document.data
        link.download = document.name || 'document'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }
}
</script>
  
  <style scoped>
  @import '@fortawesome/fontawesome-free/css/all.min.css';
  
  .hospital-detail-modal {
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
    max-width: 900px;
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
  
  .hospital-header {
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
    width: 140px;
    height: 140px;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    border: 3px solid #ecf0f1;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
  }
  
  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .verification-badge {
    position: absolute;
    bottom: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    border: 2px solid white;
    background-color: #3498db;
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
  
  .type {
    font-size: 18px;
    color: #3498db;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 500;
  }
  
  .beds-badge {
    background: #e8f4fc;
    color: #2980b9;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 14px;
    margin-left: 15px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
  
  .contact-info {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
  }
  
  .contact-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    color: #34495e;
  }
  
  .contact-item a {
    color: inherit;
    text-decoration: none;
  }
  
  .contact-item a:hover {
    text-decoration: underline;
    color: #3498db;
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
  
  .detail-section {
    margin-bottom: 30px;
  }
  
  .detail-section h3 {
    margin: 0 0 20px 0;
    font-size: 20px;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .detail-section h3 i {
    color: #3498db;
  }
  
  .detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
  
  .detail-item {
    background: #f8fafb;
    padding: 15px;
    border-radius: 8px;
    border-left: 3px solid #3498db;
  }
  
  .detail-item label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #7f8c8d;
    margin-bottom: 8px;
  }
  
  .detail-item p {
    margin: 0;
    font-size: 15px;
    color: #2c3e50;
    font-weight: 500;
  }
  
  .facilities-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .facility-tag {
    background: #e8f4fc;
    color: #2980b9;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
  }
  
  .section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .section-header.warning h3 {
    color: #e74c3c;
  }
  
  .section-header.warning i {
    color: #e74c3c;
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
  
  .document-info i {
    font-size: 20px;
    color: #e74c3c;
  }
  
  .document-name {
    font-weight: 500;
    color: #2c3e50;
  }
  
  .document-size {
    font-size: 12px;
    color: #95a5a6;
    margin-left: 10px;
  }
  
  .document-actions {
    display: flex;
    gap: 10px;
  }
  
  .rejection-section {
    background: #fef2f2;
    border-radius: 8px;
    padding: 20px;
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
    .hospital-header {
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