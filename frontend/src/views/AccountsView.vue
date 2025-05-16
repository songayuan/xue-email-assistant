<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <h1 class="text-2xl font-semibold text-gray-900 mb-4">邮箱账户管理</h1>
          
          <div v-if="loading" class="text-center py-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">加载中...</p>
          </div>
          
          <div v-else-if="accounts.length === 0" class="text-center py-10">
            <div class="mx-auto">
              <i class="el-icon-user text-5xl text-gray-400"></i>
            </div>
            <h2 class="mt-2 text-lg font-medium text-gray-900">没有邮箱账户</h2>
            <p class="mt-1 text-gray-500">通过导入页面添加您的第一个邮箱账户</p>
            <div class="mt-6">
              <router-link to="/import" class="btn btn-primary">
                添加邮箱账户
              </router-link>
            </div>
          </div>
          
          <div v-else>
            <!-- 账户列表 -->
            <div class="bg-white shadow overflow-hidden sm:rounded-md">
              <ul role="list" class="divide-y divide-gray-200">
                <li v-for="account in accounts" :key="account.id">
                  <div class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                      <p class="text-sm font-medium text-primary-600">
                        {{ account.email_address }}
                      </p>
                      <div class="ml-2 flex space-x-2">
                        <button 
                          @click="syncAccount(account.id)" 
                          class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none"
                        >
                          同步邮件
                        </button>
                        <button 
                          @click="confirmDelete(account)" 
                          class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none"
                        >
                          删除
                        </button>
                      </div>
                    </div>
                    <div class="mt-2 text-sm text-gray-500">
                      <div v-if="account.last_sync">
                        上次同步时间: {{ new Date(account.last_sync).toLocaleString() }}
                      </div>
                      <div v-else>
                        尚未同步
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>

            <!-- 操作按钮 -->
            <div class="mt-6 flex justify-between">
              <div class="flex space-x-4">
                <router-link to="/import" class="btn btn-primary">
                  添加更多账户
                </router-link>
                <button 
                  @click="syncAllAccounts" 
                  class="btn btn-secondary"
                  :disabled="syncingAll"
                >
                  {{ syncingAll ? '同步中...' : '同步所有账户' }}
                </button>
              </div>
              <div>
                <router-link to="/emails" class="btn btn-outline">
                  查看所有邮件
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除邮箱账户 {{ accountToDelete?.email_address }} 吗? 所有关联的邮件也会被删除。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="deleteAccount">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useEmailAccountsStore } from '@/store/emailAccounts'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'

const accountsStore = useEmailAccountsStore()

const loading = computed(() => accountsStore.loading)
const accounts = computed(() => accountsStore.accounts)
const showDeleteDialog = ref(false)
const accountToDelete = ref(null)
const syncingAll = ref(false)

onMounted(async () => {
  await accountsStore.fetchAccounts()
})

function confirmDelete(account) {
  accountToDelete.value = account
  showDeleteDialog.value = true
}

async function deleteAccount() {
  if (!accountToDelete.value) return
  
  const result = await accountsStore.deleteAccount(accountToDelete.value.id)
  showDeleteDialog.value = false
  
  if (result.success) {
    ElMessage({
      message: '账户删除成功',
      type: 'success'
    })
  } else {
    ElMessage({
      message: result.error || '删除失败',
      type: 'error'
    })
  }
}

async function syncAccount(accountId) {
  const result = await accountsStore.syncAccount(accountId)
  
  if (result.success) {
    ElMessage({
      message: '同步已启动，请稍候',
      type: 'success'
    })
  } else {
    ElMessage({
      message: result.error || '同步失败',
      type: 'error'
    })
  }
}

async function syncAllAccounts() {
  syncingAll.value = true
  
  try {
    const result = await accountsStore.syncAllAccounts()
    
    if (result.success) {
      ElMessage({
        message: `已成功开始同步 ${result.count} 个账户`,
        type: 'success'
      })
    } else {
      // If we have partial success, show mixed result
      if (result.results && result.results.length > 0) {
        const successCount = result.results.filter(r => r.success).length
        
        ElMessage({
          message: `已同步 ${successCount}/${result.count} 个账户`,
          type: 'warning'
        })
      } else {
        ElMessage({
          message: result.error || '同步失败',
          type: 'error'
        })
      }
    }
  } catch (error) {
    ElMessage({
      message: '同步过程中发生错误',
      type: 'error'
    })
    console.error('Sync all error:', error)
  } finally {
    syncingAll.value = false
  }
}
</script>
