<template>
  <div>
    <NavBar />
    
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-4">
          <div class="max-w-3xl mx-auto">
            <h1 class="text-2xl font-semibold text-gray-900 mb-6">Import Email Accounts</h1>
            
            <!-- Bulk Import Form -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
              <div class="px-4 py-5 sm:p-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Bulk Import
                </h3>
                <div class="mt-2 max-w-xl text-sm text-gray-500">
                  <p>
                    Enter multiple email accounts in the format: <br>
                    <code class="bg-gray-100 px-2 py-1 rounded">email----password----refreshToken----clientId</code>
                  </p>
                  <p class="mt-2">
                    Each account should be on a new line.
                  </p>
                </div>
                <div v-if="bulkImportError" class="mt-4 text-sm text-red-600">
                  {{ bulkImportError }}
                </div>
                <div v-if="bulkImportSuccess" class="mt-4 text-sm text-green-600">
                  Successfully imported {{ bulkImportSuccess }} email accounts.
                </div>
                <div class="mt-5">
                  <textarea
                    v-model="bulkImportText"
                    rows="8"
                    class="form-input block w-full resize-none"
                    placeholder="email----password----refreshToken----clientId"
                  ></textarea>
                </div>
                <div class="mt-5">
                  <button 
                    @click="handleBulkImport" 
                    type="button" 
                    class="btn btn-primary"
                    :disabled="bulkImportLoading"
                  >
                    {{ bulkImportLoading ? 'Importing...' : 'Import Accounts' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Single Account Form -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Add Single Account
                </h3>
                <div class="mt-2 max-w-xl text-sm text-gray-500">
                  <p>
                    Add a single email account with detailed information.
                  </p>
                </div>
                <div v-if="singleAccountError" class="mt-4 text-sm text-red-600">
                  {{ singleAccountError }}
                </div>
                <div v-if="singleAccountSuccess" class="mt-4 text-sm text-green-600">
                  Successfully added the email account.
                </div>
                <div class="mt-5 grid grid-cols-1 gap-6">
                  <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                    <input 
                      type="email" 
                      id="email" 
                      v-model="singleAccount.email" 
                      placeholder="email@example.com" 
                      class="form-input mt-1"
                    />
                  </div>
                  <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                    <input 
                      type="password" 
                      id="password" 
                      v-model="singleAccount.password" 
                      placeholder="Password" 
                      class="form-input mt-1"
                    />
                  </div>
                  <div>
                    <label for="refreshToken" class="block text-sm font-medium text-gray-700">Refresh Token</label>
                    <textarea 
                      id="refreshToken" 
                      v-model="singleAccount.refreshToken" 
                      placeholder="Refresh Token" 
                      rows="3" 
                      class="form-input mt-1"
                    ></textarea>
                  </div>
                  <div>
                    <label for="clientId" class="block text-sm font-medium text-gray-700">Client ID</label>
                    <input 
                      type="text" 
                      id="clientId" 
                      v-model="singleAccount.clientId" 
                      placeholder="Client ID" 
                      class="form-input mt-1"
                    />
                  </div>
                </div>
                <div class="mt-5">
                  <button 
                    @click="handleSingleAccountAdd" 
                    type="button" 
                    class="btn btn-primary"
                    :disabled="singleAccountLoading"
                  >
                    {{ singleAccountLoading ? 'Adding...' : 'Add Account' }}
                  </button>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEmailAccountsStore } from '@/store/emailAccounts'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const accountsStore = useEmailAccountsStore()

// Bulk Import
const bulkImportText = ref('')
const bulkImportLoading = ref(false)
const bulkImportError = ref('')
const bulkImportSuccess = ref(null)

// Single Account
const singleAccount = ref({
  email: '',
  password: '',
  refreshToken: '',
  clientId: ''
})
const singleAccountLoading = ref(false)
const singleAccountError = ref('')
const singleAccountSuccess = ref(false)

async function handleBulkImport() {
  if (!bulkImportText.value.trim()) {
    bulkImportError.value = 'Please enter at least one email account'
    return
  }
  
  // Split by newlines and filter out empty lines
  const accounts = bulkImportText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line)
  
  bulkImportLoading.value = true
  bulkImportError.value = ''
  bulkImportSuccess.value = null
  
  try {
    const result = await accountsStore.bulkImport(accounts)
    
    if (result.success) {
      bulkImportSuccess.value = result.count
      bulkImportText.value = ''
    } else {
      bulkImportError.value = result.error || 'Failed to import accounts'
    }
  } catch (e) {
    bulkImportError.value = e.message || 'An error occurred'
    console.error('Bulk import error:', e)
  } finally {
    bulkImportLoading.value = false
  }
}

async function handleSingleAccountAdd() {
  if (!singleAccount.value.email || !singleAccount.value.password || !singleAccount.value.refreshToken || !singleAccount.value.clientId) {
    singleAccountError.value = 'Please fill out all fields'
    return
  }
  
  singleAccountLoading.value = true
  singleAccountError.value = ''
  singleAccountSuccess.value = false
  
  try {
    const result = await accountsStore.addAccount(
      singleAccount.value.email,
      singleAccount.value.refreshToken,
      singleAccount.value.clientId
    )
    
    if (result.success) {
      singleAccountSuccess.value = true
      singleAccount.value = {
        email: '',
        password: '',
        refreshToken: '',
        clientId: ''
      }
    } else {
      singleAccountError.value = result.error || 'Failed to add account'
    }
  } catch (e) {
    singleAccountError.value = e.message || 'An error occurred'
    console.error('Add account error:', e)
  } finally {
    singleAccountLoading.value = false
  }
}
</script> 