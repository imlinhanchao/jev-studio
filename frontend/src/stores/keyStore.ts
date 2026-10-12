import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { APIKeyItem, KeyCreatePayload, KeyCreatedResponse, KeyUpdatePayload } from '@/types/key'
import { fetchKeys, createKey as apiCreateKey, updateKey as apiUpdateKey, deleteKey as apiDeleteKey } from '@/api/keys'
import { setClientApiKey } from '@/api/client'

export const useKeyStore = defineStore('keys', () => {
  const keys = ref<APIKeyItem[]>([])
  const loading = ref(false)
  const activePlaygroundKey = ref<string>(localStorage.getItem('jev_active_key') || '')

  function setActivePlaygroundKey(key: string) {
    activePlaygroundKey.value = key
    localStorage.setItem('jev_active_key', key)
    setClientApiKey(key || null)
  }

  async function loadKeys() {
    loading.value = true
    try {
      keys.value = await fetchKeys()
      // If no active key is chosen and we have keys, default to the first one's prefix or demo
      if (!activePlaygroundKey.value && keys.value.length > 0) {
        // We might not have raw key unless user created it, but master demo key is known
        const demo = keys.value.find(k => k.name.includes('Developer') || k.name.includes('Master'))
        if (demo) {
          setActivePlaygroundKey('jev-live-demo-master-key-2026')
        }
      }
    } catch (e) {
      console.error('Failed to load keys:', e)
    } finally {
      loading.value = false
    }
  }

  async function addKey(payload: KeyCreatePayload): Promise<KeyCreatedResponse> {
    const created = await apiCreateKey(payload)
    await loadKeys()
    return created
  }

  async function toggleKeyActive(id: number, currentStatus: boolean) {
    await apiUpdateKey(id, { is_active: !currentStatus })
    await loadKeys()
  }

  async function updateKeyDetails(id: number, payload: KeyUpdatePayload) {
    await apiUpdateKey(id, payload)
    await loadKeys()
  }

  async function removeKey(id: number) {
    await apiDeleteKey(id)
    await loadKeys()
  }

  return {
    keys,
    loading,
    activePlaygroundKey,
    setActivePlaygroundKey,
    loadKeys,
    addKey,
    toggleKeyActive,
    updateKeyDetails,
    removeKey,
  }
})
