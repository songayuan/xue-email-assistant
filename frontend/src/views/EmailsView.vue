<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-center mb-4">
            <h1 class="text-2xl font-semibold text-gray-900">邮件列表</h1>
            
            <!-- Account selector -->
            <div class="flex items-center space-x-2">
              <label class="text-sm text-gray-700">账户:</label>
              <select 
                v-model="selectedAccount" 
                @change="handleAccountChange"
                class="form-select rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
              >
                <option :value="null">所有账户</option>
                <option v-for="account in emailAccounts" :key="account.id" :value="account.id">
                  {{ account.email_address }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- Email categories -->
          <EmailCategories 
            :selectedCategory="selectedCategory" 
            :emailCounts="emailStore.categoryCounts"
            @select-category="handleCategorySelect" 
          />
          
          <div v-if="loading" class="text-center py-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">加载中...</p>
          </div>
          
          <div v-else-if="emails.length === 0" class="text-center py-10">
            <div class="mx-auto">
              <i class="el-icon-email text-5xl text-gray-400"></i>
            </div>
            <h2 class="mt-2 text-lg font-medium text-gray-900">没有邮件</h2>
            <p class="mt-1 text-gray-500">{{ getEmptyMessage() }}</p>
          </div>
          
          <div v-else>
            <!-- 邮件列表 -->
            <div class="bg-white shadow overflow-hidden sm:rounded-md">
              <ul role="list" class="divide-y divide-gray-200">
                <li v-for="email in emails" :key="email.id">
                  <router-link :to="`/emails/${email.id}`" class="block hover:bg-gray-50">
                    <div class="px-4 py-4 sm:px-6">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center">
                          <span class="w-2 h-2 rounded-full mr-2" :class="getCategoryColor(email.category)"></span>
                          <p class="text-sm font-medium text-primary-600 truncate" :class="{ 'font-bold': !email.is_read }">
                            {{ email.subject || '(无主题)' }}
                          </p>
                        </div>
                        <div class="ml-2 flex-shrink-0 flex space-x-2">
                          <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                            {{ getCategoryLabel(email.category) }}
                          </span>
                          <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                             :class="email.is_read ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                            {{ email.is_read ? '已读' : '未读' }}
                          </p>
                        </div>
                      </div>
                      <div class="mt-2 sm:flex sm:justify-between">
                        <div class="sm:flex">
                          <p class="flex items-center text-sm text-gray-500">
                            <span v-if="!selectedAccount" class="mr-1 text-xs bg-blue-100 text-blue-800 px-1 rounded">
                              {{ getAccountEmail(email.email_account_id) }}
                            </span>
                            发件人: {{ email.sender }}
                          </p>
                        </div>
                        <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>
                            {{ new Date(email.date_received).toLocaleString() }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useEmailStore } from '@/store/emails'
import { useEmailAccountsStore } from '@/store/emailAccounts'
import NavBar from '@/components/NavBar.vue'
import EmailCategories from '@/components/EmailCategories.vue'

const route = useRoute()
const emailStore = useEmailStore()
const accountsStore = useEmailAccountsStore()

const selectedCategory = ref(null)
const selectedAccount = ref(null)
const loading = computed(() => emailStore.loading)
const emails = computed(() => emailStore.emails)
const emailAccounts = computed(() => accountsStore.accounts)

// Get the current account selection from query params on mount
onMounted(async () => {
  if (route.query.account) {
    selectedAccount.value = route.query.account
  }
  
  // Load accounts first
  await accountsStore.fetchAccounts()
  
  // Then load emails with the appropriate filter
  await emailStore.fetchEmails(selectedAccount.value, null, selectedCategory.value)
  
  // Set up websocket connection
  emailStore.connectWebSocket()
})

// Map account IDs to email addresses
function getAccountEmail(accountId) {
  const account = emailAccounts.value.find(a => a.id === accountId)
  return account ? account.email_address : '未知账户'
}

// Category helpers
function getCategoryLabel(category) {
  const categories = {
    'inbox': '收件箱',
    'important': '重要',
    'social': '社交',
    'promotions': '促销',
    'updates': '更新',
    'forums': '论坛',
    'spam': '垃圾邮件'
  }
  return categories[category] || category
}

function getCategoryColor(category) {
  const colors = {
    'inbox': 'bg-blue-500',
    'important': 'bg-red-500',
    'social': 'bg-green-500',
    'promotions': 'bg-purple-500',
    'updates': 'bg-yellow-500',
    'forums': 'bg-indigo-500',
    'spam': 'bg-gray-500'
  }
  return colors[category] || 'bg-blue-500'
}

function getEmptyMessage() {
  let message = ''
  
  if (selectedAccount.value) {
    const account = emailAccounts.value.find(a => a.id === selectedAccount.value)
    message += `在账户 ${account ? account.email_address : ''} 中`
  } else {
    message += '所有账户中'
  }
  
  if (selectedCategory.value) {
    message += `的 ${getCategoryLabel(selectedCategory.value)} 分类中没有找到邮件`
  } else {
    message += '没有找到邮件'
  }
  
  return message
}

function handleCategorySelect(category) {
  selectedCategory.value = category
  emailStore.fetchEmails(selectedAccount.value, null, category)
}

function handleAccountChange() {
  emailStore.fetchEmails(selectedAccount.value, null, selectedCategory.value)
}
</script>
