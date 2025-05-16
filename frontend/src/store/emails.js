import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_URL = '/api/v1'

export const useEmailStore = defineStore('emails', () => {
  // State
  const emails = ref([])
  const currentEmail = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const websocket = ref(null)
  
  // Getters
  const unreadCount = computed(() => {
    return emails.value.filter(email => !email.is_read).length
  })
  
  const categoryCounts = computed(() => {
    const counts = {}
    emails.value.forEach(email => {
      if (!counts[email.category]) {
        counts[email.category] = 0
      }
      counts[email.category]++
    })
    return counts
  })
  
  // Actions
  async function fetchEmails(accountId = null, isRead = null, category = null) {
    loading.value = true
    error.value = null
    
    try {
      const authStore = useAuthStore()
      
      let url = `${API_URL}/emails`
      const params = {}
      
      if (accountId) {
        params.account_id = accountId
      }
      
      if (isRead !== null) {
        params.is_read = isRead
      }
      
      if (category) {
        params.category = category
      }
      
      const response = await axios.get(url, {
        params,
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      emails.value = response.data
    } catch (e) {
      error.value = e.message || 'Error fetching emails'
      console.error('Error fetching emails:', e)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchEmailById(emailId) {
    loading.value = true
    error.value = null
    currentEmail.value = null
    
    try {
      const authStore = useAuthStore()
      
      const response = await axios.get(`${API_URL}/emails/${emailId}`, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      currentEmail.value = response.data
    } catch (e) {
      error.value = e.message || 'Error fetching email'
      console.error('Error fetching email:', e)
    } finally {
      loading.value = false
    }
  }
  
  async function markAsRead(emailId) {
    try {
      const authStore = useAuthStore()
      
      const response = await axios.patch(`${API_URL}/emails/${emailId}/read`, {}, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      // Update email in the list
      const index = emails.value.findIndex(e => e.id === emailId)
      if (index !== -1) {
        emails.value[index] = { ...emails.value[index], is_read: true }
      }
      
      // Update current email if it's the one being viewed
      if (currentEmail.value && currentEmail.value.id === emailId) {
        currentEmail.value = { ...currentEmail.value, is_read: true }
      }
      
      return response.data
    } catch (e) {
      console.error('Error marking email as read:', e)
      throw e
    }
  }
  
  async function markAsUnread(emailId) {
    try {
      const authStore = useAuthStore()
      
      const response = await axios.patch(`${API_URL}/emails/${emailId}/unread`, {}, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      // Update email in the list
      const index = emails.value.findIndex(e => e.id === emailId)
      if (index !== -1) {
        emails.value[index] = { ...emails.value[index], is_read: false }
      }
      
      // Update current email if it's the one being viewed
      if (currentEmail.value && currentEmail.value.id === emailId) {
        currentEmail.value = { ...currentEmail.value, is_read: false }
      }
      
      return response.data
    } catch (e) {
      console.error('Error marking email as unread:', e)
      throw e
    }
  }
  
  async function updateCategory(emailId, category) {
    try {
      const authStore = useAuthStore()
      
      const response = await axios.patch(`${API_URL}/emails/${emailId}/category`, 
        { category }, 
        {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        }
      )
      
      // Update email in the list
      const index = emails.value.findIndex(e => e.id === emailId)
      if (index !== -1) {
        emails.value[index] = { ...emails.value[index], category }
      }
      
      // Update current email if it's the one being viewed
      if (currentEmail.value && currentEmail.value.id === emailId) {
        currentEmail.value = { ...currentEmail.value, category }
      }
      
      return response.data
    } catch (e) {
      console.error('Error updating email category:', e)
      throw e
    }
  }
  
  function connectWebSocket() {
    const authStore = useAuthStore()
    
    if (authStore.user && authStore.isAuthenticated) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws/${authStore.user.id}`
      
      websocket.value = new WebSocket(wsUrl)
      
      websocket.value.onopen = () => {
        console.log('WebSocket connected')
      }
      
      websocket.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'new_email') {
          // Notify user of new email
          fetchEmails()
        }
      }
      
      websocket.value.onclose = () => {
        console.log('WebSocket disconnected')
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000)
      }
    }
  }
  
  function disconnect() {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
    }
  }
  
  return {
    emails,
    currentEmail,
    loading,
    error,
    unreadCount,
    categoryCounts,
    fetchEmails,
    fetchEmailById,
    markAsRead,
    markAsUnread,
    updateCategory,
    connectWebSocket,
    disconnect
  }
}) 