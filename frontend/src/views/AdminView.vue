<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <h1 class="text-2xl font-semibold text-gray-900 mb-4">管理员控制台</h1>
          
          <div v-if="!isAdmin" class="text-center py-10">
            <div class="mx-auto">
              <i class="el-icon-warning text-5xl text-yellow-500"></i>
            </div>
            <h2 class="mt-2 text-lg font-medium text-gray-900">权限不足</h2>
            <p class="mt-1 text-gray-500">您需要管理员权限来访问此页面</p>
          </div>
          
          <div v-else>
            <!-- 用户管理 -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
              <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  用户管理
                </h3>
              </div>
              <div class="bg-white">
                <div v-if="loading" class="text-center py-10">
                  <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto"></div>
                  <p class="mt-4 text-gray-600">加载中...</p>
                </div>
                <div v-else>
                  <p class="p-4 text-gray-500">功能待开发</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import NavBar from '@/components/NavBar.vue'

const authStore = useAuthStore()
const loading = ref(false)
const isAdmin = computed(() => authStore.isAdmin)
</script>
