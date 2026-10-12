<template>
  <div class="space-y-8 max-w-5xl">
    <!-- Header -->
    <div class="space-y-2">
      <h1 class="text-3xl font-black tracking-tight">JEV 决策模型 API 开发者文档</h1>
      <p class="text-sm text-base-content/70">
        基于 Liquid AI d1-omni-600M 决策模型的快速接入指南、身份鉴权规范及多语言代码示例
      </p>
    </div>

    <!-- Quick Architecture Overview -->
    <div class="card bg-base-200 border border-base-300">
      <div class="card-body p-6 space-y-3">
        <h2 class="card-title text-base font-bold flex items-center gap-2">
          <span>💡 什么是 Liquid AI 决策模型 (Decision Model)？</span>
        </h2>
        <p class="text-xs text-base-content/80 leading-relaxed">
          与传统的自回归逐字生成大语言模型 (LLM) 不同，<strong>Liquid AI d1-omni-600M</strong>
          专为结构化决策设计。它通过<strong>单步前向传播 (Single Forward Pass)</strong> 直接输出校准的条件概率分布与离散决策结果，具有如下核心优势：
        </p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
          <div class="bg-base-100 p-3 rounded-lg border border-base-300 text-xs space-y-1">
            <div class="font-bold text-primary">⚡ 零生成延迟 (Zero Generation)</div>
            <div class="text-base-content/70 text-[11px]">无需逐 Token 采样，单次前向传播仅需 15-40ms 即可完成评估。</div>
          </div>
          <div class="bg-base-100 p-3 rounded-lg border border-base-300 text-xs space-y-1">
            <div class="font-bold text-accent">🎯 校准概率分布</div>
            <div class="text-base-content/70 text-[11px]">输出严格校准的 Softmax/Sigmoid 概率，可信度远高于常规 Prompt 提取。</div>
          </div>
          <div class="bg-base-100 p-3 rounded-lg border border-base-300 text-xs space-y-1">
            <div class="font-bold text-secondary">💰 精准代币计量与控制</div>
            <div class="text-base-content/70 text-[11px]">按输入 Token 与决策计算头消耗计费，支持细粒度 Key 配额与速率限制。</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Decision Primitives Explanation -->
    <div class="space-y-3">
      <h2 class="text-lg font-bold">三大约束决策原语 (Decision Primitives)</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card bg-base-200 border border-base-300 p-4 space-y-2">
          <div class="badge badge-primary font-mono text-xs">choice</div>
          <div class="font-bold text-sm">多项分类选择</div>
          <p class="text-xs text-base-content/70">
            从无序分类集合中进行归类。返回每个类别的 Softmax 概率分布与置信度最高项。
          </p>
          <pre class="bg-base-300 p-2 rounded text-[11px] font-mono">{
  "type": "choice",
  "criteria": {
    "tech": "技术支持",
    "billing": "账务退款"
  }
}</pre>
        </div>

        <div class="card bg-base-200 border border-base-300 p-4 space-y-2">
          <div class="badge badge-success font-mono text-xs">noul</div>
          <div class="font-bold text-sm">二元判断 (Yes / No)</div>
          <p class="text-xs text-base-content/70">
            针对特定判定标准的布尔判断。返回真伪决策布尔值及 [0.0, 1.0] 校准概率。
          </p>
          <pre class="bg-base-300 p-2 rounded text-[11px] font-mono">{
  "type": "noul",
  "instructions": "是否紧急?",
  "criteria": "业务完全中断"
}</pre>
        </div>

        <div class="card bg-base-200 border border-base-300 p-4 space-y-2">
          <div class="badge badge-accent font-mono text-xs">score</div>
          <div class="font-bold text-sm">量规有序打分</div>
          <p class="text-xs text-base-content/70">
            在指定等级区间 (如 1-5 或 1-10) 进行强度评估，返回整数评级与量表尺度。
          </p>
          <pre class="bg-base-300 p-2 rounded text-[11px] font-mono">{
  "type": "score",
  "instructions": "严重性打分",
  "scale": 5
}</pre>
        </div>
      </div>
    </div>

    <!-- Authentication -->
    <div class="space-y-3">
      <h2 class="text-lg font-bold">接口鉴权方式</h2>
      <p class="text-xs text-base-content/70">
        调用决策模型接口时，请在 HTTP 请求头中携带通过本平台开通的 API Key：
      </p>
      <div class="mockup-code text-xs">
        <pre data-prefix="$"><code># 方式一：标准 Bearer 鉴权头</code></pre>
        <pre data-prefix=">"><code>Authorization: Bearer jev-live-your-secret-api-key</code></pre>
        <pre data-prefix="$"><code># 方式二：X-API-Key 自定义请求头</code></pre>
        <pre data-prefix=">"><code>X-API-Key: jev-live-your-secret-api-key</code></pre>
      </div>
    </div>

    <!-- Code Examples (Tabs) -->
    <div class="space-y-3">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold">多语言调用代码示例</h2>
        <div class="tabs tabs-boxed tabs-xs">
          <a
            class="tab"
            :class="{ 'tab-active': codeLang === 'python' }"
            @click="codeLang = 'python'"
          >
            Python
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': codeLang === 'curl' }"
            @click="codeLang = 'curl'"
          >
            cURL
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': codeLang === 'typescript' }"
            @click="codeLang = 'typescript'"
          >
            TypeScript / Node
          </a>
        </div>
      </div>

      <!-- Code Box -->
      <div class="relative bg-base-300 rounded-xl p-4 text-xs font-mono border border-base-200">
        <div class="absolute top-3 right-3 z-10">
          <CopyButton :text="currentSnippet" textLabel="复制代码" />
        </div>
        <pre class="overflow-x-auto text-xs leading-relaxed max-h-[420px]">{{ currentSnippet }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CopyButton from '@/components/CopyButton.vue'

const codeLang = ref<'python' | 'curl' | 'typescript'>('python')

const pythonSnippet = `import requests

API_URL = "http://127.0.0.1:8002/api/v1/decision/predict"
API_KEY = "jev-live-demo-master-key-2026"

payload = {
    "input": "我们的生产集群部署后出现宕机，支付服务无法访问，请立即排查！",
    "questions": {
        "intent": {
            "type": "choice",
            "instructions": "判断工单主要诉求分类",
            "criteria": {
                "infrastructure": "服务器或网络基础设施故障",
                "billing": "账务、发票或退款咨询",
                "general": "常规咨询与产品使用说明"
            }
        },
        "is_critical": {
            "type": "noul",
            "instructions": "是否属于阻断核心业务的严重故障？",
            "criteria": "服务大面积中断或资金安全风险"
        },
        "urgency_score": {
            "type": "score",
            "instructions": "评估紧急响应优先级 (1=低, 5=最高)",
            "scale": 5
        }
    }
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=payload, headers=headers)
data = response.json()

print("决策结果:", data["answers"])
print(f"Token 消耗: {data['usage']['total_tokens']} tokens")
print(f"推理延迟: {data['latency_ms']} ms")`

const curlSnippet = `curl -X POST http://127.0.0.1:8002/api/v1/decision/predict \\
  -H "Authorization: Bearer jev-live-demo-master-key-2026" \\
  -H "Content-Type: application/json" \\
  -d '{
    "input": "系统支付接口突然返回 500 内部错误，用户无法结算！",
    "questions": {
      "intent": {
        "type": "choice",
        "instructions": "分类工单类型",
        "criteria": {
          "fault": "系统故障",
          "query": "常规查询"
        }
      },
      "is_urgent": {
        "type": "noul",
        "instructions": "是否属于高优先级紧急事件"
      }
    }
  }'`

const tsSnippet = `import axios from 'axios';

async function main() {
  const response = await axios.post(
    'http://127.0.0.1:8002/api/v1/decision/predict',
    {
      input: '我们的生产环境集群在刚刚的部署中全部中断了！',
      questions: {
        intent: {
          type: 'choice',
          instructions: '判断故障分类',
          criteria: {
            infra: '基础设施故障',
            app: '应用逻辑异常'
          }
        },
        urgency: {
          type: 'score',
          instructions: '评估响应紧急度',
          scale: 5
        }
      }
    },
    {
      headers: {
        Authorization: 'Bearer jev-live-demo-master-key-2026',
        'Content-Type': 'application/json'
      }
    }
  );

  console.log('决策结果:', response.data.answers);
  console.log('消耗统计:', response.data.usage);
}

main();`

const currentSnippet = computed(() => {
  if (codeLang.value === 'python') return pythonSnippet
  if (codeLang.value === 'curl') return curlSnippet
  return tsSnippet
})
</script>
