<template>
  <div class="min-h-screen bg-gray-50">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  // Check if user is authenticated
  const token = authStore.token
  if (!token && !['login', 'register'].includes(router.currentRoute.value.name)) {
    router.push({ name: 'login' })
  }
})
</script> 