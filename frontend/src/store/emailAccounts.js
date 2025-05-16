import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_URL = '/api/v1'

export const useEmailAccountsStore = defineStore('emailAccounts', () => {
  // State
  const accounts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Actions
  async function fetchAccounts() {
    loading.value = true
    error.value = null
    
    try {
      const authStore = useAuthStore()
      
      const response = await axios.get(`${API_URL}/email-accounts`, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      accounts.value = response.data
    } catch (e) {
      error.value = e.message || 'Error fetching accounts'
      console.error('Error fetching accounts:', e)
    } finally {
      loading.value = false
    }
  }
  
  async function addAccount(emailAddress, refreshToken, clientId) {
    loading.value = true
    error.value = null
    
    try {
      const authStore = useAuthStore()
      
      const response = await axios.post(`${API_URL}/email-accounts`, {
        email_address: emailAddress,
        refresh_token: refreshToken,
        client_id: clientId
      }, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      accounts.value.push(response.data)
      return { success: true, data: response.data }
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error adding account'
      console.error('Error adding account:', e)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  async function bulkImport(emailAccounts) {
    loading.value = true
    error.value = null
    
    try {
      const authStore = useAuthStore()
      
      const response = await axios.post(`${API_URL}/email-accounts/bulk-import`, {
        email_accounts: emailAccounts
      }, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      // Add new accounts to the list
      const newAccounts = response.data
      accounts.value = [...accounts.value, ...newAccounts]
      
      return { success: true, count: newAccounts.length }
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error importing accounts'
      console.error('Error importing accounts:', e)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  async function deleteAccount(accountId) {
    try {
      const authStore = useAuthStore()
      
      await axios.delete(`${API_URL}/email-accounts/${accountId}`, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      // Remove account from the list
      accounts.value = accounts.value.filter(a => a.id !== accountId)
      
      return { success: true }
    } catch (e) {
      console.error('Error deleting account:', e)
      return { 
        success: false, 
        error: e.response?.data?.detail || e.message || 'Error deleting account'
      }
    }
  }
  
  async function syncAccount(accountId) {
    try {
      const authStore = useAuthStore()
      
      const response = await axios.post(`${API_URL}/email-accounts/${accountId}/sync`, {}, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })
      
      return { success: true, data: response.data }
    } catch (e) {
      console.error('Error syncing account:', e)
      return { 
        success: false, 
        error: e.response?.data?.detail || e.message || 'Error syncing account'
      }
    }
  }
  
  async function syncAllAccounts() {
    if (!accounts.value.length) {
      return { success: false, error: "No accounts to sync" }
    }
    
    const results = []
    let allSuccess = true
    
    for (const account of accounts.value) {
      const result = await syncAccount(account.id)
      results.push({
        account: account.email_address,
        success: result.success,
        error: result.error || null
      })
      
      if (!result.success) {
        allSuccess = false
      }
    }
    
    return { 
      success: allSuccess, 
      results,
      count: results.length
    }
  }
  
  return {
    accounts,
    loading,
    error,
    fetchAccounts,
    addAccount,
    bulkImport,
    deleteAccount,
    syncAccount,
    syncAllAccounts
  }
}) 