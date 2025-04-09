<template>
      <div class="queue-item" @click="$emit('navigate', 'doctors')">
        <div class="queue-icon doctor">
          <i class="fas fa-user-md"></i>
        </div>
        <div class="queue-details">
          <h3>Doctors</h3>
          <p>{{ pendingDoctors }} pending verification</p>
        </div>
        <div class="queue-arrow">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
      
      <div class="queue-item" @click="$emit('navigate', 'hospitals')">
        <div class="queue-icon hospital">
          <i class="fas fa-hospital"></i>
        </div>
        <div class="queue-details">
          <h3>Hospitals</h3>
          <p>{{ pendingHospitals }} pending verification</p>
        </div>
        <div class="queue-arrow">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
      
      <div class="queue-item" @click="$emit('navigate', 'pharmacies')">
        <div class="queue-icon pharmacy">
          <i class="fas fa-prescription-bottle-alt"></i>
        </div>
        <div class="queue-details">
          <h3>Pharmacies</h3>
          <p>{{ pendingPharmacies }} pending verification</p>
        </div>
        <div class="queue-arrow">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
      
      <div class="queue-item" @click="$emit('navigate', 'patients')">
        <div class="queue-icon patient">
          <i class="fas fa-procedures"></i>
        </div>
        <div class="queue-details">
          <h3>Patients</h3>
          <p>{{ pendingPatients }} pending verification</p>
        </div>
        <div class="queue-arrow">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
  </template>
  
  <script>
  export default {
    props: {
      pendingDoctors: Number,
      pendingHospitals: Number,
      pendingPharmacies: Number,
      pendingPatients: Number
    }
  }
  </script>
  
  <style scoped>
  .verification-queue {
    display: grid;
    gap: 12px;
  }
  
  .queue-item {
    display: flex;
    align-items: center;
    padding: 16px;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(46, 106, 79, 0.05);
    border: 1px solid #e8f0eb;
  }
  
  .queue-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 106, 79, 0.1);
    border-color: #d4e4dd;
  }
  
  .queue-icon {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    color: white;
    flex-shrink: 0;
    font-size: 16px;
  }
  
  .queue-icon.doctor {
    background: #52b788;
  }
  
  .queue-icon.hospital {
    background: #40916c;
  }
  
  .queue-icon.pharmacy {
    background: #2d6a4f;
  }
  
  .queue-icon.patient {
    background: #95d5b2;
  }
  
  .queue-details {
    flex: 1;
  }
  
  .queue-details h3 {
    margin: 0 0 4px;
    font-size: 15px;
    font-weight: 600;
    color: #2d6a4f;
  }
  
  .queue-details p {
    margin: 0;
    font-size: 13px;
    color: #7b8a82;
  }
  
  .queue-arrow {
    color: #b8c7ce;
    margin-left: 10px;
    transition: transform 0.2s ease;
  }
  
  .queue-item:hover .queue-arrow {
    color: #2d6a4f;
    transform: translateX(3px);
  }
  </style>