# MedChain - Healthcare Blockchain Platform

## Overview

MedChain is a comprehensive healthcare platform leveraging blockchain technology to provide secure, transparent, and efficient management of medical data and user interactions. The system consists of a Vue.js frontend and Flask backend, offering role-based access control for patients, doctors, hospital administrators, pharmacy administrators, and system administrators.

## Key Features

### Core Functionalities
- **Secure User Authentication**: JWT-based authentication with optional multi-factor authentication (MFA)
- **Role-Based Access Control**: Distinct interfaces and permissions for:
  - Patients
  - Doctors
  - Hospital Administrators
  - Pharmacy Administrators
  - System Administrators
- **Verification System**: Comprehensive verification workflow for all user types
- **Blockchain Integration**: Secure and transparent record-keeping

### Frontend Features
- **Responsive Dashboard**: Customized interfaces for each user role
- **Real-Time Updates**: Dynamic data fetching and display
- **Modern UI**: Clean, accessible design with reusable components
- **State Management**: Centralized data handling with Vuex

### Backend Features
- **Data Encryption**: Sensitive information protection
- **Audit Logging**: Comprehensive activity tracking
- **API Security**: CSRF protection and rate limiting
- **Email Notifications**: Verification and password reset functionality

## System Architecture

### Frontend Structure
```
frontend/
├── public/            # Static assets
├── src/
│   ├── assets/        # Images and styles
│   ├── components/    # Reusable UI components
│   ├── router/        # Navigation and route guards
│   ├── store/         # Vuex state management
│   ├── views/         # Page-level components
│   └── ...
```

### Backend Structure
```
backend/
├── app/
│   ├── routes/        # API endpoints
│   ├── models.py      # Database models
│   ├── security.py    # Encryption utilities
│   └── ...
```

## Installation

### Prerequisites
- Node.js 16+ (for frontend)
- Python 3.10+ (for backend)
- PostgreSQL database
- Redis server

### Setup Instructions

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/medchain.git
   ```

2. **Frontend Setup**:
   ```sh
   cd medchain/frontend
   npm install
   cp .env.example .env
   npm run serve
   ```

3. **Backend Setup**:
   ```sh
   cd ../backend
   pip install -r requirements.txt
   cp .env.example .env
   flask db upgrade
   flask run
   ```

## API Documentation

The backend provides RESTful endpoints for:
- User authentication and registration
- Role management
- Verification workflows
- Administrative functions

See the [API Documentation](API_DOCS.md) for detailed endpoint specifications.

## Deployment

### Frontend
```sh
npm run build
# Deploy the dist/ directory to your web server
```

### Backend
Configure a production WSGI server (e.g., Gunicorn with Nginx) and set appropriate environment variables.

## Testing

Run frontend tests:
```sh
npm run test:unit
npm run test:e2e
```

Run backend tests:
```sh
pytest
```

## Contributing

We welcome contributions! Please see our [Contribution Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please contact our support team at support@medchain.example.com.
