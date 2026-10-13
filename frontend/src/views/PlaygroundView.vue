<template>
  <div class="space-y-6">
    <!-- Top Workspace Bar: Scenario Template Selector & Context -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-base-200/60 p-3.5 sm:px-4 rounded-xl border border-base-300">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-bold text-base-content/80 flex items-center gap-1.5">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span>预置评估场景:</span>
        </span>
        <div class="join shadow-sm">
          <button
            v-for="tpl in decisionStore.templates"
            :key="tpl.id"
            class="join-item btn btn-xs flex items-center gap-1"
            :class="decisionStore.selectedTemplateId === tpl.id ? 'btn-primary font-bold' : 'btn-ghost bg-base-100'"
            @click="decisionStore.applyTemplate(tpl)"
          >
            <span v-if="tpl.sample_image" class="text-[10px]">📷</span>
            <span>{{ tpl.name }}</span>
          </button>
        </div>
      </div>

      <div class="flex items-center gap-3 text-xs text-base-content/60">
        <div class="flex items-center gap-1.5 font-mono text-[11px]">
          <span class="text-base-content/50">当前模型:</span>
          <span class="badge badge-neutral badge-xs font-mono font-bold">{{ currentModelShortName }}</span>
        </div>
        <div class="flex items-center gap-1.5 font-mono text-[11px] hidden md:flex">
          <span class="text-base-content/50">架构:</span>
          <span class="badge badge-outline badge-xs font-mono">{{ currentModelMeta.architecture }}</span>
        </div>
      </div>
    </div>

    <!-- Main Workspace Split: Input + Schema (Left) vs Results (Right) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left Column: Input and Questions Builder (col-span-7) -->
      <div class="lg:col-span-7 space-y-5">
        <!-- Multimodal Image Attachment Card (Available for d1-omni-600M) -->
        <div v-if="decisionStore.isMultimodal" class="card bg-base-200 border border-base-300">
          <div class="card-body p-4 sm:p-5 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <label class="font-bold text-sm flex items-center gap-1.5">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>图片</span>
                </label>
              </div>

              <!-- Clear button if image present -->
              <div v-if="decisionStore.imageUrl" class="flex items-center gap-2">
                <span class="badge badge-success badge-xs gap-1 font-mono">
                  <span class="w-1.5 h-1.5 rounded-full bg-success-content"></span>
                  已就绪
                </span>
                <button
                  class="btn btn-xs btn-ghost text-error"
                  @click="decisionStore.clearImage"
                >
                  移除
                </button>
              </div>
            </div>

            <!-- Image Loaded Preview View -->
            <div
              v-if="decisionStore.imageUrl"
              class="flex items-center gap-3.5 bg-base-100 p-3 rounded-xl border border-base-300 shadow-sm"
            >
              <div class="relative group shrink-0">
                <img
                  :src="decisionStore.imageUrl"
                  alt="Multimodal context preview"
                  class="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded-lg border border-base-300 bg-base-200"
                />
              </div>

              <div class="min-w-0 flex-1 space-y-1">
                <div class="flex items-center gap-2">
                  <span
                    class="badge badge-xs font-mono"
                    :class="decisionStore.imageType === 'upload' ? 'badge-primary' : 'badge-neutral'"
                  >
                    {{ decisionStore.imageType === 'upload' ? '本地上传' : '图片 URL' }}
                  </span>
                  <span class="text-xs font-bold text-base-content/85 truncate">
                    {{ decisionStore.imageName || 'Multimodal Image' }}
                  </span>
                </div>
                <div class="text-[11px] text-base-content/50 truncate font-mono">
                  {{ decisionStore.imageUrl.startsWith('data:') ? 'Base64 数据流已注入' : decisionStore.imageUrl }}
                </div>
                <div class="flex items-center gap-2 pt-0.5">
                  <button
                    class="btn btn-xs btn-outline btn-ghost text-primary text-[11px] h-6 min-h-0"
                    @click="triggerFileInput"
                  >
                    重新上传
                  </button>
                  <button
                    class="btn btn-xs btn-ghost text-base-content/60 text-[11px] h-6 min-h-0"
                    @click="switchImageMode('url')"
                  >
                    填写 URL
                  </button>
                </div>
              </div>
            </div>

            <!-- Image Selection Tabs (When no image loaded) -->
            <div v-else class="space-y-3">
              <!-- Upload Mode vs URL Mode Switcher Tabs -->
              <div class="tabs tabs-boxed tabs-xs inline-flex bg-base-300/60 p-1">
                <a
                  class="tab text-xs"
                  :class="{ 'tab-active font-bold': imageMode === 'upload' }"
                  @click="imageMode = 'upload'"
                >
                  📁 本地上传
                </a>
                <a
                  class="tab text-xs"
                  :class="{ 'tab-active font-bold': imageMode === 'url' }"
                  @click="imageMode = 'url'"
                >
                  🔗 填写图片地址
                </a>
              </div>

              <!-- Mode 1: Local File Upload -->
              <div v-if="imageMode === 'upload'">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/gif,image/bmp"
                  class="hidden"
                  @change="handleFileUpload"
                />
                <div
                  class="border-2 border-dashed border-base-300 hover:border-primary/60 transition-all rounded-xl p-4 text-center cursor-pointer bg-base-100/60 hover:bg-base-100 group"
                  @click="triggerFileInput"
                  @dragover.prevent
                  @drop.prevent="handleFileDrop"
                >
                  <div class="text-2xl mb-1 group-hover:scale-110 transition-transform">📷</div>
                  <div class="text-xs font-semibold text-base-content/85">
                    点击选择图片，或将图片文件拖拽至此
                  </div>
                  <div class="text-[11px] text-base-content/50 mt-0.5">
                    支持 PNG, JPG, WEBP, BMP (自动转换为 Data URI 进行前向单步评估)
                  </div>
                </div>
              </div>

              <!-- Mode 2: Image URL Input -->
              <div v-else class="space-y-2.5">
                <div class="flex items-center gap-2">
                  <input
                    v-model="inputUrl"
                    type="url"
                    placeholder="例如：https://example.com/invoice.jpg 或公网图片地址..."
                    class="input input-bordered input-sm flex-1 text-xs focus:outline-primary"
                    @keyup.enter="handleUrlSubmit"
                  />
                  <button
                    class="btn btn-sm btn-primary text-xs"
                    :disabled="!inputUrl.trim()"
                    @click="handleUrlSubmit"
                  >
                    载入图片
                  </button>
                </div>

                <!-- Quick Samples -->
                <div class="flex items-center gap-1.5 text-[11px] text-base-content/60 flex-wrap">
                  <span class="font-semibold">预置示例:</span>
                  <button
                    v-for="sample in sampleImages"
                    :key="sample.label"
                    class="btn btn-xs btn-ghost bg-base-300/40 text-[10px] px-2 h-6 min-h-0"
                    @click="setSampleImage(sample.url, sample.label)"
                  >
                    {{ sample.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Text Card -->
        <div class="card bg-base-200 border border-base-300">
          <div class="card-body p-4 sm:p-5">
            <div class="flex justify-between items-center mb-2">
              <label class="font-bold text-sm flex items-center gap-1.5">
                <span>待评估输入文本</span>
                <span class="badge badge-xs badge-neutral font-mono">{{ decisionStore.inputText.length }} 字符</span>
              </label>
              <button
                class="btn btn-xs btn-ghost text-base-content/60"
                @click="decisionStore.inputText = ''"
              >
                清空
              </button>
            </div>
            <textarea
              v-model="decisionStore.inputText"
              class="textarea textarea-bordered w-full h-32 text-sm font-sans focus:outline-primary"
              placeholder="输入需要让 Liquid AI 评估的文本内容，例如客户工单、风险咨询、评论、申请说明等..."
            ></textarea>
          </div>
        </div>

        <!-- Decision Questions Schema Builder -->
        <div class="card bg-base-200 border border-base-300">
          <div class="card-body p-4 sm:p-5 space-y-4">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="font-bold text-sm">决策问题</h3>
                <p class="text-xs text-base-content/60">
                  支持多项分类, 二元判断, 量规评分
                </p>
              </div>
              <button
                class="btn btn-xs btn-outline btn-primary gap-1"
                @click="openAddQuestionModal"
              >
                + 添加问题
              </button>
            </div>

            <!-- List of Questions -->
            <div class="space-y-3">
              <div
                v-for="([qKey, qDef], index) in Object.entries(decisionStore.questions)"
                :key="qKey"
                class="card bg-base-100 border border-base-300 hover:border-primary/40 transition-all shadow-sm"
              >
                <div class="card-body p-4 space-y-3">
                  <!-- Header: Index Badge + Type Badge + Actions (No Key Displayed) -->
                  <div class="flex items-center justify-between gap-2 border-b border-base-200 pb-2.5">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="badge badge-sm badge-neutral font-semibold">
                        问题 {{ index + 1 }}
                      </span>
                      <span
                        class="badge badge-sm gap-1 font-medium"
                        :class="getBadgeTypeClass(qDef.type)"
                      >
                        <span v-if="qDef.type === 'choice'">🔘 多项分类</span>
                        <span v-else-if="qDef.type === 'noul'">⚖️ 二元判断 (Yes/No)</span>
                        <span v-else-if="qDef.type === 'score'">⭐ 量规评分 (1~{{ qDef.scale || 5 }}分)</span>
                      </span>
                    </div>

                    <!-- Actions: Secondary Edit & Delete -->
                    <div class="flex items-center gap-1">
                      <button
                        class="btn btn-xs btn-ghost gap-1 text-primary hover:bg-primary/10"
                        @click="openEditQuestionModal(qKey)"
                        title="编辑此问题"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        <span>编辑</span>
                      </button>
                      <button
                        class="btn btn-xs btn-ghost text-error hover:bg-error/10 p-1"
                        @click="decisionStore.removeQuestion(qKey)"
                        title="删除该问题"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <!-- Question Description (Main Content) -->
                  <div>
                    <h4 class="font-bold text-sm text-base-content leading-snug">
                      {{ qDef.instructions }}
                    </h4>
                  </div>

                  <!-- Details Sub-Panel for Choice (Option Cards) -->
                  <div v-if="qDef.type === 'choice' && isRecord(qDef.criteria)" class="pt-1">
                    <div class="text-[11px] text-base-content/60 font-semibold mb-1.5 flex items-center justify-between">
                      <span>设定候选项 (共 {{ Object.keys(qDef.criteria).length }} 项):</span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      <div
                        v-for="([optKey, desc], optIdx) in Object.entries(qDef.criteria)"
                        :key="optKey"
                        class="bg-base-200/70 p-2 rounded-lg border border-base-300/80 flex items-start gap-2"
                      >
                        <span class="badge badge-xs badge-primary/20 text-primary font-bold shrink-0 mt-0.5">
                          选项 {{ String.fromCharCode(65 + Number(optIdx)) }}
                        </span>
                        <span class="text-base-content/80 text-xs leading-tight flex-1">{{ desc }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Details Sub-Panel for Noul (Criterion) -->
                  <div v-else-if="qDef.type === 'noul' && qDef.criteria" class="bg-base-200/50 p-2.5 rounded-lg border border-base-300/60 flex items-start gap-2 text-xs">
                    <span class="badge badge-xs badge-success shrink-0 mt-0.5">判定依据</span>
                    <span class="text-base-content/80 text-xs leading-relaxed flex-1">{{ qDef.criteria }}</span>
                  </div>

                  <!-- Details Sub-Panel for Score (Rubric & Scale) -->
                  <div v-else-if="qDef.type === 'score'" class="bg-base-200/50 p-2.5 rounded-lg border border-base-300/60 flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2 min-w-0 pr-2">
                      <span class="badge badge-xs badge-accent shrink-0">打分量规</span>
                      <span class="text-base-content/80 text-xs truncate">{{ qDef.criteria || '按照 1 至 ' + (qDef.scale || 5) + ' 分打分' }}</span>
                    </div>
                    <span class="badge badge-outline badge-xs font-mono font-bold shrink-0">
                      1 ~ {{ qDef.scale || 5 }} 分
                    </span>
                  </div>
                </div>
              </div>

              <div
                v-if="Object.keys(decisionStore.questions).length === 0"
                class="p-8 text-center text-xs text-base-content/50 border border-dashed border-base-300 rounded-xl space-y-1"
              >
                <div class="text-2xl mb-1">📋</div>
                <div class="font-medium text-base-content/70">尚未配置任何决策问题</div>
                <div class="text-[11px] text-base-content/50">请点击上方“+ 添加问题”创建，或在顶栏快速切换预置模版</div>
              </div>
            </div>

            <!-- Execution Action Bar -->
            <div class="pt-2 border-t border-base-300 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
              <!-- API Key selector for billing attribution -->
              <div class="flex items-center gap-2 text-xs">
                <span class="text-base-content/70">核算 Key:</span>
                <select
                  v-model="keyStore.activePlaygroundKey"
                  class="select select-bordered select-xs w-48 font-mono text-xs"
                >
                  <option value="">默认凭证 (系统预留)</option>
                  <option v-for="k in keyStore.keys" :key="k.id" :value="`jev-live-key-${k.id}`">
                    {{ k.name }} ({{ k.key_prefix }})
                  </option>
                </select>
              </div>

              <!-- Run Button -->
              <button
                class="btn btn-primary btn-sm gap-2"
                :disabled="decisionStore.executing"
                @click="decisionStore.runDecision(keyStore.activePlaygroundKey)"
              >
                <span v-if="decisionStore.executing" class="loading loading-spinner loading-xs"></span>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                </svg>
                执行决策
              </button>
            </div>

            <!-- Error Banner -->
            <div v-if="decisionStore.error" class="alert alert-error text-xs p-3">
              <span>{{ decisionStore.error }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Results & Token Audit (col-span-5) -->
      <div class="lg:col-span-5 space-y-5">
        <!-- Results Card -->
        <div class="card bg-base-200 border border-base-300">
          <div class="card-body p-4 sm:p-5">
            <div class="flex justify-between items-center mb-3">
              <h3 class="font-bold text-sm flex items-center gap-1.5">
                <span>推理决策输出</span>
                <span v-if="decisionStore.currentResponse" class="badge badge-success badge-xs">Completed</span>
              </h3>
              <div v-if="decisionStore.currentResponse" class="tabs tabs-boxed tabs-xs">
                <a
                  class="tab"
                  :class="{ 'tab-active': activeTab === 'visual' }"
                  @click="activeTab = 'visual'"
                >
                  可视化
                </a>
                <a
                  class="tab"
                  :class="{ 'tab-active': activeTab === 'json' }"
                  @click="activeTab = 'json'"
                >
                  JSON
                </a>
                <a
                  class="tab"
                  :class="{ 'tab-active': activeTab === 'curl' }"
                  @click="activeTab = 'curl'"
                >
                  cURL
                </a>
              </div>
            </div>

            <!-- Visual Results Display -->
            <div v-if="decisionStore.currentResponse && activeTab === 'visual'" class="space-y-4">
              <!-- Token Consumption & Latency Bar -->
              <div class="grid grid-cols-3 gap-2 bg-base-100 p-3 rounded-lg border border-base-300 text-center">
                <div>
                  <div class="text-[10px] text-base-content/60">消耗 Token</div>
                  <div class="font-mono font-bold text-sm text-primary">
                    {{ decisionStore.currentResponse.usage.total_tokens }}
                  </div>
                  <div class="text-[9px] text-base-content/50">
                    P: {{ decisionStore.currentResponse.usage.prompt_tokens }} / D: {{ decisionStore.currentResponse.usage.decision_tokens }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] text-base-content/60">推理延迟</div>
                  <div class="font-mono font-bold text-sm text-accent">
                    {{ decisionStore.currentResponse.latency_ms }} ms
                  </div>
                  <div class="text-[9px] text-base-content/50">前向单步推理</div>
                </div>
                <div>
                  <div class="text-[10px] text-base-content/60">运行模型</div>
                  <div class="font-mono font-bold text-[11px] truncate text-base-content/90" :title="decisionStore.currentResponse.model">
                    {{ decisionStore.currentResponse.model.includes('EdgeJev') ? 'EdgeJev' : (decisionStore.currentResponse.model.includes('MiniCPM') ? 'MiniCPM5-2B' : 'd1-omni-600M') }}
                  </div>
                  <div class="text-[9px] text-base-content/50 truncate">
                    {{ decisionStore.currentResponse.model.includes('EdgeJev') ? '322M Edge' : (decisionStore.currentResponse.model.includes('MiniCPM') ? '2.0B Jev-Tuned' : '600M LFM') }}
                  </div>
                </div>
              </div>

              <!-- Multimodal Vision Context Feedback Banner -->
              <div v-if="decisionStore.isMultimodal && decisionStore.imageUrl" class="flex items-center gap-3 bg-base-100 p-2.5 rounded-lg border border-base-300 shadow-sm">
                <img :src="decisionStore.imageUrl" alt="Vision Context" class="w-10 h-10 object-cover rounded-lg border border-base-300 shrink-0 bg-base-200" />
                <div class="min-w-0 flex-1 text-xs">
                  <div class="flex items-center gap-1.5 font-bold text-base-content/85">
                    <span>图像视觉特征已融合</span>
                    <span class="badge badge-success badge-xs font-mono">Vision Patch OK</span>
                  </div>
                  <div class="text-[11px] text-base-content/50 truncate font-mono">
                    {{ decisionStore.imageName || decisionStore.imageUrl }}
                  </div>
                </div>
              </div>

              <!-- Question Outcomes -->
              <div class="space-y-3">
                <div
                  v-for="(ans, qKey) in decisionStore.currentResponse.answers"
                  :key="qKey"
                  class="bg-base-100 p-3.5 rounded-lg border border-base-300 space-y-3 shadow-sm hover:border-primary/30 transition-all"
                >
                  <!-- Question Header (No key shown) -->
                  <div class="flex items-center justify-between gap-2 border-b border-base-200 pb-2">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="badge badge-sm badge-neutral font-semibold">
                        问题 {{ getQuestionNumber(String(qKey)) }}
                      </span>
                      <span
                        v-if="decisionStore.questions[qKey]"
                        class="badge badge-sm font-medium"
                        :class="getBadgeTypeClass(decisionStore.questions[qKey].type)"
                      >
                        <span v-if="decisionStore.questions[qKey].type === 'choice'">🔘 多项分类</span>
                        <span v-else-if="decisionStore.questions[qKey].type === 'noul'">⚖️ 二元判断</span>
                        <span v-else-if="decisionStore.questions[qKey].type === 'score'">⭐ 量规评分</span>
                      </span>
                    </div>
                  </div>

                  <!-- Question Instructions -->
                  <div v-if="decisionStore.questions[qKey]?.instructions" class="text-xs font-bold text-base-content leading-snug">
                    {{ decisionStore.questions[qKey].instructions }}
                  </div>

                  <!-- Probability / Scoring Display -->
                  <ProbabilitiesBar
                    :type="decisionStore.questions[qKey]?.type || 'choice'"
                    :data="ans"
                    :criteria="decisionStore.questions[qKey]?.criteria"
                  />
                </div>
              </div>
            </div>

            <!-- JSON View Tab -->
            <div v-else-if="decisionStore.currentResponse && activeTab === 'json'">
              <JsonViewer :data="decisionStore.currentResponse" />
            </div>

            <!-- cURL View Tab -->
            <div v-else-if="decisionStore.currentResponse && activeTab === 'curl'" class="space-y-2">
              <div class="relative bg-base-300 rounded-lg p-3 text-xs font-mono">
                <div class="absolute top-2 right-2">
                  <CopyButton :text="curlSnippet" textLabel="复制 cURL" />
                </div>
                <pre class="overflow-x-auto text-[11px] leading-relaxed whitespace-pre-wrap">{{ curlSnippet }}</pre>
              </div>
            </div>

            <!-- Empty Placeholder -->
            <div
              v-else-if="!decisionStore.executing"
              class="h-64 flex flex-col items-center justify-center text-center p-6 text-base-content/50"
            >
              <div class="text-3xl mb-2">⚡</div>
              <div class="text-sm font-medium">尚未执行决策</div>
              <div class="text-xs text-base-content/40 mt-1 max-w-xs">
                在左侧输入需要判断的文本内容，点击“执行 {{ currentModelShortName }} 决策”即可获得单步决策结果与代币统计
              </div>
            </div>

            <!-- Loading Spinner -->
            <div
              v-else
              class="h-64 flex flex-col items-center justify-center text-center p-6"
            >
              <span class="loading loading-bars loading-lg text-primary"></span>
              <div class="text-xs font-mono text-base-content/60 mt-3">
                {{ currentModelMeta.fullName }} 正在进行单步决策评估...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add / Edit Question Modal -->
    <dialog class="modal" :class="{ 'modal-open': showModal }">
      <div class="modal-box max-w-xl max-h-[90vh] flex flex-col p-5">
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
          <div>
            <h3 class="font-bold text-base flex items-center gap-2">
              <span>{{ modalMode === 'create' ? '添加决策问题' : '编辑决策问题' }}</span>
              <span v-if="modalMode === 'edit'" class="badge badge-sm badge-neutral">
                问题 {{ getQuestionNumber(editingKey) }}
              </span>
            </h3>
            <p class="text-xs text-base-content/60 mt-0.5">
              {{ modalMode === 'create' ? '配置单步决策评估问题、原语类型与判定条件' : '修改判定指导指令、候选项或评分量规' }}
            </p>
          </div>
          <button class="btn btn-ghost btn-xs btn-circle" @click="closeModal">✕</button>
        </div>

        <!-- Modal Body Scrollable -->
        <div class="overflow-y-auto space-y-4 pr-1 text-xs flex-1">
          <!-- Question Type Selector -->
          <div class="space-y-1.5">
            <label class="label-text font-semibold flex items-center gap-1.5">
              <span>决策原语类型</span>
              <span class="text-error">*</span>
            </label>
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                class="btn btn-sm text-xs flex flex-col h-auto py-2 px-1 text-center transition-all"
                :class="modalForm.type === 'choice' ? 'btn-primary' : 'btn-outline border-base-300 text-base-content/70'"
                @click="setModalType('choice')"
              >
                <span class="font-bold">🔘 多项分类</span>
                <span class="text-[10px] opacity-75 font-normal">从候选项中选择</span>
              </button>
              <button
                type="button"
                class="btn btn-sm text-xs flex flex-col h-auto py-2 px-1 text-center transition-all"
                :class="modalForm.type === 'noul' ? 'btn-success text-success-content' : 'btn-outline border-base-300 text-base-content/70'"
                @click="setModalType('noul')"
              >
                <span class="font-bold">⚖️ 二元判断</span>
                <span class="text-[10px] opacity-75 font-normal">Yes / No 是非题</span>
              </button>
              <button
                type="button"
                class="btn btn-sm text-xs flex flex-col h-auto py-2 px-1 text-center transition-all"
                :class="modalForm.type === 'score' ? 'btn-accent text-accent-content' : 'btn-outline border-base-300 text-base-content/70'"
                @click="setModalType('score')"
              >
                <span class="font-bold">⭐ 量规打分</span>
                <span class="text-[10px] opacity-75 font-normal">多级量程评分</span>
              </button>
            </div>
          </div>

          <!-- Instructions Field -->
          <div class="space-y-1">
            <label class="label-text font-semibold flex items-center justify-between">
              <span class="flex items-center gap-1">
                <span>评估指导指令 (Instructions)</span>
                <span class="text-error">*</span>
              </span>
              <span class="text-[11px] text-base-content/50 font-normal">指导模型判断的目标</span>
            </label>
            <textarea
              v-model="modalForm.instructions"
              placeholder="例如：判断该工单的主要诉求分类 / 该问题是否属于严重阻断故障 / 评估事件紧急程度..."
              class="textarea textarea-bordered textarea-sm w-full h-20 text-xs focus:outline-primary"
            ></textarea>
          </div>

          <!-- Type-Specific: Choice Options -->
          <div v-if="modalForm.type === 'choice'" class="space-y-2 bg-base-200/50 p-3 rounded-xl border border-base-300/80">
            <div class="flex items-center justify-between">
              <div>
                <label class="label-text font-semibold flex items-center gap-1 text-xs">
                  <span>候选项设定</span>
                  <span class="text-error">*</span>
                  <span class="badge badge-xs badge-neutral font-mono">{{ modalForm.choiceOptions.length }} 项</span>
                </label>
                <div class="text-[11px] text-base-content/60">
                  至少配置 2 个分类选项，模型将根据语义特征计算各选项置信度
                </div>
              </div>
              <button
                type="button"
                class="btn btn-xs btn-outline btn-primary gap-1"
                @click="addChoiceOption"
              >
                + 添加选项
              </button>
            </div>

            <!-- Options List -->
            <div class="space-y-2 mt-2">
              <div
                v-for="(opt, idx) in modalForm.choiceOptions"
                :key="opt.id"
                class="flex items-center gap-2 bg-base-100 p-2 rounded-lg border border-base-300 shadow-sm"
              >
                <span class="badge badge-xs badge-primary/20 text-primary font-bold shrink-0">
                  选项 {{ String.fromCharCode(65 + idx) }}
                </span>
                <input
                  v-model="opt.desc"
                  type="text"
                  class="input input-bordered input-xs flex-1 text-xs focus:outline-primary"
                  :placeholder="`输入选项 ${String.fromCharCode(65 + idx)} 的判定描述或内容，例如：服务器、网络基础设施故障`"
                />
                <button
                  type="button"
                  class="btn btn-ghost btn-xs text-error p-1 hover:bg-error/10"
                  :disabled="modalForm.choiceOptions.length <= 2"
                  @click="removeChoiceOption(idx)"
                  title="删除该选项"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Type-Specific: Noul (Yes/No Criterion) -->
          <div v-else-if="modalForm.type === 'noul'" class="space-y-1 bg-base-200/50 p-3 rounded-xl border border-base-300/80">
            <label class="label-text font-semibold flex items-center justify-between text-xs">
              <span>判定标准 (Criteria, 判定为 YES 的依据)</span>
              <span class="text-[11px] text-base-content/50 font-normal">选填</span>
            </label>
            <textarea
              v-model="modalForm.noulCriteria"
              placeholder="例如：系统完全不可用、服务大面积中断或资金安全风险..."
              class="textarea textarea-bordered textarea-sm w-full h-16 text-xs focus:outline-primary"
            ></textarea>
          </div>

          <!-- Type-Specific: Score (Scale & Rubric) -->
          <div v-else-if="modalForm.type === 'score'" class="space-y-3 bg-base-200/50 p-3 rounded-xl border border-base-300/80">
            <div class="space-y-1">
              <label class="label-text font-semibold flex items-center justify-between text-xs">
                <span>最高打分量程 (Scale)</span>
                <span class="badge badge-xs font-mono font-bold">{{ modalForm.scale }} 分制</span>
              </label>
              <div class="flex items-center gap-2">
                <input
                  v-model.number="modalForm.scale"
                  type="range"
                  min="2"
                  max="10"
                  class="range range-xs range-accent flex-1"
                />
                <span class="font-mono text-xs font-bold w-12 text-right">1~{{ modalForm.scale }}分</span>
              </div>
            </div>

            <div class="space-y-1">
              <label class="label-text font-semibold flex items-center justify-between text-xs">
                <span>打分量规说明 (Rubric)</span>
                <span class="text-[11px] text-base-content/50 font-normal">选填</span>
              </label>
              <textarea
                v-model="modalForm.scoreCriteria"
                placeholder="例如：1 表示常规轻微，5 表示极度紧急最高级别响应..."
                class="textarea textarea-bordered textarea-sm w-full h-16 text-xs focus:outline-primary"
              ></textarea>
            </div>
          </div>

          <!-- Validation Error Alert -->
          <div v-if="modalError" class="alert alert-error text-xs p-2.5 rounded-lg">
            <span>{{ modalError }}</span>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="modal-action border-t border-base-300 pt-3 mt-3 flex justify-end gap-2">
          <button class="btn btn-sm btn-ghost" @click="closeModal">取消</button>
          <button class="btn btn-sm btn-primary" @click="confirmSaveQuestion">
            {{ modalMode === 'create' ? '确认添加' : '保存修改' }}
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="closeModal">
        <button>close</button>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDecisionStore } from '@/stores/decisionStore'
import { useKeyStore } from '@/stores/keyStore'
import type { QuestionType, QuestionDefinition } from '@/types/decision'
import ProbabilitiesBar from '@/components/ProbabilitiesBar.vue'
import JsonViewer from '@/components/JsonViewer.vue'
import CopyButton from '@/components/CopyButton.vue'

interface ChoiceOptionItem {
  id: string
  key: string
  desc: string
}

const decisionStore = useDecisionStore()
const keyStore = useKeyStore()

const activeTab = ref<'visual' | 'json' | 'curl'>('visual')
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingKey = ref<string>('')
const modalError = ref<string | null>(null)

const modalForm = ref<{
  type: QuestionType
  instructions: string
  choiceOptions: ChoiceOptionItem[]
  noulCriteria: string
  scoreCriteria: string
  scale: number
}>({
  type: 'choice',
  instructions: '',
  choiceOptions: [],
  noulCriteria: '',
  scoreCriteria: '',
  scale: 5,
})

onMounted(async () => {
  await keyStore.loadKeys()
  await decisionStore.loadTemplates()
})

function getBadgeTypeClass(type: QuestionType) {
  if (type === 'choice') return 'badge-primary'
  if (type === 'noul') return 'badge-success'
  return 'badge-accent'
}

function isRecord(val: any): val is Record<string, string> {
  return typeof val === 'object' && val !== null && !Array.isArray(val)
}

function getQuestionNumber(key: string): number {
  const keys = Object.keys(decisionStore.questions)
  const idx = keys.indexOf(key)
  return idx >= 0 ? idx + 1 : 1
}

function setModalType(type: QuestionType) {
  modalForm.value.type = type
  if (type === 'choice' && modalForm.value.choiceOptions.length < 2) {
    modalForm.value.choiceOptions = [
      { id: 'opt_' + Date.now() + '_1', key: 'opt_1', desc: '' },
      { id: 'opt_' + Date.now() + '_2', key: 'opt_2', desc: '' },
    ]
  }
}

function addChoiceOption() {
  const nextNum = modalForm.value.choiceOptions.length + 1
  modalForm.value.choiceOptions.push({
    id: 'opt_' + Date.now() + '_' + nextNum,
    key: 'opt_' + nextNum,
    desc: '',
  })
}

function removeChoiceOption(idx: number) {
  if (modalForm.value.choiceOptions.length > 2) {
    modalForm.value.choiceOptions.splice(idx, 1)
  }
}

function openAddQuestionModal() {
  modalMode.value = 'create'
  editingKey.value = ''
  modalError.value = null
  modalForm.value = {
    type: 'choice',
    instructions: '',
    choiceOptions: [
      { id: 'opt_1', key: 'opt_1', desc: '' },
      { id: 'opt_2', key: 'opt_2', desc: '' },
    ],
    noulCriteria: '',
    scoreCriteria: '',
    scale: 5,
  }
  showModal.value = true
}

function openEditQuestionModal(key: string) {
  const qDef = decisionStore.questions[key]
  if (!qDef) return

  modalMode.value = 'edit'
  editingKey.value = key
  modalError.value = null

  const choiceOptions: ChoiceOptionItem[] = []
  if (qDef.type === 'choice' && isRecord(qDef.criteria)) {
    Object.entries(qDef.criteria).forEach(([k, v], idx) => {
      choiceOptions.push({
        id: `opt_${idx}_${k}`,
        key: k,
        desc: String(v),
      })
    })
  }

  // Ensure at least 2 options for choice
  if (choiceOptions.length < 2) {
    while (choiceOptions.length < 2) {
      const idx = choiceOptions.length + 1
      choiceOptions.push({
        id: `opt_${Date.now()}_${idx}`,
        key: `opt_${idx}`,
        desc: '',
      })
    }
  }

  modalForm.value = {
    type: qDef.type,
    instructions: qDef.instructions || '',
    choiceOptions,
    noulCriteria: typeof qDef.criteria === 'string' ? qDef.criteria : '',
    scoreCriteria: typeof qDef.criteria === 'string' ? qDef.criteria : '',
    scale: qDef.scale || 5,
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  modalError.value = null
}

function confirmSaveQuestion() {
  modalError.value = null
  const instructions = modalForm.value.instructions.trim()
  if (!instructions) {
    modalError.value = '请输入评估指导指令 (Instructions)'
    return
  }

  let criteria: Record<string, string> | string | undefined = undefined
  let scale: number | undefined = undefined

  if (modalForm.value.type === 'choice') {
    const validOptions = modalForm.value.choiceOptions.filter(o => o.desc.trim())
    if (validOptions.length < 2) {
      modalError.value = '请至少填写 2 个有效的候选项内容'
      return
    }
    const criteriaObj: Record<string, string> = {}
    validOptions.forEach((opt, idx) => {
      const optKey = opt.key || `opt_${idx + 1}`
      criteriaObj[optKey] = opt.desc.trim()
    })
    criteria = criteriaObj
  } else if (modalForm.value.type === 'noul') {
    criteria = modalForm.value.noulCriteria.trim() || undefined
  } else if (modalForm.value.type === 'score') {
    criteria = modalForm.value.scoreCriteria.trim() || undefined
    scale = modalForm.value.scale || 5
  }

  const newDef: QuestionDefinition = {
    type: modalForm.value.type,
    instructions,
    criteria,
    scale,
  }

  if (modalMode.value === 'create') {
    // Auto-generate key in background, never show to user
    const autoKey = `q_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 6)}`
    decisionStore.addQuestion(autoKey, newDef)
  } else {
    decisionStore.updateQuestion(editingKey.value, newDef)
  }

  closeModal()
}

const currentModelMeta = computed(() => decisionStore.currentModelMeta)
const currentModelShortName = computed(() => decisionStore.currentModelShortName)

const fileInputRef = ref<HTMLInputElement | null>(null)
const imageMode = ref<'upload' | 'url'>('upload')
const inputUrl = ref('')

const sampleImages = [
  { label: '示例动物 (拉布拉多犬)', url: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.LS_T9sXWOLjaDoXqjat2_gHaE8' },
  { label: '发票报销凭证', url: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=500' },
  { label: '服务器报错图', url: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500' },
  { label: '合同签字文档', url: 'https://images.unsplash.com/photo-1450133064473-71024230f91b?w=500' },
]

function triggerFileInput() {
  fileInputRef.value?.click()
}

function switchImageMode(mode: 'upload' | 'url') {
  imageMode.value = mode
  if (mode === 'upload') {
    triggerFileInput()
  }
}

function processImageFile(file: File) {
  if (!file.type.startsWith('image/')) {
    decisionStore.error = '请选择有效的图片文件 (PNG, JPG, WEBP 等)'
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    const res = e.target?.result as string
    if (res) {
      decisionStore.setImage(res, 'upload', file.name)
    }
  }
  reader.readAsDataURL(file)
}

function handleFileUpload(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    processImageFile(target.files[0])
    target.value = ''
  }
}

function handleFileDrop(e: DragEvent) {
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    processImageFile(e.dataTransfer.files[0])
  }
}

function handleUrlSubmit() {
  const url = inputUrl.value.trim()
  if (!url) return
  decisionStore.setImage(url, 'url', url.split('/').pop() || 'image')
  inputUrl.value = ''
}

function setSampleImage(url: string, label: string) {
  decisionStore.setImage(url, 'url', label)
}

const curlSnippet = computed(() => {
  const payload: any = {
    input: decisionStore.inputText,
    questions: decisionStore.questions,
    model: decisionStore.selectedModelId,
  }
  if (decisionStore.isMultimodal && decisionStore.imageUrl) {
    payload.image = decisionStore.imageUrl.startsWith('data:')
      ? `${decisionStore.imageUrl.substring(0, 30)}...[base64_data]`
      : decisionStore.imageUrl
  }
  const keyHeader = keyStore.activePlaygroundKey
    ? `  -H "Authorization: Bearer ${keyStore.activePlaygroundKey}" \\\n`
    : ''

  const baseUrl = typeof window !== 'undefined' && window.location.origin
    ? window.location.origin
    : 'http://127.0.0.1:8002'

  return `curl -X POST ${baseUrl}/api/v1/decision/predict \\
  -H "Content-Type: application/json" \\
${keyHeader}  -d '${JSON.stringify(payload, null, 2)}'`
})
</script>
