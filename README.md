# MedChain: A Blockchain-Based Healthcare Platform

![Vue.js](https://img.shields.io/badge/Vue.js-v3.2-green) ![Python](https://img.shields.io/badge/Python-v3.10-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

MedChain is a blockchain-based healthcare platform designed to provide secure, efficient, and responsive solutions for healthcare systems. It features user-friendly interfaces, robust backend functionality, and role-based dashboards tailored to different user types.

---

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Project Structure](#project-structure)
4. [Admin Dashboard](#admin-dashboard)
5. [Backend](#backend)
6. [Frontend](#frontend)
7. [Setup Instructions](#setup-instructions)
8. [Contributing](#contributing)
9. [License](#license)

---

## Overview
MedChain leverages blockchain technology to ensure data security, transparency, and efficiency within the healthcare ecosystem. Key components include:
- **Admin Dashboard**: A centralized hub for managing users, verifications, and activities.
- **Backend**: A Flask-based application providing secure APIs for authentication, role management, and data storage.
- **Frontend**: A Vue.js-based application offering responsive user interfaces for various roles.

---

## Key Features
### Platform-Wide
- Blockchain integration for secure data storage and management.
- Role-based access control for administrators, doctors, patients, and other stakeholders.
- Responsive design optimized for desktops, tablets, and mobile devices.

### Backend
- **User Authentication**: Secure registration, login, and password management.
- **Role-Based Access Control**: Multiple roles such as admin, doctor, patient, hospital admin, and pharmacy admin.
- **Data Encryption**: Sensitive data is encrypted for secure storage.
- **Rate Limiting**: Protection against endpoint abuse.
- **Audit Logging**: Tracks key events for transparency.

### Frontend
- Separate dashboards for different roles.
- Modular Vue.js components for reusability.
- Real-time data fetching and state management with Vuex.
- User-friendly design and error handling.

### Admin Dashboard
- **Summary Cards**: Displays essential metrics like pending verifications and unresolved complaints.
- **Verification Queue**: Streamlined verification process for doctors, hospitals, patients, and pharmacies.
- **Activity Feed**: Provides a quick overview of platform activities.
- **Sidebar Navigation**: Easy access to different sections of the admin dashboard.

---

## Project Structure
```
MedChain/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── admin.py
│   │   │   └── ...
│   │   ├── security.py
│   │   ├── utils.py
│   │   └── ...
│   ├── run.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   └── styles/
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   ├── shared/
│   │   │   └── ...
│   │   ├── router/
│   │   ├── store/
│   │   ├── views/
│   │   └── ...
├── README.md
└── ...
```

---

## Admin Dashboard
### Summary of Features
- **Dynamic Data Fetching**: Real-time updates for dashboard metrics and queues.
- **Error Handling**: Graceful error management and retry options.
- **Auto-Refresh**: Data refreshes every 5 minutes to keep information up-to-date.
- **Vue.js Components**: Modular components for summary cards, activity feeds, and verification queues.

### Key Components
- **AdminDashboard.vue**: Main admin dashboard component.
- **AdminNavbar.vue**: Top navigation bar.
- **AdminSidebar.vue**: Collapsible sidebar for navigation.
- **DashboardCard.vue**: Reusable card component for metrics.
- **ActivityFeed.vue**: Component for displaying recent activities.

### API Endpoints
- `GET /api/admin/dashboard-stats`: Fetches dashboard metrics.
- `GET /api/admin/activity-feed`: Retrieves recent activity logs.
- `GET /api/admin/verification-queue`: Fetches pending verifications.

---

## Backend
### Key Features
- **Authentication**: Secure user registration, login, and multi-factor authentication.
- **Admin Tools**: APIs for managing users, roles, and verification statuses.
- **Data Security**: Encryption of sensitive fields and CSRF protection.
- **Rate Limiting**: Prevents abuse of API endpoints.

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── ...
│   └── ...
```

### API Endpoints
#### Authentication
- `POST /api/auth/register`: Registers a new user.
- `POST /api/auth/login`: Logs in a user and issues JWT tokens.
- `POST /api/auth/reset-password`: Resets a user's password.

#### Administration
- `GET /api/admin/users`: Fetches all users with roles and statuses.
- `POST /api/admin/approve`: Approves a user or entity.
- `POST /api/admin/reject`: Rejects a user or entity.

---

## Frontend
### Key Features
- **Role-Based Dashboards**: Tailored dashboards for admins, doctors, patients, and others.
- **Reusable Components**: Modular design for cards, tables, and forms.
- **State Management**: Centralized state with Vuex for seamless data flow.
- **Dynamic Data Fetching**: Real-time updates for statistics and queues.
- **Responsive Design**: Optimized for all device types.

### Project Structure
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── styles/
│   ├── components/
│   ├── router/
│   ├── store/
│   ├── views/
│   ├── App.vue
│   └── main.js
```

---

## Setup Instructions
### Prerequisites
- **Backend**: Python 3.10+, Redis, PostgreSQL
- **Frontend**: Node.js 16+, Vue CLI

### Backend Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/21Ravan12/MedChain-Admin.git
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/medchain
   JWT_SECRET_KEY=your_jwt_secret
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_email_password
   ```
4. Run the application:
   ```bash
   flask run
   ```

### Frontend Installation
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
    npm run serve
   ```

---

## Contributing
We welcome contributions! Please follow the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details
```
