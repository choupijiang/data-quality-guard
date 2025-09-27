<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const formData = ref({
  name: '',
  description: '',
  status: 'active'
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在2-50个字符之间', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '项目描述最多500个字符', trigger: 'blur' }
  ]
}

const formRef = ref()

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    await api.post('/api/v1/projects/', formData.value)
    
    ElMessage.success('项目创建成功')
    router.push('/projects')
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.detail || '创建项目失败')
    } else {
      ElMessage.error('创建项目失败')
    }
  } finally {
    loading.value = false
  }
}

const cancelCreate = () => {
  router.push('/projects')
}
</script>

<template>
  <div class="create-project-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1>创建项目</h1>
          <p>创建一个新的数据库质量巡检项目</p>
        </div>
        <button class="apple-button apple-button-secondary" @click="cancelCreate">
          <el-icon><ArrowLeft /></el-icon>
          返回项目列表
        </button>
      </div>
    </div>

    <!-- Form Content -->
    <div class="form-content">
      <div class="form-card">
        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="120px"
          label-position="left"
          @submit.prevent="submitForm"
        >
          <!-- Project Name -->
          <el-form-item label="项目名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入项目名称"
              maxlength="50"
              show-word-limit
              size="large"
            />
          </el-form-item>

          <!-- Project Description -->
          <el-form-item label="项目描述" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              placeholder="请输入项目描述（选填）"
              maxlength="500"
              show-word-limit
              :rows="4"
              resize="none"
            />
          </el-form-item>

          <!-- Project Status -->
          <el-form-item label="项目状态">
            <el-radio-group v-model="formData.status">
              <el-radio value="active">
                <span class="status-active">
                  <el-icon><Plus /></el-icon>
                  启用
                </span>
              </el-radio>
              <el-radio value="inactive">
                <span class="status-inactive">
                  <el-icon><Plus /></el-icon>
                  禁用
                </span>
              </el-radio>
            </el-radio-group>
            <div class="status-help">
              <small>
                启用状态的项目可以正常创建巡检任务，禁用状态的项目暂停所有相关任务
              </small>
            </div>
          </el-form-item>

          <!-- Form Actions -->
          <div class="form-actions">
            <button 
              class="apple-button apple-button-secondary" 
              @click="cancelCreate"
              :disabled="loading"
            >
              取消
            </button>
            <button 
              class="apple-button apple-button-primary" 
              @click="submitForm"
              :disabled="loading"
            >
              <el-icon v-if="!loading"><Plus /></el-icon>
              {{ loading ? '创建中...' : '创建项目' }}
            </button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.create-project-container {
  min-height: 100vh;
  background: var(--gray-8);
}

/* Page Header */
.page-header {
  padding: var(--spacing-2xl) 0;
  background: var(--gray-9);
  border-bottom: 1px solid var(--gray-5);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.title-section h1 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-sm) 0;
}

.title-section p {
  font-size: var(--font-size-lg);
  color: var(--gray-3);
  margin: 0;
}

/* Form Content */
.form-content {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.form-card {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
}

/* Form Styling */
.el-form {
  max-width: 100%;
}

.el-form-item {
  margin-bottom: var(--spacing-xl);
}

.el-form-item__label {
  font-weight: 600;
  color: var(--gray-1);
  font-size: var(--font-size-base);
}

.el-input {
  font-size: var(--font-size-base);
}

.el-input__inner {
  background: var(--gray-8);
  border: 1px solid var(--gray-5);
  color: var(--gray-1);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
}

.el-input__inner:focus {
  border-color: var(--apple-blue);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
}

.el-textarea__inner {
  background: var(--gray-8);
  border: 1px solid var(--gray-5);
  color: var(--gray-1);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
}

.el-textarea__inner:focus {
  border-color: var(--apple-blue);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
}

/* Radio Group Styling */
.el-radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.el-radio {
  margin-right: 0;
  margin-bottom: 0;
}

.el-radio__label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 500;
}

.status-active {
  color: var(--apple-green);
}

.status-inactive {
  color: var(--apple-red);
}

.status-help {
  margin-top: var(--spacing-sm);
  color: var(--gray-3);
  line-height: 1.4;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--gray-5);
}

.apple-button {
  min-width: 120px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .form-content {
    padding: var(--spacing-md);
  }
  
  .form-card {
    padding: var(--spacing-lg);
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .apple-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: var(--spacing-xl) 0;
  }
  
  .title-section h1 {
    font-size: var(--font-size-2xl);
  }
  
  .form-content {
    padding: var(--spacing-sm);
  }
  
  .form-card {
    padding: var(--spacing-md);
  }
}

/* Animations */
.form-card {
  animation: apple-fade-in 0.5s ease-out;
}
</style>