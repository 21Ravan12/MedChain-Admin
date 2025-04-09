// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../components/views/auth/LoginView.vue' 
import SignUpView from '../components/views/auth/RegisterView.vue' 
import SelectRoleView from '../components/views/auth/SelectRoleView.vue' 
import ResetView from '../components/views/auth/ResetView.vue' 
import SignUpVerifyCodeView from '../components/views/auth/SignUpVerifyCodeView.vue' 
import VerifyCodeView from '../components/views/auth/VerifyCodeView.vue' 
import UpdatePasswordView from '../components/views/auth/UpdatePasswordView.vue' 

import AdminDashboardView from '../components/views/admin/AdminDashboardView.vue' 
import VerifyDoctorsView from '../components/views/admin/verify/VerifyDoctorsView.vue' 
import VerifyAdminView from '../components/views/admin/verify/VerifyAdminView.vue' 
import VerifyHospitalsView from '../components/views/admin/verify/VerifyHospitalsView.vue' 
import VerifyPharmaciesView from '../components/views/admin/verify/VerifyPharmaciesView.vue' 
import VerifyPatientsView from '../components/views/admin/verify/VerifyPatientsView.vue' 
import VerifyPharmacistsView from '../components/views/admin/verify/VerifyPharmacistsView.vue' 
import ComplaintsListView from '../components/views/admin/complaints/ComplaintsListView.vue' 
import UserManagementView from '../components/views/admin/user/UserManagementView.vue'
import VerifyHospitalAdminView from '../components/views/admin/verify/VerifyHospitalAdminView.vue'
import VerifyPharmacyAdminView from '../components/views/admin/verify/VerifyPharmacyAdminView.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignUpView
  },
  {
    path: '/resetpassword',
    name: 'resetpassword',
    component: ResetView
  },
  {
    path: '/signupverifycode',
    name: 'signupverifycode',
    component: SignUpVerifyCodeView
  },
  {
    path: '/verifycode',
    name: 'verifycode',
    component: VerifyCodeView
  },
  {
    path: '/updatepassword',
    name: 'updatepassword',
    component: UpdatePasswordView
  },
  {
    path: '/selectroleview',
    name: 'selectroleview',
    component: SelectRoleView
  },
  {
    path: '/admin/dashboard',
    name: 'admindashboardview',
    component: AdminDashboardView
  },
  {
    path: '/admin/verify/doctors',
    name: 'verifydoctorsview',
    component: VerifyDoctorsView
  },
  {
    path: '/admin/verify/hospitals',
    name: 'verifyhospitalsview',
    component: VerifyHospitalsView
  },
  {
    path: '/admin/verify/pharmacies',
    name: 'verifypharmaciesview',
    component: VerifyPharmaciesView
  },
  {
    path: '/admin/verify/patients',
    name: 'verifypatientsview',
    component: VerifyPatientsView
  },
  {
    path: '/admin/verify/pharmacists',
    name: 'verifypharmacistsview',
    component: VerifyPharmacistsView
  },
  {
    path: '/admin/complaints',
    name: 'complaintslistview',
    component: ComplaintsListView
  },
  {
    path: '/admin/users',
    name: 'usermanagementview',
    component: UserManagementView
  },
  {
    path: '/admin/verify/hospitals/admins',
    name: 'verifyhospitaladminview',
    component: VerifyHospitalAdminView
  },
  {
    path: '/admin/verify/pharmacies/admins',
    name: 'verifypharmacyadminview',
    component: VerifyPharmacyAdminView
  },
  {
    path: '/admin/verify/admins',
    name: 'verifyadminview',
    component: VerifyAdminView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router