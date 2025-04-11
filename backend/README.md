# MedChain Backend

The MedChain backend is a Flask-based application designed to handle user authentication, role-based access control, and secure data management for a healthcare platform. It provides APIs for user registration, login, role selection, and other administrative functionalities.

## Features

- **User Authentication**: Secure user registration, login, logout, and password reset functionalities.
- **Role-Based Access Control**: Supports multiple roles such as `patient`, `doctor`, `hospitalAdmin`, `pharmacyAdmin`, and `admin`.
- **Data Encryption**: Sensitive data is encrypted before being stored in the database.
- **Rate Limiting**: Protects endpoints from abuse using Flask-Limiter.
- **CSRF Protection**: Ensures secure requests with CSRF tokens.
- **Audit Logging**: Tracks critical events like login attempts, registration, and role changes.
- **Redis Integration**: Manages temporary session data and rate-limiting keys.
- **Email Notifications**: Sends verification codes and notifications via email.
- **Multi-Factor Authentication (MFA)**: Optional MFA for enhanced security.
- **Admin Dashboard**: Provides endpoints for managing users, roles, and verification statuses.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── ...
│   ├── security.py
│   ├── utils.py
│   └── ...
├── run.py
└── requirements.txt
```

### Key Files

- **`auth.py`**: Handles user authentication, registration, role selection, and MFA.
- **`admin.py`**: Provides administrative endpoints for managing users, roles, and verification statuses.
- **`models.py`**: Defines database models for users, roles, and audit logs.
- **`security.py`**: Contains encryption, decryption, and security-related utilities.
- **`utils.py`**: Includes helper functions for email sending, token generation, and rate-limiting keys.
- **`config.py`**: Centralized configuration for the application, including database and email settings.

## API Endpoints

### Authentication (`auth.py`)

- **`POST /api/auth/register`**: Registers a new user.
- **`POST /api/auth/login`**: Logs in a user and issues JWT tokens.
- **`POST /api/auth/logout`**: Logs out a user and invalidates their session.
- **`POST /api/auth/select-role`**: Assigns a role to a user during registration.
- **`POST /api/auth/resend-verification-code`**: Resends a verification code to the user.
- **`POST /api/auth/complete-registration`**: Completes the registration process after verification.
- **`POST /api/auth/request-password-reset`**: Initiates a password reset process.
- **`POST /api/auth/verify-reset-code`**: Verifies a password reset code.
- **`POST /api/auth/reset-password`**: Resets the user's password.
- **`POST /api/auth/enable-mfa`**: Enables multi-factor authentication for a user.
- **`POST /api/auth/disable-mfa`**: Disables multi-factor authentication for a user.
- **`POST /api/auth/verify-mfa`**: Verifies an MFA code.

### Administration (`admin.py`)

The `admin.py` file provides endpoints for managing users, roles, and verification statuses. These endpoints are restricted to users with the `admin` role.

#### Admin Profile and Dashboard

- **`GET /api/admin/profile`**: Retrieves the profile of the currently logged-in admin.
- **`GET /api/admin/dashboard-stats`**: Retrieves statistics for the admin dashboard, including counts of verified and unverified entities.

#### User Management

- **`GET /api/admin/users`**: Fetches all users with their roles and statuses.
- **`POST /api/admin/approve`**: Approves a user or entity.
- **`POST /api/admin/reject`**: Rejects a user or entity.

#### Verification Management

- **`GET /api/admin/unverified-hospital`**: Fetches unverified hospitals.
- **`GET /api/admin/unverified-doctor`**: Fetches unverified doctors.
- **`GET /api/admin/unverified-patient`**: Fetches unverified patients.
- **`GET /api/admin/unverified-pharmacy`**: Fetches unverified pharmacies.
- **`GET /api/admin/unverified-pharmacist`**: Fetches unverified pharmacists.
- **`GET /api/admin/unverified-admins`**: Fetches unverified admins.
- **`GET /api/admin/unverified-hospital-admin`**: Fetches unverified hospital admins.
- **`GET /api/admin/unverified-pharmacy-admins`**: Fetches unverified pharmacy admins.
- **`GET /api/admin/verified-hospital`**: Fetches verified hospitals.
- **`GET /api/admin/verified-pharmacy`**: Fetches verified pharmacies.

### Key Features in `admin.py`

- **Pagination**: All endpoints support pagination using `page` and `per_page` query parameters.
- **Data Decryption**: Sensitive fields like names, emails, and phone numbers are decrypted before being returned in the response.
- **CSRF Protection**: CSRF tokens are generated and included in responses for secure admin actions.
- **Dynamic Role Management**: Supports multiple roles and dynamically fetches data based on the role.
- **Error Handling**: Comprehensive error handling with detailed logging for debugging.

## Security Features

- **Encryption**: All sensitive fields (e.g., email, phone, passwords) are encrypted using `encrypt_data` and `decrypt_data` functions.
- **CSRF Protection**: Ensures secure requests using CSRF tokens.
- **Rate Limiting**: Prevents abuse of endpoints with configurable limits.
- **Audit Logs**: Tracks critical events asynchronously using the `AuditLog` model.

## Setup Instructions

### Prerequisites

- Python 3.10+
- Redis
- PostgreSQL (or any SQLAlchemy-compatible database)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/medchain-backend.git
   cd medchain-backend
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost/medchain
   JWT_SECRET_KEY=your_jwt_secret
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_email_password
   ```

4. Initialize the database:
   ```sh
   flask db upgrade
   ```

5. Run the application:
   ```sh
   flask run
   ```

## Testing

- Run unit tests:
  ```sh
  pytest
  ```

## Logging

Logs are stored in `app.log` with advanced filtering for sensitive data. Rotating logs are configured to prevent excessive disk usage.

## Contributing

Contributions are welcome! Please follow the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
