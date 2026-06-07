import http from './http'

export const api = {
  login(credentials) {
    return http.post('/user/login', credentials)
  },
  register(credentials) {
    return http.post('/user/register', credentials)
  },
  getCategories(userId) {
    return http.get(`/category/list/${userId}`)
  },
  addRecord(record) {
    return http.post('/record/add', record)
  },
  getRecords(userId) {
    return http.get(`/record/list/${userId}`)
  },
  saveBudget(payload) {
    return http.post('/budget/save', payload)
  },
  getTodayStats(userId) {
    return http.get(`/record/today/${userId}`)
  },
  getAiReport(userId, yearMonth) {
    return http.get(`/report/ai/${userId}/${yearMonth}`)
  },
  getAiYearReport(userId, year) {
    return http.get(`/report/ai/${userId}/year/${year}`)
  }
}
