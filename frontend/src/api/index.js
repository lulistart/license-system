import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  login(username, password) {
    return api.post('/login', { username, password })
  },
  
  generateLicense(data) {
    return api.post('/generate_license', data)
  },
  
  getLicenses(page = 1, pageSize = 10) {
    return api.get('/licenses', {
      params: {
        page,
        pageSize
      }
    })
  },
  
  deactivateLicense(licenseKey) {
    return api.post(`/deactivate_license/${licenseKey}`)
  },
  
  renewLicense(licenseKey, days) {
    return api.post(`/renew_license/${licenseKey}`, { days })
  },
  
  getLicenseDetails(licenseKey) {
    return api.get(`/license/${licenseKey}`)
  },
  
  batchDeactivate(licenseKeys) {
    return api.post('/batch/deactivate', { licenseKeys })
  },
  
  batchRenew(licenseKeys, days) {
    return api.post('/batch/renew', { licenseKeys, days })
  },
  
  exportLicenses() {
    return api.get('/licenses/export', { responseType: 'blob' })
  },
  
  searchLicenses(query, page = 1, pageSize = 10) {
    return api.get('/licenses/search', {
      params: {
        ...query,
        page,
        pageSize
      }
    })
  },
  
  updateLicenseNote(licenseKey, note) {
    return api.post(`/license/${licenseKey}/note`, { note })
  }
}