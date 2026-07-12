<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  ElMessage,
  ElMessageBox,
} from 'element-plus'

import {
  Bell,
  Check,
  Connection,
  Monitor,
  Refresh,
  Setting,
} from '@element-plus/icons-vue'

import {
  getSystemSettingsApi,
  updateSystemSettingsApi,
} from '../api/systemSettings'


/* ==============================
   页面状态
================================ */

const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)

const originalSettings = ref(null)


/* ==============================
   设置表单
================================ */

const settingsForm = reactive({
  platform_name: '',
  platform_subtitle: '',
  default_platform: '抖音',
  timezone: 'Asia/Shanghai',
  theme: 'dark',
  ai_provider: 'OpenAI',
  ai_model: 'default',
  temperature: 0.7,
  enable_ai_generation: true,
  enable_auto_review: false,
  enable_notifications: true,
})


/* ==============================
   表单校验
================================ */

const formRules = {
  platform_name: [
    {
      required: true,
      message: '请输入平台名称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 100,
      message: '平台名称长度为1到100个字符',
      trigger: 'blur',
    },
  ],

  platform_subtitle: [
    {
      required: true,
      message: '请输入平台副标题',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 200,
      message: '平台副标题不能超过200个字符',
      trigger: 'blur',
    },
  ],

  default_platform: [
    {
      required: true,
      message: '请选择默认发布平台',
      trigger: 'change',
    },
  ],

  timezone: [
    {
      required: true,
      message: '请选择系统时区',
      trigger: 'change',
    },
  ],

  theme: [
    {
      required: true,
      message: '请选择界面主题',
      trigger: 'change',
    },
  ],

  ai_provider: [
    {
      required: true,
      message: '请选择AI服务商',
      trigger: 'change',
    },
  ],

  ai_model: [
    {
      required: true,
      message: '请输入AI模型名称',
      trigger: 'blur',
    },
  ],
}


/* ==============================
   下拉选项
================================ */

const platformOptions = [
  '抖音',
  '快手',
  '小红书',
  '视频号',
  'B站',
]

const timezoneOptions = [
  {
    label: '中国标准时间（Asia/Shanghai）',
    value: 'Asia/Shanghai',
  },
  {
    label: '美国东部时间（America/New_York）',
    value: 'America/New_York',
  },
  {
    label: '美国西部时间（America/Los_Angeles）',
    value: 'America/Los_Angeles',
  },
  {
    label: '日本标准时间（Asia/Tokyo）',
    value: 'Asia/Tokyo',
  },
  {
    label: '世界标准时间（UTC）',
    value: 'UTC',
  },
]

const themeOptions = [
  {
    label: '深色主题',
    value: 'dark',
  },
  {
    label: '浅色主题',
    value: 'light',
  },
  {
    label: '跟随系统',
    value: 'system',
  },
]

const aiProviderOptions = [
  'OpenAI',
  'Claude',
  'Gemini',
  'DeepSeek',
  '通义千问',
  '豆包',
  '自定义服务',
]


/* ==============================
   页面统计
================================ */

const enabledFeatureCount = computed(() => {
  return [
    settingsForm.enable_ai_generation,
    settingsForm.enable_auto_review,
    settingsForm.enable_notifications,
  ].filter(Boolean).length
})

const temperatureDescription = computed(() => {
  const value = Number(
    settingsForm.temperature,
  )

  if (value <= 0.3) {
    return '输出更稳定、严格，适合结构化内容'
  }

  if (value <= 0.8) {
    return '稳定性与创造力较为均衡'
  }

  if (value <= 1.3) {
    return '输出更加灵活，适合创意脚本'
  }

  return '随机性较高，适合创意发散测试'
})


/* ==============================
   接口数据解析
================================ */

function resolveSettingsResponse(response) {
  /*
   * 兼容：
   * 1. Axios返回完整response
   * 2. Axios拦截器直接返回response.data
   */

  if (
    response?.data?.data &&
    typeof response.data.data === 'object'
  ) {
    return response.data.data
  }

  if (
    response?.data &&
    typeof response.data === 'object' &&
    'platform_name' in response.data
  ) {
    return response.data
  }

  if (
    response &&
    typeof response === 'object' &&
    'platform_name' in response
  ) {
    return response
  }

  return null
}

function getErrorMessage(
  error,
  fallbackMessage,
) {
  const detail =
    error?.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (
    Array.isArray(detail) &&
    detail.length > 0
  ) {
    return (
      detail[0]?.msg ||
      fallbackMessage
    )
  }

  return (
    error?.response?.data?.message ||
    error?.message ||
    fallbackMessage
  )
}


/* ==============================
   表单赋值
================================ */

function applySettings(settings) {
  Object.assign(settingsForm, {
    platform_name:
      settings.platform_name ||
      'AI短视频电商平台',

    platform_subtitle:
      settings.platform_subtitle ||
      'AI驱动的短视频内容创作与电商增长平台',

    default_platform:
      settings.default_platform ||
      '抖音',

    timezone:
      settings.timezone ||
      'Asia/Shanghai',

    theme:
      settings.theme ||
      'dark',

    ai_provider:
      settings.ai_provider ||
      'OpenAI',

    ai_model:
      settings.ai_model ||
      'default',

    temperature:
      Number(
        settings.temperature ?? 0.7,
      ),

    enable_ai_generation:
      Boolean(
        settings.enable_ai_generation,
      ),

    enable_auto_review:
      Boolean(
        settings.enable_auto_review,
      ),

    enable_notifications:
      Boolean(
        settings.enable_notifications,
      ),
  })
}


/* ==============================
   加载设置
================================ */

async function loadSystemSettings() {
  loading.value = true

  try {
    const response =
      await getSystemSettingsApi()

    const settings =
      resolveSettingsResponse(response)

    if (!settings) {
      throw new Error(
        '系统设置返回格式不正确',
      )
    }

    applySettings(settings)

    originalSettings.value =
      JSON.parse(
        JSON.stringify(settingsForm),
      )
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '系统设置加载失败',
      ),
    )
  } finally {
    loading.value = false
  }
}


/* ==============================
   保存设置
================================ */

async function saveSystemSettings() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true

  const submitData = {
    platform_name:
      settingsForm.platform_name.trim(),

    platform_subtitle:
      settingsForm.platform_subtitle.trim(),

    default_platform:
      settingsForm.default_platform,

    timezone:
      settingsForm.timezone,

    theme:
      settingsForm.theme,

    ai_provider:
      settingsForm.ai_provider,

    ai_model:
      settingsForm.ai_model.trim(),

    temperature:
      Number(
        settingsForm.temperature,
      ),

    enable_ai_generation:
      Boolean(
        settingsForm.enable_ai_generation,
      ),

    enable_auto_review:
      Boolean(
        settingsForm.enable_auto_review,
      ),

    enable_notifications:
      Boolean(
        settingsForm.enable_notifications,
      ),
  }

  try {
    const response =
      await updateSystemSettingsApi(
        submitData,
      )

    const settings =
      resolveSettingsResponse(response)

    if (settings) {
      applySettings(settings)
    }

    originalSettings.value =
      JSON.parse(
        JSON.stringify(settingsForm),
      )

    ElMessage.success(
      '系统设置保存成功',
    )
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '系统设置保存失败',
      ),
    )
  } finally {
    saving.value = false
  }
}


/* ==============================
   恢复上次保存
================================ */

async function restoreSavedSettings() {
  if (!originalSettings.value) {
    ElMessage.warning(
      '暂无可恢复的设置',
    )
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定恢复到上一次保存的系统设置吗？当前未保存的修改将丢失。',
      '恢复设置',
      {
        confirmButtonText: '确认恢复',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    applySettings(
      originalSettings.value,
    )

    formRef.value?.clearValidate()

    ElMessage.success(
      '已恢复到上一次保存的设置',
    )
  } catch (error) {
    if (
      error === 'cancel' ||
      error === 'close'
    ) {
      return
    }

    ElMessage.error(
      '恢复设置失败',
    )
  }
}


/* ==============================
   生命周期
================================ */

onMounted(() => {
  loadSystemSettings()
})
</script>


<template>
  <div
    v-loading="loading"
    class="settings-page"
  >
    <!-- 页面头部 -->
    <section class="page-heading">
      <div>
        <h2>系统设置</h2>

        <p>
          管理平台基础信息、AI生成参数与自动化功能
        </p>
      </div>

      <div class="heading-actions">
        <el-button
          :icon="Refresh"
          class="restore-button"
          @click="restoreSavedSettings"
        >
          恢复修改
        </el-button>

        <el-button
          type="primary"
          :icon="Check"
          :loading="saving"
          class="save-button"
          @click="saveSystemSettings"
        >
          保存设置
        </el-button>
      </div>
    </section>

    <!-- 状态概览 -->
    <section class="summary-grid">
      <article class="summary-card">
        <div class="summary-icon purple">
          <el-icon>
            <Setting />
          </el-icon>
        </div>

        <div>
          <span>系统主题</span>

          <strong>
            {{
              themeOptions.find(
                (item) =>
                  item.value ===
                  settingsForm.theme,
              )?.label || '-'
            }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon cyan">
          <el-icon>
            <Connection />
          </el-icon>
        </div>

        <div>
          <span>AI服务商</span>

          <strong>
            {{ settingsForm.ai_provider }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon green">
          <el-icon>
            <Monitor />
          </el-icon>
        </div>

        <div>
          <span>默认平台</span>

          <strong>
            {{
              settingsForm.default_platform
            }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <div class="summary-icon orange">
          <el-icon>
            <Bell />
          </el-icon>
        </div>

        <div>
          <span>已开启功能</span>

          <strong>
            {{ enabledFeatureCount }}/3
          </strong>
        </div>
      </article>
    </section>

    <el-form
      ref="formRef"
      :model="settingsForm"
      :rules="formRules"
      label-position="top"
      class="settings-form"
    >
      <div class="settings-grid">
        <!-- 平台基础设置 -->
        <section class="setting-card">
          <div class="card-heading">
            <div class="heading-icon purple">
              <el-icon>
                <Monitor />
              </el-icon>
            </div>

            <div>
              <h3>平台基础设置</h3>

              <p>
                设置平台名称、默认渠道、时区和显示主题
              </p>
            </div>
          </div>

          <div class="card-content">
            <el-form-item
              label="平台名称"
              prop="platform_name"
            >
              <el-input
                v-model="settingsForm.platform_name"
                maxlength="100"
                show-word-limit
                placeholder="请输入平台名称"
              />
            </el-form-item>

            <el-form-item
              label="平台副标题"
              prop="platform_subtitle"
            >
              <el-input
                v-model="settingsForm.platform_subtitle"
                maxlength="200"
                show-word-limit
                placeholder="请输入平台副标题"
              />
            </el-form-item>

            <div class="form-row">
              <el-form-item
                label="默认发布平台"
                prop="default_platform"
              >
                <el-select
                  v-model="settingsForm.default_platform"
                  style="width: 100%"
                >
                  <el-option
                    v-for="platform in platformOptions"
                    :key="platform"
                    :label="platform"
                    :value="platform"
                  />
                </el-select>
              </el-form-item>

              <el-form-item
                label="系统时区"
                prop="timezone"
              >
                <el-select
                  v-model="settingsForm.timezone"
                  filterable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in timezoneOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </div>

            <el-form-item
              label="界面主题"
              prop="theme"
            >
              <el-radio-group
                v-model="settingsForm.theme"
                class="theme-selector"
              >
                <el-radio-button
                  v-for="item in themeOptions"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <div class="setting-note">
              当前系统界面以深色主题完成设计。浅色和跟随系统模式仅保存配置，后续可继续开发对应主题样式。
            </div>
          </div>
        </section>

        <!-- AI 模型设置 -->
        <section class="setting-card">
          <div class="card-heading">
            <div class="heading-icon cyan">
              <el-icon>
                <Connection />
              </el-icon>
            </div>

            <div>
              <h3>AI模型设置</h3>

              <p>
                配置内容分析、脚本生成和智能复盘参数
              </p>
            </div>
          </div>

          <div class="card-content">
            <div class="form-row">
              <el-form-item
                label="AI服务商"
                prop="ai_provider"
              >
                <el-select
                  v-model="settingsForm.ai_provider"
                  filterable
                  allow-create
                  style="width: 100%"
                >
                  <el-option
                    v-for="provider in aiProviderOptions"
                    :key="provider"
                    :label="provider"
                    :value="provider"
                  />
                </el-select>
              </el-form-item>

              <el-form-item
                label="模型名称"
                prop="ai_model"
              >
                <el-input
                  v-model="settingsForm.ai_model"
                  maxlength="100"
                  placeholder="例如：gpt-5、deepseek-chat"
                />
              </el-form-item>
            </div>

            <el-form-item label="生成温度">
              <div class="temperature-control">
                <el-slider
                  v-model="settingsForm.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  :show-tooltip="true"
                />

                <el-input-number
                  v-model="settingsForm.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  :precision="1"
                  controls-position="right"
                />
              </div>

              <p class="field-description">
                {{ temperatureDescription }}
              </p>
            </el-form-item>

            <div class="setting-note security-note">
              API Key 不在此页面或数据库中保存。生产环境应通过后端环境变量或专用密钥管理服务配置。
            </div>
          </div>
        </section>

        <!-- 自动化功能 -->
        <section class="setting-card full-width-card">
          <div class="card-heading">
            <div class="heading-icon green">
              <el-icon>
                <Setting />
              </el-icon>
            </div>

            <div>
              <h3>自动化功能</h3>

              <p>
                控制AI生成、自动审核和系统通知
              </p>
            </div>
          </div>

          <div class="feature-grid">
            <article class="feature-item">
              <div class="feature-copy">
                <div class="feature-icon purple">
                  <el-icon>
                    <Connection />
                  </el-icon>
                </div>

                <div>
                  <strong>AI内容生成</strong>

                  <p>
                    允许系统调用AI模型生成内容分析、脚本和优化建议
                  </p>
                </div>
              </div>

              <el-switch
                v-model="settingsForm.enable_ai_generation"
                inline-prompt
                active-text="开"
                inactive-text="关"
              />
            </article>

            <article class="feature-item">
              <div class="feature-copy">
                <div class="feature-icon orange">
                  <el-icon>
                    <Check />
                  </el-icon>
                </div>

                <div>
                  <strong>自动审核</strong>

                  <p>
                    允许符合条件的内容自动通过审核并进入下一业务阶段
                  </p>
                </div>
              </div>

              <el-switch
                v-model="settingsForm.enable_auto_review"
                inline-prompt
                active-text="开"
                inactive-text="关"
              />
            </article>

            <article class="feature-item">
              <div class="feature-copy">
                <div class="feature-icon cyan">
                  <el-icon>
                    <Bell />
                  </el-icon>
                </div>

                <div>
                  <strong>系统通知</strong>

                  <p>
                    在任务状态变化、审核完成或接口异常时发送通知
                  </p>
                </div>
              </div>

              <el-switch
                v-model="settingsForm.enable_notifications"
                inline-prompt
                active-text="开"
                inactive-text="关"
              />
            </article>
          </div>
        </section>
      </div>
    </el-form>
  </div>
</template>


<style scoped>
.settings-page {
  width: 100%;
  min-width: 0;
  min-height: 100%;
  color: var(--app-text-primary);
}

/* ==============================
   页面头部
================================ */

.page-heading {
  display: flex;
  min-height: 48px;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 12px;
}

.page-heading h2 {
  margin: 0;
  color: #f1f3f8;
  font-size: 15px;
  font-weight: 600;
  line-height: 22px;
}

.page-heading p {
  margin: 4px 0 0;
  color: #687184;
  font-size: 9px;
}

.heading-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.heading-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 14px;
  font-size: 9px;
  border-radius: 5px;
}

.restore-button {
  color: #9aa2b2 !important;
  background: #151a25 !important;
  border-color: #303747 !important;
}

.restore-button:hover {
  color: #c4baff !important;
  background:
    rgba(118, 91, 255, 0.09) !important;
  border-color: #56468d !important;
}

.save-button {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    ) !important;
  border-color: #765bff !important;
  box-shadow:
    0 5px 14px rgba(118, 91, 255, 0.22);
}

.save-button:hover {
  background:
    linear-gradient(
      135deg,
      #846cff,
      #7055ef
    ) !important;
  border-color: #846cff !important;
}

/* ==============================
   概览卡片
================================ */

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}

.summary-card {
  display: flex;
  height: 70px;
  align-items: center;
  gap: 11px;
  padding: 11px 13px;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.015),
      transparent 65%
    ),
    #111621;
  border: 1px solid #202736;
  border-radius: 7px;
}

.summary-icon {
  display: flex;
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  border-radius: 9px;
}

.summary-icon.purple,
.heading-icon.purple,
.feature-icon.purple {
  color: #927dff;
  background:
    rgba(118, 91, 255, 0.12);
}

.summary-icon.cyan,
.heading-icon.cyan,
.feature-icon.cyan {
  color: #48c5d2;
  background:
    rgba(72, 197, 210, 0.1);
}

.summary-icon.green,
.heading-icon.green {
  color: #55d6a2;
  background:
    rgba(45, 190, 135, 0.11);
}

.summary-icon.orange,
.feature-icon.orange {
  color: #e2ae60;
  background:
    rgba(226, 174, 96, 0.1);
}

.summary-card > div:last-child {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.summary-card span {
  color: #737c8d;
  font-size: 8px;
}

.summary-card strong {
  margin-top: 5px;
  overflow: hidden;
  color: #edf0f5;
  font-size: 13px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ==============================
   设置卡片
================================ */

.settings-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.setting-card {
  min-width: 0;
  overflow: hidden;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.012),
      transparent 58%
    ),
    #0f141e;
  border: 1px solid #202736;
  border-radius: 7px;
}

.full-width-card {
  grid-column: 1 / -1;
}

.card-heading {
  display: flex;
  min-height: 64px;
  align-items: center;
  gap: 11px;
  padding: 0 16px;
  background: #111621;
  border-bottom: 1px solid #202736;
}

.heading-icon {
  display: flex;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  border-radius: 8px;
}

.card-heading h3 {
  margin: 0;
  color: #e5e7ed;
  font-size: 11px;
  font-weight: 600;
}

.card-heading p {
  margin: 4px 0 0;
  color: #687184;
  font-size: 8px;
}

.card-content {
  padding: 16px;
}

.settings-form :deep(.el-form-item) {
  margin-bottom: 17px;
}

.settings-form
  :deep(.el-form-item__label) {
  margin-bottom: 6px;
  color: #aeb5c2;
  font-size: 9px;
  line-height: 14px;
}

.settings-form :deep(.el-input__wrapper),
.settings-form :deep(.el-select__wrapper),
.settings-form :deep(.el-input-number) {
  min-height: 34px;
  background: #0b1019;
  border-radius: 5px;
  box-shadow:
    0 0 0 1px #293142 inset;
}

.settings-form
  :deep(.el-input__wrapper:hover),
.settings-form
  :deep(.el-select__wrapper:hover) {
  box-shadow:
    0 0 0 1px #3a4355 inset;
}

.settings-form
  :deep(.el-input__wrapper.is-focus),
.settings-form
  :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.07);
}

.settings-form :deep(.el-input__inner),
.settings-form
  :deep(.el-select__selected-item),
.settings-form
  :deep(.el-select__placeholder) {
  color: #afb6c3;
  font-size: 9px;
}

.form-row {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.theme-selector {
  display: grid;
  width: 100%;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
}

.theme-selector
  :deep(.el-radio-button) {
  width: 100%;
}

.theme-selector
  :deep(.el-radio-button__inner) {
  width: 100%;
  height: 34px;
  color: #8b93a2;
  font-size: 9px;
  line-height: 17px;
  background: #10151f;
  border-color: #293142;
  box-shadow: none;
}

.theme-selector
  :deep(
    .el-radio-button__original-radio:checked
      + .el-radio-button__inner
  ) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    );
  border-color: #765bff;
  box-shadow: none;
}

/* ==============================
   温度参数
================================ */

.temperature-control {
  display: grid;
  width: 100%;
  grid-template-columns:
    minmax(0, 1fr)
    112px;
  align-items: center;
  gap: 18px;
}

.temperature-control
  :deep(.el-slider__runway) {
  background: #242b39;
}

.temperature-control
  :deep(.el-slider__bar) {
  background:
    linear-gradient(
      90deg,
      #765bff,
      #9c87ff
    );
}

.temperature-control
  :deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  background: #8d76ff;
  border-color: #c1b6ff;
}

.field-description {
  margin: 7px 0 0;
  color: #687184;
  font-size: 8px;
}

.setting-note {
  padding: 10px 12px;
  color: #767f90;
  font-size: 8px;
  line-height: 15px;
  background:
    rgba(118, 91, 255, 0.045);
  border:
    1px solid rgba(118, 91, 255, 0.11);
  border-radius: 6px;
}

.security-note {
  color: #8b849e;
  background:
    rgba(226, 174, 96, 0.04);
  border-color:
    rgba(226, 174, 96, 0.11);
}

/* ==============================
   自动化功能
================================ */

.feature-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 14px 16px 16px;
}

.feature-item {
  display: flex;
  min-height: 86px;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  padding: 13px;
  background: #131824;
  border: 1px solid #242c3a;
  border-radius: 7px;
}

.feature-copy {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  gap: 10px;
}

.feature-icon {
  display: flex;
  width: 31px;
  height: 31px;
  flex: 0 0 31px;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border-radius: 7px;
}

.feature-copy strong {
  color: #d8dce4;
  font-size: 9px;
  font-weight: 500;
}

.feature-copy p {
  margin: 5px 0 0;
  color: #697284;
  font-size: 8px;
  line-height: 14px;
}

.feature-item :deep(.el-switch) {
  --el-switch-on-color: #765bff;
  --el-switch-off-color: #303747;

  flex: 0 0 auto;
}

/* ==============================
   加载样式
================================ */

.settings-page
  :deep(.el-loading-mask) {
  background:
    rgba(8, 11, 18, 0.72);
  backdrop-filter: blur(2px);
}

.settings-page
  :deep(.el-loading-spinner .path) {
  stroke: #765bff;
}

/* ==============================
   响应式
================================ */

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .full-width-card {
    grid-column: auto;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .page-heading {
    flex-direction: column;
  }

  .heading-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .summary-grid,
  .form-row {
    grid-template-columns: 1fr;
  }

  .temperature-control {
    grid-template-columns: 1fr;
  }
}
</style>