export const validateEmail = (email) => {
    return /@medical\.com$/.test(email)
  }
  
  export const validatePassword = (password) => {
    return password.length >= 10
  }