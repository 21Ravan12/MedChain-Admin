<template>
  <div class="doctor-detail-modal">
    <div class="modal-overlay" @click.self="$emit('close')"></div>
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
      
      <div class="doctor-header">
        <div class="avatar-container">
          <div class="avatar">
            <img :src="doctor.avatar || defaultAvatar" alt="Doctor Avatar">
            <div class="verification-badge" :class="doctor.status">
              <i :class="statusIcon"></i>
            </div>
          </div>
        </div>
        
        <div class="header-info">
          <h2>Dr. {{ doctor.fullName }}</h2>
          <div class="specialization">
            <i class="fas fa-stethoscope"></i>
            {{ doctor.specialization }}
          </div>
          
          <div class="contact-info">
            <div class="contact-item">
              <i class="fas fa-envelope"></i>
              <span>{{ doctor.email }}</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-id-card"></i>
              <span>License: {{ doctor.licenseNumber }}</span>
            </div>
            <div class="contact-item" v-if="doctor.phone">
              <i class="fas fa-phone"></i>
              <span>{{ doctor.phone }}</span>
            </div>
            <div class="contact-item">
              <i class="fas fa-calendar-alt"></i>
              <span>Registered: {{ formatDate(doctor.registrationDate) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="documents-section" v-if="doctor.documents && doctor.documents.length">
        <div class="section-header">
          <h3><i class="fas fa-file-alt"></i> Verification Documents</h3>
          <span class="badge">{{ doctor.documents.length }}</span>
        </div>
        <div class="document-list">
          <div v-for="(doc, index) in doctor.documents" :key="index" class="document-item">
            <div class="document-info">
              <i class="fas" :class="getDocumentIcon(doc)"></i>
              <span class="document-name">{{ getDocumentName(doc) }}</span>
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

      <!-- Document Viewer Modal -->
      <div v-if="showDocumentViewer" class="document-viewer-modal">
        <div class="document-viewer-overlay" @click="closeDocumentViewer"></div>
        <div class="document-viewer-content">
          <div class="viewer-header">
            <h3>{{ currentDocumentName }}</h3>
            <button class="close-btn" @click="closeDocumentViewer">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="viewer-container">
            <iframe 
              v-if="isPdf"
              :src="pdfViewerUrl"
              frameborder="0"
              class="pdf-viewer"
            ></iframe>
            <img 
              v-else-if="isImage"
              :src="imageViewerUrl"
              alt="Document"
              class="image-viewer"
              @error="handleImageError"
            />
            <div v-else class="unsupported-format">
              <i class="fas fa-exclamation-triangle"></i>
              <p>This file format is not supported for preview</p>
            </div>
          </div>
        </div>
      </div>

      <div class="rejection-section" v-if="doctor.rejectionReason">
        <div class="section-header warning">
          <h3><i class="fas fa-exclamation-triangle"></i> Rejection Details</h3>
        </div>
        <div class="rejection-content">
          <div class="rejection-meta">
            <span class="rejection-date">Rejected on: {{ formatDate(doctor.rejectionDate) }}</span>
            <span class="rejected-by">By: {{ doctor.rejectedBy || 'Administrator' }}</span>
          </div>
          <div class="rejection-reason">
            <p>{{ doctor.rejectionReason }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    doctor: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      defaultAvatar: '/images/default-doctor.png',
      showDocumentViewer: false,
      currentDocumentName: '',
      currentDocumentData: null,
      imageLoadError: false
    }
  },
  computed: {
    statusIcon() {
      return {
        'pending': 'fas fa-hourglass-half',
        'approved': 'fas fa-check-circle',
        'rejected': 'fas fa-times-circle'
      }[this.doctor.status]
    },
    isPdf() {
      if (!this.currentDocumentName) return false
      const docName = this.currentDocumentName.toLowerCase()
      return docName.endsWith('.pdf')
    },
    isImage() {
      if (!this.currentDocumentName) return false
      const docName = this.currentDocumentName.toLowerCase()
      return ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'].some(ext => docName.endsWith(ext))
    },
    pdfViewerUrl() {
      if (!this.currentDocumentData) return ''
      
      // Extract raw data from Proxy
      const rawData = this.unproxy(this.currentDocumentData)
      const data = rawData.data || (rawData.license && rawData.license.data)
      
      if (data) {
        return `data:application/pdf;base64,${data}`
      }
      return `/documents/${encodeURIComponent(this.currentDocumentName)}#view=fitH`
    },
    imageViewerUrl() {
      if (!this.currentDocumentData) return ''
      
      // Extract raw data from Proxy
      const rawData = this.unproxy(this.currentDocumentData)
      const base64Data = rawData.data || (rawData.license && rawData.license.data)
      
      if (!base64Data) {
        return `/documents/${encodeURIComponent(this.currentDocumentName)}`
      }

      // Determine MIME type based on file extension
      let mimeType = 'image/png' // default
      if (this.currentDocumentName) {
        const ext = this.currentDocumentName.toLowerCase().split('.').pop()
        switch(ext) {
          case 'jpg':
          case 'jpeg': mimeType = 'image/jpeg'; break
          case 'gif': mimeType = 'image/gif'; break
          case 'webp': mimeType = 'image/webp'; break
          case 'bmp': mimeType = 'image/bmp'; break
          // Don't include PDF here as we have separate PDF handling
        }
      }
      
      return `data:${mimeType};base64,${base64Data}`
    }
  },
  methods: {
    // Helper to extract raw data from Vue Proxy
    unproxy(obj) {
      return JSON.parse(JSON.stringify(obj))
    },
    
    getDocumentIcon(doc) {
      const name = this.getDocumentName(doc).toLowerCase()
      if (name.endsWith('.pdf')) return 'fa-file-pdf'
      if (name.endsWith('.doc') || name.endsWith('.docx')) return 'fa-file-word'
      if (name.endsWith('.xls') || name.endsWith('.xlsx')) return 'fa-file-excel'
      if ([ '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp' ].some(ext => name.endsWith(ext))) {
        return 'fa-file-image'
      }
      return 'fa-file'
    },
    getDocumentName(doc) {
      // Handle Proxy objects by getting raw data first
      const rawDoc = this.unproxy(doc)
      if (typeof rawDoc === 'string') return rawDoc
      if (rawDoc?.name) return rawDoc.name
      if (rawDoc?.license?.name) return rawDoc.license.name
      return 'Document'
    },
    viewDocument(document) {
      console.log('Viewing document:', this.unproxy(document))
      this.currentDocumentName = this.getDocumentName(document)
      this.currentDocumentData = document
      this.imageLoadError = false
      this.showDocumentViewer = true
    },
    // Rest of the methods remain exactly the same
    closeDocumentViewer() {
      this.showDocumentViewer = false
      this.currentDocumentName = ''
      this.currentDocumentData = null
      this.imageLoadError = false
    },
    downloadCurrentDocument() {
      if (this.currentDocumentData) {
        this.downloadDocument(this.currentDocumentData)
      }
    },
    downloadDocument(document) {
      const docName = this.getDocumentName(document)
      if (!docName) {
        console.error('Invalid document format:', document)
        return
      }

      // Handle both direct data and nested license data
      const rawDoc = this.unproxy(document)
      const data = rawDoc.data || (rawDoc.license && rawDoc.license.data)
      
      if (data) {
        // Determine MIME type based on file extension
        let mimeType = 'application/octet-stream'
        const ext = docName.toLowerCase().split('.').pop()
        switch(ext) {
          case 'pdf': mimeType = 'application/pdf'; break
          case 'jpg':
          case 'jpeg': mimeType = 'image/jpeg'; break
          case 'png': mimeType = 'image/png'; break
          case 'gif': mimeType = 'image/gif'; break
          case 'webp': mimeType = 'image/webp'; break
          case 'bmp': mimeType = 'image/bmp'; break
        }
        this.downloadBase64(data, docName, mimeType)
      } else {
        this.downloadFile(docName)
      }
    },
    downloadBase64(base64Data, fileName, mimeType) {
      try {
        // Clean base64 string (remove data URI prefix if present)
        const cleanBase64 = base64Data.replace(/^data:.*?;base64,/, '')
        
        const link = document.createElement('a')
        link.href = `data:${mimeType};base64,${cleanBase64}`
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        setTimeout(() => {
          document.body.removeChild(link)
          URL.revokeObjectURL(link.href)
        }, 100)
      } catch (error) {
        console.error('Error downloading base64 file:', error)
      }
    },
    downloadFile(fileName) {
      try {
        const link = document.createElement('a')
        link.href = `/documents/${encodeURIComponent(fileName)}`
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        setTimeout(() => {
          document.body.removeChild(link)
        }, 100)
      } catch (error) {
        console.error('Error downloading file:', error)
        window.open(`/documents/${encodeURIComponent(fileName)}`, '_blank')
      }
    },
    handleImageError() {
      console.error('Failed to load image:', this.currentDocumentName)
      this.imageLoadError = true
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

.doctor-detail-modal {
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

.document-viewer-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1051;
}

.document-viewer-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
}

.document-viewer-content {
  position: relative;
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.3);
}

.viewer-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
  min-height: 500px;
}

.pdf-viewer {
  width: 100%;
  height: 80vh;
}

.image-viewer {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.unsupported-format {
  text-align: center;
  color: #e74c3c;
  padding: 20px;
}

.unsupported-format i {
  font-size: 48px;
  margin-bottom: 15px;
}

.unsupported-format p {
  font-size: 18px;
  margin: 0;
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

.doctor-header {
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
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  .doctor-header {
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

  .document-viewer-content {
    width: 95%;
    padding: 15px;
  }

  .viewer-container {
    min-height: 300px;
  }

  .document-name {
    max-width: 200px;
  }
}
</style>
