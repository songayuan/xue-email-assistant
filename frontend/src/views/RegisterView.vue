<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create an account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Join Xue Email Assistant
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div v-if="error" class="rounded-md bg-red-50 p-4 mb-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">{{ error }}</h3>
            </div>
          </div>
        </div>
        
        <div class="rounded-md shadow-sm space-y-3">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
            <input id="username" v-model="username" name="username" type="text" required class="form-input" placeholder="Username">
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
            <input id="email" v-model="email" name="email" type="email" required class="form-input" placeholder="Email">
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input id="password" v-model="password" name="password" type="password" required class="form-input" placeholder="Password">
          </div>
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input id="confirmPassword" v-model="confirmPassword" name="confirmPassword" type="password" required class="form-input" placeholder="Confirm Password">
          </div>
        </div>

        <div>
          <button type="submit" class="btn btn-primary w-full" :disabled="loading">
            {{ loading ? 'Creating account...' : 'Register' }}
          </button>
        </div>
        
        <div class="text-center">
          <p class="mt-2 text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">
              Sign in
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill out all fields'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.register(username.value, email.value, password.value)
    
    if (result.success) {
      // Success, redirect to login
      router.push('/login')
    } else {
      error.value = result.message || 'Registration failed'
    }
  } catch (e) {
    error.value = e.message || 'An error occurred'
    console.error('Registration error:', e)
  } finally {
    loading.value = false
  }
}
</script> 