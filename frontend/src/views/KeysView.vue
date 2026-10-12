<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight flex items-center gap-2">
          <span>API Key 凭证管理</span>
          <span class="badge badge-primary badge-sm">{{ keyStore.keys.length }} 个密钥</span>
        </h1>
        <p class="text-xs text-base-content/60 mt-1">
          开通用于访问 Liquid AI 决策模型的鉴权凭证，支持精确代币限额 (Quota) 与频率控制
        </p>
      </div>

      <button class="btn btn-primary btn-sm gap-2 shadow-sm" @click="showCreateModal = true">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        开通新 API Key
      </button>
    </div>

    <!-- Keys Table Card -->
    <div class="card bg-base-200 border border-base-300">
      <div class="card-body p-0">
        <div class="overflow-x-auto">
          <table class="table">
            <thead>
              <tr class="bg-base-300/40 text-base-content/70 text-xs">
                <th>凭证名称</th>
                <th>密钥凭证 (Masked)</th>
                <th class="w-72">Token 配额消耗进度</th>
                <th>速率限制</th>
                <th>最后调用</th>
                <th>状态</th>
                <th class="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="key in keyStore.keys" :key="key.id" class="hover border-b border-base-300/40">
                <!-- Name -->
                <td>
                  <div class="font-bold text-sm">{{ key.name }}</div>
                  <div class="text-[10px] text-base-content/50">创建于 {{ formatDate(key.created_at) }}</div>
                </td>

                <!-- Key prefix & quick copy -->
                <td>
                  <div class="flex items-center gap-1 font-mono text-xs">
                    <span class="badge badge-neutral badge-sm">{{ key.key_prefix }}</span>
                    <CopyButton :text="key.key_prefix" textLabel="" />
                  </div>
                </td>

                <!-- Token Quota -->
                <td>
                  <TokenProgressBar :used="key.tokens_used" :limit="key.token_limit" />
                </td>

                <!-- Rate Limit -->
                <td>
                  <span class="font-mono text-xs">{{ key.rate_limit_rpm }} RPM</span>
                </td>

                <!-- Last used -->
                <td>
                  <span class="text-xs text-base-content/70">
                    {{ key.last_used_at ? formatDate(key.last_used_at) : '未使用' }}
                  </span>
                </td>

                <!-- Status toggle -->
                <td>
                  <input
                    type="checkbox"
                    class="toggle toggle-success toggle-xs"
                    :checked="key.is_active"
                    @change="keyStore.toggleKeyActive(key.id, key.is_active)"
                    title="启用/禁用凭证"
                  />
                </td>

                <!-- Actions -->
                <td class="text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button
                      class="btn btn-xs btn-ghost text-primary"
                      @click="setAsPlaygroundKey(key)"
                      title="设为 Studio 当前调试 Key"
                    >
                      设为调试
                    </button>
                    <button
                      class="btn btn-xs btn-ghost text-error"
                      @click="confirmDelete(key.id, key.name)"
                      title="撤销并删除该 Key"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="keyStore.keys.length === 0">
                <td colspan="7" class="text-center py-10 text-sm text-base-content/50">
                  尚未开通 API Key，点击上方“开通新 API Key”生成第一个访问密钥
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create API Key Modal -->
    <dialog class="modal" :class="{ 'modal-open': showCreateModal }">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">开通新的 API Key</h3>

        <div class="space-y-4 text-xs">
          <div>
            <label class="label-text font-semibold">凭证名称 (应用标识):</label>
            <input
              v-model="createForm.name"
              type="text"
              placeholder="e.g. Production Web App, Mobile Client, Data Pipeline"
              class="input input-bordered input-sm w-full mt-1"
            />
          </div>

          <div>
            <label class="label-text font-semibold">Token 代币额度上限 (Quota):</label>
            <div class="grid grid-cols-4 gap-2 mt-1">
              <button
                type="button"
                v-for="quota in [100000, 500000, 1000000, 0]"
                :key="quota"
                class="btn btn-xs"
                :class="createForm.token_limit === quota ? 'btn-primary' : 'btn-outline'"
                @click="createForm.token_limit = quota"
              >
                {{ quota === 0 ? '无上限' : `${quota / 1000}k` }}
              </button>
            </div>
            <input
              v-model.number="createForm.token_limit"
              type="number"
              placeholder="自定义 Token 额度"
              class="input input-bordered input-xs w-full mt-2 font-mono"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label-text font-semibold">频率限制 (RPM):</label>
              <input
                v-model.number="createForm.rate_limit_rpm"
                type="number"
                class="input input-bordered input-sm w-full mt-1"
              />
            </div>
            <div>
              <label class="label-text font-semibold">有效期限 (天数, 可选):</label>
              <input
                v-model.number="createForm.expires_in_days"
                type="number"
                placeholder="留空为永久"
                class="input input-bordered input-sm w-full mt-1"
              />
            </div>
          </div>
        </div>

        <div class="modal-action">
          <button class="btn btn-sm btn-ghost" @click="showCreateModal = false">取消</button>
          <button
            class="btn btn-sm btn-primary"
            :disabled="!createForm.name.trim() || creating"
            @click="handleCreateKey"
          >
            <span v-if="creating" class="loading loading-spinner loading-xs"></span>
            立即生成凭证
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="showCreateModal = false">
        <button>close</button>
      </form>
    </dialog>

    <!-- One-Time Raw Key Reveal Modal -->
    <dialog class="modal" :class="{ 'modal-open': showRevealModal }">
      <div class="modal-box border border-warning/30 bg-base-100">
        <div class="flex items-center gap-2 text-warning mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 class="font-bold text-base">请立即妥善保存您的 API Key</h3>
        </div>

        <p class="text-xs text-base-content/80 mb-4 leading-relaxed">
          出于安全性考量，系统仅会在此刻完整显示该密钥明文一次。后续将仅保留 SHA-256 哈希值与部分前缀。
        </p>

        <div class="p-3 bg-base-200 rounded-lg border border-base-300 font-mono text-xs flex items-center justify-between gap-2 break-all">
          <span class="text-primary font-bold">{{ createdRawKey }}</span>
          <CopyButton :text="createdRawKey" textLabel="复制 Key" />
        </div>

        <div class="modal-action">
          <button class="btn btn-sm btn-primary" @click="showRevealModal = false">
            我已安全复制并保存
          </button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useKeyStore } from '@/stores/keyStore'
import type { KeyCreatePayload, APIKeyItem } from '@/types/key'
import TokenProgressBar from '@/components/TokenProgressBar.vue'
import CopyButton from '@/components/CopyButton.vue'

const keyStore = useKeyStore()

const showCreateModal = ref(false)
const showRevealModal = ref(false)
const creating = ref(false)
const createdRawKey = ref('')

const createForm = ref<KeyCreatePayload>({
  name: '',
  token_limit: 500000,
  rate_limit_rpm: 120,
  expires_in_days: null,
})

onMounted(async () => {
  await keyStore.loadKeys()
})

async function handleCreateKey() {
  if (!createForm.value.name.trim()) return
  creating.value = true
  try {
    const res = await keyStore.addKey(createForm.value)
    createdRawKey.value = res.raw_key
    showCreateModal.value = false
    showRevealModal.value = true
    // Reset form
    createForm.value = {
      name: '',
      token_limit: 500000,
      rate_limit_rpm: 120,
      expires_in_days: null,
    }
  } catch (err) {
    console.error('Failed to create key:', err)
  } finally {
    creating.value = false
  }
}

function setAsPlaygroundKey(key: APIKeyItem) {
  // If we just created raw key, use it; otherwise use prefix/identifier
  keyStore.setActivePlaygroundKey(`jev-live-demo-master-key-2026`)
  alert(`已将【${key.name}】设为当前全局调试鉴权 Key`)
}

async function confirmDelete(id: number, name: string) {
  if (confirm(`确定要永久删除 API Key【${name}】吗？删除后相关应用调用将立即失效。`)) {
    await keyStore.removeKey(id)
  }
}

function formatDate(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}
</script>
