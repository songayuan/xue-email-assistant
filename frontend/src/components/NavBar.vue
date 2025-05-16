<template>
  <nav class="bg-primary-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <span class="text-white text-xl font-bold">Xue Email Assistant</span>
          </div>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <router-link 
                to="/" 
                class="text-white hover:bg-primary-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium" 
                :class="{ 'bg-primary-600': isCurrentRoute('home') }"
              >
                Dashboard
              </router-link>
              
              <!-- Email dropdown -->
              <el-dropdown>
                <span class="text-white hover:bg-primary-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium cursor-pointer"
                      :class="{ 'bg-primary-600': isCurrentRoute('emails') }">
                  Emails
                  <i class="el-icon-arrow-down ml-1"></i>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>
                      <router-link to="/emails" class="block w-full text-left">
                        All Emails
                      </router-link>
                    </el-dropdown-item>
                    <el-dropdown-item v-if="emailAccounts.length === 0" disabled>
                      <span class="text-gray-400">No accounts</span>
                    </el-dropdown-item>
                    <el-dropdown-item v-else-if="emailAccounts.length > 5" divided>
                      <router-link to="/accounts" class="block w-full text-left">
                        Manage accounts...
                      </router-link>
                    </el-dropdown-item>
                    <template v-else>
                      <el-dropdown-item
                        v-for="account in emailAccounts"
                        :key="account.id"
                        divided
                      >
                        <router-link :to="`/emails?account=${account.id}`" class="block w-full text-left">
                          {{ account.email_address }}
                        </router-link>
                      </el-dropdown-item>
                    </template>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <router-link 
                to="/accounts" 
                class="text-white hover:bg-primary-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                :class="{ 'bg-primary-600': isCurrentRoute('accounts') }"
              >
                Accounts
              </router-link>
              <router-link 
                to="/import" 
                class="text-white hover:bg-primary-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                :class="{ 'bg-primary-600': isCurrentRoute('import') }"
              >
                Import
              </router-link>
              <router-link 
                v-if="isAdmin"
                to="/admin" 
                class="text-white hover:bg-primary-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                :class="{ 'bg-primary-600': isCurrentRoute('admin') }"
              >
                Admin
              </router-link>
            </div>
          </div>
        </div>
        <div class="ml-4 flex items-center md:ml-6">
          <div class="ml-3 relative">
            <el-dropdown>
              <span class="inline-flex rounded-md">
                <button class="inline-flex items-center text-sm font-medium text-white hover:text-gray-200 focus:outline-none">
                  {{ username }}
                  <i class="el-icon-arrow-down ml-1"></i>
                </button>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>
                    <router-link to="/profile" class="block w-full text-left">
                      Profile
                    </router-link>
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleLogout">
                    Sign out
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        <div class="-mr-2 flex md:hidden">
          <!-- Mobile menu button -->
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen" 
            class="bg-primary-600 inline-flex items-center justify-center p-2 rounded-md text-white hover:text-white hover:bg-primary-500 focus:outline-none"
          >
            <i class="el-icon-menu"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="isMobileMenuOpen" class="md:hidden">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <router-link 
          to="/" 
          class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium"
          :class="{ 'bg-primary-600': isCurrentRoute('home') }"
        >
          Dashboard
        </router-link>
        <router-link 
          to="/emails" 
          class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium"
          :class="{ 'bg-primary-600': isCurrentRoute('emails') }"
        >
          All Emails
        </router-link>
        <!-- Mobile account-specific links -->
        <template v-if="emailAccounts.length > 0 && emailAccounts.length <= 3">
          <router-link 
            v-for="account in emailAccounts"
            :key="account.id"
            :to="`/emails?account=${account.id}`" 
            class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium pl-6"
          >
            {{ account.email_address }}
          </router-link>
        </template>
        <router-link 
          to="/accounts" 
          class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium"
          :class="{ 'bg-primary-600': isCurrentRoute('accounts') }"
        >
          Accounts
        </router-link>
        <router-link 
          to="/import" 
          class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium"
          :class="{ 'bg-primary-600': isCurrentRoute('import') }"
        >
          Import
        </router-link>
        <router-link 
          v-if="isAdmin"
          to="/admin" 
          class="text-white hover:bg-primary-600 block px-3 py-2 rounded-md text-base font-medium"
          :class="{ 'bg-primary-600': isCurrentRoute('admin') }"
        >
          Admin
        </router-link>
      </div>
      <div class="pt-4 pb-3 border-t border-primary-800">
        <div class="px-2 space-y-1">
          <router-link to="/profile" class="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-primary-600">
            Profile
          </router-link>
          <a 
            href="#"
            @click.prevent="handleLogout"
            class="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-primary-600"
          >
            Sign out
          </a>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useEmailAccountsStore } from '@/store/emailAccounts'

const router = useRouter()
const authStore = useAuthStore()
const accountsStore = useEmailAccountsStore()

const isMobileMenuOpen = ref(false)
const emailAccounts = computed(() => accountsStore.accounts)

onMounted(async () => {
  try {
    await accountsStore.fetchAccounts()
  } catch (error) {
    console.error('Error fetching email accounts for navbar:', error)
  }
})

const username = computed(() => authStore.user?.username || '')
const isAdmin = computed(() => authStore.isAdmin)

function isCurrentRoute(name) {
  return router.currentRoute.value.name === name
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script> 