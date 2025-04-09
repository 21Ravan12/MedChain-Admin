import { encrypt, decrypt } from '@/utils/crypto'

export default {
  actions: {
    encryptMedicalData({ state }) {
      return encrypt(state.patients)
    }
  }
}