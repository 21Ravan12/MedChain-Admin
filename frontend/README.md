# MedChain Frontend

The MedChain frontend is a Vue.js-based application designed to provide an intuitive and responsive user interface for the MedChain healthcare platform. It includes role-based dashboards, user management, and administrative tools for managing verifications, complaints, and blockchain health.

## Features

- **Role-Based Dashboards**: Separate dashboards for `admin`, `doctor`, `patient`, `hospitalAdmin`, `pharmacyAdmin`, and other roles.
- **Verification Management**: Admins can view and manage pending verifications for doctors, hospitals, pharmacies, and patients.
- **Activity Feed**: Displays recent activities for admins to monitor platform events.
- **Responsive Design**: Fully responsive UI optimized for desktop, tablet, and mobile devices.
- **Dynamic Data Fetching**: Real-time updates for dashboard statistics and verification queues.
- **Error Handling**: Graceful error handling with retry options for failed API calls.
- **State Management**: Centralized state management using Vuex for seamless data flow across components.
- **Reusable Components**: Modular and reusable components for cards, tables, and forms.
- **Theming**: Consistent design with a clean and modern theme.

## Project Structure

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
│   │   ├── admin/
│   │   │   ├── dashboard/
│   │   │   │   ├── AdminDashboard.vue
│   │   │   │   ├── components/
│   │   │   │   │   ├── AdminNavbar.vue
│   │   │   │   │   ├── AdminSidebar.vue
│   │   │   │   │   ├── DashboardCard.vue
│   │   │   │   │   ├── ActivityFeed.vue
│   │   │   │   │   └── VerificationQueue.vue
│   │   │   └── ...
│   │   ├── shared/
│   │   │   ├── Button.vue
│   │   │   ├── Modal.vue
│   │   │   └── ...
│   ├── router/
│   │   ├── index.js
│   │   └── routes/
│   │       ├── adminRoutes.js
│   │       ├── userRoutes.js
│   │       └── ...
│   ├── store/
│   │   ├── index.js
│   │   ├── modules/
│   │   │   ├── admin.js
│   │   │   ├── user.js
│   │   │   └── ...
│   ├── views/
│   │   ├── AdminView.vue
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   └── ...
│   ├── App.vue
│   ├── main.js
│   └── ...
├── package.json
└── README.md
```

### Key Directories

- **`components/`**: Contains reusable Vue components, including admin-specific components like `AdminDashboard.vue` and shared components like `Button.vue` and `Modal.vue`.
- **`router/`**: Defines application routes and role-based navigation guards.
- **`store/`**: Vuex store for managing global state, including modules for admin and user-specific data.
- **`views/`**: High-level views corresponding to application pages, such as login, registration, and admin dashboard.
- **`assets/`**: Static assets like images and global styles.

## Key Components

### Admin Dashboard (`AdminDashboard.vue`)

The admin dashboard is the central hub for managing the platform. It includes:

- **Summary Cards**: Displays key statistics like pending verifications, unresolved complaints, total users, and blockchain health.
- **Recent Activity**: Shows a feed of recent actions performed on the platform.
- **Verification Queue**: Lists pending verifications for doctors, hospitals, pharmacies, and patients.
- **Sidebar Navigation**: Collapsible sidebar for navigating between admin-specific pages.
- **Navbar**: Displays the admin's name and provides quick access to settings and logout.

### Shared Components

- **`Button.vue`**: A customizable button component with support for different styles and sizes.
- **`Modal.vue`**: A reusable modal dialog for displaying forms, confirmations, and alerts.

## State Management

The application uses Vuex for centralized state management. Key modules include:

- **`admin.js`**: Manages admin-specific data, such as dashboard statistics, recent activities, and verification queues.
- **`user.js`**: Handles user authentication, profile data, and role-based permissions.

### Example Vuex Actions

- **`fetchDashboardStats`**: Fetches dashboard statistics for the admin.
- **`fetchVerificationQueue`**: Retrieves pending verifications for doctors, hospitals, pharmacies, and patients.

## API Integration

The frontend communicates with the backend via RESTful APIs. Key API endpoints include:

- **`GET /api/admin/dashboard-stats`**: Fetches statistics for the admin dashboard.
- **`GET /api/admin/unverified-doctor`**: Retrieves unverified doctors for verification.
- **`GET /api/admin/unverified-patient`**: Retrieves unverified patients for verification.
- **`GET /api/admin/unverified-pharmacist`**: Retrieves unverified pharmacists for verification.
- **`POST /api/auth/login`**: Authenticates a user and retrieves a JWT token.
- **`POST /api/auth/register`**: Registers a new user.

## Styling

The application uses scoped CSS for component-specific styles and global styles for shared elements. Key design principles include:

- **Consistency**: Uniform spacing, colors, and typography across components.
- **Responsiveness**: Media queries for adapting layouts to different screen sizes.
- **Accessibility**: ARIA attributes and keyboard navigation support.

### Example Styles

```css
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8faf7;
}

.dashboard-header h1 {
  color: #2d6a4f;
  font-size: 2rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.view-all {
  color: #40916c;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.view-all:hover {
  color: #2d6a4f;
  text-decoration: underline;
}
```

## Setup Instructions

### Prerequisites

- Node.js 16+
- Vue CLI

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/medchain-frontend.git
   cd medchain-frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. Configure environment variables in a `.env` file:
   ```
   VUE_APP_API_BASE_URL=http://localhost:5000/api
   ```

4. Run the development server:
   ```sh
   npm run serve
   ```

5. Build for production:
   ```sh
   npm run build
   ```

## Testing

- Run unit tests:
  ```sh
  npm run test:unit
  ```

- Run end-to-end tests:
  ```sh
  npm run test:e2e
  ```

## Deployment

1. Build the application:
   ```sh
   npm run build
   ```

2. Deploy the `dist/` directory to your web server.

## Contributing

Contributions are welcome! Please follow the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
