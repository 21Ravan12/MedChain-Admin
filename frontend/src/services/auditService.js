export default {
  logRoleChange({ userId, newRole, adminId }) {
    console.log(`Role change logged: User ${userId} -> ${newRole} by Admin ${adminId}`)
  },
  logSecurityEvent(event) {
    console.log(`Security event logged: ${JSON.stringify(event)}`)
  }
}