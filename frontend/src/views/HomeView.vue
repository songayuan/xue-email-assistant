<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <div v-if="loading" class="text-center py-10">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">Loading...</p>
          </div>
          
          <div v-else-if="noAccounts" class="text-center py-10">
            <div class="mx-auto">
              <i class="el-icon-email text-5xl text-gray-400"></i>
            </div>
            <h2 class="mt-2 text-lg font-medium text-gray-900">No email accounts</h2>
            <p class="mt-1 text-gray-500">Get started by adding your first email account</p>
            <div class="mt-6">
              <router-link to="/import" class="btn btn-primary">
                Add email account
              </router-link>
            </div>
          </div>
          
          <div v-else class="space-y-6">
            <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
            
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <!-- Email stats -->
              <div class="bg-white overflow-hidden shadow rounded-lg">
                <div class="p-5">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 bg-primary-500 rounded-md p-3">
                      <i class="el-icon-message text-white"></i>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">
                          Unread Emails
                        </dt>
                        <dd>
                          <div class="text-lg font-medium text-gray-900">
                            {{ unreadCount }}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div class="bg-gray-50 px-5 py-3">
                  <div class="text-sm">
                    <router-link to="/emails" class="font-medium text-primary-600 hover:text-primary-500">
                      View all
                    </router-link>
                  </div>
                </div>
              </div>
              
              <!-- Account stats -->
              <div class="bg-white overflow-hidden shadow rounded-lg">
                <div class="p-5">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                      <i class="el-icon-user text-white"></i>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">
                          Email Accounts
                        </dt>
                        <dd>
                          <div class="text-lg font-medium text-gray-900">
                            {{ accounts.length }}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div class="bg-gray-50 px-5 py-3">
                  <div class="text-sm">
                    <router-link to="/accounts" class="font-medium text-primary-600 hover:text-primary-500">
                      Manage accounts
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Recent emails section -->
            <div class="bg-white shadow overflow-hidden sm:rounded-md mt-6">
              <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Recent Emails
                </h3>
                <router-link to="/emails" class="text-sm font-medium text-primary-600 hover:text-primary-500">
                  View all
                </router-link>
              </div>
              <ul role="list" class="divide-y divide-gray-200">
                <li v-for="email in recentEmails" :key="email.id">
                  <router-link :to="`/emails/${email.id}`" class="block hover:bg-gray-50">
                    <div class="px-4 py-4 sm:px-6">
                      <div class="flex items-center justify-between">
                        <p class="text-sm font-medium text-primary-600 truncate" :class="{ 'font-bold': !email.is_read }">
                          {{ email.subject || '(No subject)' }}
                        </p>
                        <div class="ml-2 flex-shrink-0 flex">
                          <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                             :class="email.is_read ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                            {{ email.is_read ? 'Read' : 'Unread' }}
                          </p>
                        </div>
                      </div>
                      <div class="mt-2 sm:flex sm:justify-between">
                        <div class="sm:flex">
                          <p class="flex items-center text-sm text-gray-500">
                            From: {{ email.sender }}
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
                <li v-if="recentEmails.length === 0" class="px-4 py-6 text-center text-gray-500">
                  No emails found
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
import { computed, onMounted, ref } from 'vue'
import { useEmailStore } from '@/store/emails'
import { useEmailAccountsStore } from '@/store/emailAccounts'
import NavBar from '@/components/NavBar.vue'

const emailStore = useEmailStore()
const accountsStore = useEmailAccountsStore()

const loading = ref(true)

const accounts = computed(() => accountsStore.accounts)
const noAccounts = computed(() => !loading.value && accounts.value.length === 0)
const unreadCount = computed(() => emailStore.unreadCount)
const recentEmails = computed(() => emailStore.emails.slice(0, 5))

onMounted(async () => {
  loading.value = true
  
  try {
    // Fetch accounts first
    await accountsStore.fetchAccounts()
    
    // Then fetch emails if there are accounts
    if (accounts.value.length > 0) {
      await emailStore.fetchEmails()
      emailStore.connectWebSocket()
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
})
</script> 