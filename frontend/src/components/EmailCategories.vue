<template>
  <div class="bg-white shadow overflow-hidden sm:rounded-md mb-4">
    <div class="px-4 py-2 sm:px-6 flex space-x-2 overflow-x-auto whitespace-nowrap">
      <button
        v-for="category in categories"
        :key="category.value"
        @click="$emit('select-category', category.value)"
        :class="[
          'px-3 py-1 rounded-full text-sm font-medium',
          selectedCategory === category.value
            ? 'bg-primary-100 text-primary-800 border border-primary-300'
            : 'bg-gray-100 text-gray-800 border border-gray-200 hover:bg-gray-200'
        ]"
      >
        <span class="flex items-center">
          <i :class="category.icon" class="mr-1"></i>
          {{ category.label }}
          <span 
            v-if="emailCounts && emailCounts[category.value]" 
            class="ml-1 bg-gray-200 text-gray-700 rounded-full px-2 text-xs"
          >
            {{ emailCounts[category.value] }}
          </span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineEmits(['select-category'])

const props = defineProps({
  selectedCategory: {
    type: String,
    default: null
  },
  emailCounts: {
    type: Object,
    default: () => ({})
  }
})

const categories = [
  { label: '所有邮件', value: null, icon: 'el-icon-message' },
  { label: '收件箱', value: 'inbox', icon: 'el-icon-message' },
  { label: '重要', value: 'important', icon: 'el-icon-star-on' },
  { label: '社交', value: 'social', icon: 'el-icon-user' },
  { label: '促销', value: 'promotions', icon: 'el-icon-shopping-cart-full' },
  { label: '更新', value: 'updates', icon: 'el-icon-refresh' },
  { label: '论坛', value: 'forums', icon: 'el-icon-chat-dot-round' },
  { label: '垃圾邮件', value: 'spam', icon: 'el-icon-warning' }
]
</script> 