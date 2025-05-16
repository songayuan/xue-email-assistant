import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = '/api/v1'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(Cookies.get('token') || null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  // Actions
  async function login(username, password) {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await axios.post(`${API_URL}/auth/login`, formData)
      const data = response.data
      
      token.value = data.access_token
      Cookies.set('token', data.access_token, { expires: 7 }) // 7 days
      
      await fetchUserInfo()
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || 'An error occurred during login'
      }
    }
  }
  
  async function register(username, email, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        username,
        email,
        password
      })
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Registration error:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || 'An error occurred during registration'
      }
    }
  }
  
  async function fetchUserInfo() {
    if (!token.value) return
    
    try {
      const response = await axios.get(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      
      user.value = response.data
    } catch (error) {
      console.error('Error fetching user info:', error)
      logout()
    }
  }
  
  function logout() {
    user.value = null
    token.value = null
    Cookies.remove('token')
  }
  
  // Initialize
  if (token.value) {
    fetchUserInfo()
  }
  
  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchUserInfo,
    logout
  }
})