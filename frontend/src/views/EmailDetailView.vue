<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <div v-if="loading" class="text-center py-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">加载中...</p>
          </div>
          
          <div v-else-if="!currentEmail" class="text-center py-10">
            <div class="mx-auto">
              <i class="el-icon-warning text-5xl text-yellow-500"></i>
            </div>
            <h2 class="mt-2 text-lg font-medium text-gray-900">邮件不存在</h2>
            <p class="mt-1 text-gray-500">未找到请求的邮件或您没有权限查看</p>
            <div class="mt-6">
              <router-link to="/emails" class="btn btn-primary">
                返回邮件列表
              </router-link>
            </div>
          </div>
          
          <div v-else>
            <!-- 邮件详情 -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
              <!-- 邮件头部 -->
              <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
                <div>
                  <h3 class="text-lg leading-6 font-medium text-gray-900">
                    {{ currentEmail.subject || '(无主题)' }}
                  </h3>
                  <p class="mt-1 max-w-2xl text-sm text-gray-500">
                    {{ new Date(currentEmail.date_received).toLocaleString() }}
                  </p>
                </div>
                <div class="flex space-x-2">
                  <el-dropdown @command="handleCategoryChange">
                    <span class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none cursor-pointer">
                      分类: {{ getCategoryLabel(currentEmail.category) }}
                      <i class="el-icon-arrow-down ml-1"></i>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-for="category in categories" :key="category.value" :command="category.value">
                          <div class="flex items-center">
                            <span class="w-2 h-2 rounded-full mr-2" :class="category.color"></span>
                            {{ category.label }}
                          </div>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <button 
                    v-if="currentEmail.is_read" 
                    @click="markAsUnread" 
                    class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:outline-none"
                  >
                    标记为未读
                  </button>
                  <button 
                    v-else
                    @click="markAsRead" 
                    class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none"
                  >
                    标记为已读
                  </button>
                  <router-link 
                    to="/emails" 
                    class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none"
                  >
                    返回列表
                  </router-link>
                </div>
              </div>
              
              <!-- 邮件信息 -->
              <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
                <p class="text-sm">
                  <span class="font-medium text-gray-500">发件人: </span>
                  {{ currentEmail.sender }}
                </p>
                <p class="text-sm mt-1">
                  <span class="font-medium text-gray-500">收件人: </span>
                  {{ currentEmail.recipients }}
                </p>
                <p class="text-sm mt-1">
                  <span class="font-medium text-gray-500">账户: </span>
                  <span v-if="emailAccount" class="text-primary-600">
                    <router-link :to="`/emails?account=${currentEmail.email_account_id}`">
                      {{ emailAccount.email_address }} (查看该账户所有邮件)
                    </router-link>
                  </span>
                  <span v-else>未知账户</span>
                </p>
                <p class="text-sm mt-1">
                  <span class="font-medium text-gray-500">分类: </span>
                  <span class="inline-flex items-center">
                    <span class="w-2 h-2 rounded-full mr-1" :class="getCategoryColor(currentEmail.category)"></span>
                    {{ getCategoryLabel(currentEmail.category) }}
                  </span>
                </p>
              </div>
              
              <!-- 邮件内容 -->
              <div class="px-4 py-5 sm:p-6">
                <div v-if="currentEmail.body_html" v-html="currentEmail.body_html"></div>
                <div v-else-if="currentEmail.body_text" class="whitespace-pre-wrap">{{ currentEmail.body_text }}</div>
                <div v-else class="text-gray-500">无内容</div>
              </div>
              
              <!-- 附件 -->
              <div v-if="currentEmail.attachments && currentEmail.attachments.length > 0" class="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <h4 class="text-sm font-medium text-gray-500">附件:</h4>
                <ul class="mt-2 space-y-2">
                  <li v-for="attachment in currentEmail.attachments" :key="attachment.id" class="flex items-center">
                    <span class="text-sm">{{ attachment.filename }} ({{ formatFileSize(attachment.size) }})</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useEmailStore } from '@/store/emails'
import { useEmailAccountsStore } from '@/store/emailAccounts'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const emailStore = useEmailStore()
const accountsStore = useEmailAccountsStore()

const loading = computed(() => emailStore.loading)
const currentEmail = computed(() => emailStore.currentEmail)
const emailId = computed(() => route.params.id)
const emailAccount = computed(() => {
  if (!currentEmail.value || !accountsStore.accounts.length) return null
  return accountsStore.accounts.find(a => a.id === currentEmail.value.email_account_id)
})

// Email categories
const categories = [
  { label: '收件箱', value: 'inbox', color: 'bg-blue-500' },
  { label: '重要', value: 'important', color: 'bg-red-500' },
  { label: '社交', value: 'social', color: 'bg-green-500' },
  { label: '促销', value: 'promotions', color: 'bg-purple-500' },
  { label: '更新', value: 'updates', color: 'bg-yellow-500' },
  { label: '论坛', value: 'forums', color: 'bg-indigo-500' },
  { label: '垃圾邮件', value: 'spam', color: 'bg-gray-500' }
]

function getCategoryLabel(category) {
  const found = categories.find(c => c.value === category)
  return found ? found.label : category
}

function getCategoryColor(category) {
  const found = categories.find(c => c.value === category)
  return found ? found.color : 'bg-blue-500'
}

async function handleCategoryChange(category) {
  if (!currentEmail.value || currentEmail.value.category === category) return
  
  try {
    await emailStore.updateCategory(currentEmail.value.id, category)
    ElMessage({
      message: `邮件已移至 ${getCategoryLabel(category)}`,
      type: 'success'
    })
  } catch (e) {
    ElMessage({
      message: '移动邮件失败',
      type: 'error'
    })
  }
}

onMounted(async () => {
  // Fetch accounts first so we can display account info
  await accountsStore.fetchAccounts()
  
  // Then fetch the email
  if (emailId.value) {
    await emailStore.fetchEmailById(emailId.value)
  }
})

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function markAsRead() {
  if (!currentEmail.value) return
  
  try {
    await emailStore.markAsRead(currentEmail.value.id)
    ElMessage({
      message: '邮件已标记为已读',
      type: 'success'
    })
  } catch (e) {
    ElMessage({
      message: '操作失败',
      type: 'error'
    })
  }
}

async function markAsUnread() {
  if (!currentEmail.value) return
  
  try {
    await emailStore.markAsUnread(currentEmail.value.id)
    ElMessage({
      message: '邮件已标记为未读',
      type: 'success'
    })
  } catch (e) {
    ElMessage({
      message: '操作失败',
      type: 'error'
    })
  }
}
</script>
