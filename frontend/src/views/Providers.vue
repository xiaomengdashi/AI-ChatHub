<template>
  <div class="providers-view"></div>
  <div class="providers-container">
    <div class="header">
      <h2>模型提供商管理</h2>
      <a-button type="primary" @click="showAddModal">
        <template #icon>
          <PlusOutlined />
        </template>
        添加平台
      </a-button>
    </div>

    <div class="table-container">
      <ResponsiveTable 
      :columns="columns" 
      :data-source="providers" 
      :loading="loading"
      row-key="id"
      :pagination="{ pageSize: 10 }"
      :mobile-hidden-columns="['description', 'created_at']"
      :tablet-hidden-columns="['created_at']"
      :min-scroll-width="1000"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="editProvider(record)">
              编辑
            </a-button>
            <a-popconfirm
              title="确定要删除这个平台吗？"
              @confirm="deleteProvider(record.id)"
            >
              <a-button type="link" size="small" danger>
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </ResponsiveTable>
    </div>

    <!-- 添加/编辑模态框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑平台' : '添加平台'"
      @ok="handleSubmit"
      @cancel="handleCancel"
      :confirm-loading="submitting"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        layout="vertical"
      >
        <a-form-item label="平台标识" name="provider_key">
          <a-input 
            v-model:value="formData.provider_key" 
            placeholder="请输入平台标识（如：openai）"
            :disabled="isEdit"
          />
        </a-form-item>
        
        <a-form-item label="显示名称" name="display_name">
          <a-input 
            v-model:value="formData.display_name" 
            placeholder="请输入显示名称（如：OpenAI）"
          />
        </a-form-item>
        
        <a-form-item label="默认Base URL" name="default_base_url">
          <a-input 
            v-model:value="formData.default_base_url" 
            placeholder="请输入默认Base URL"
          />
        </a-form-item>
        
        <a-form-item label="排序" name="sort_order">
          <a-input-number 
            v-model:value="formData.sort_order" 
            :min="0"
            placeholder="排序值"
            style="width: 100%"
          />
        </a-form-item>
        
        <a-form-item label="状态" name="is_active">
          <a-switch 
            v-model:checked="formData.is_active"
            checked-children="启用"
            un-checked-children="禁用"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import request from '../utils/request'
import ResponsiveTable from '../components/ResponsiveTable.vue'

const loading = ref(false)
const providers = ref([])
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()

const columns = [
  {
    title: '平台标识',
    dataIndex: 'provider_key',
    key: 'provider_key',
    width: 150,
  },
  {
    title: '显示名称',
    dataIndex: 'display_name',
    key: 'display_name',
    width: 200,
  },
  {
    title: '默认Base URL',
    dataIndex: 'default_base_url',
    key: 'default_base_url',
    ellipsis: true,
  },
  {
    title: '排序',
    dataIndex: 'sort_order',
    key: 'sort_order',
    width: 80,
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 80,
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
  },
]

const formData = reactive({
  provider_key: '',
  display_name: '',
  default_base_url: '',
  sort_order: 0,
  is_active: true,
})

const rules = {
  provider_key: [
    { required: true, message: '请输入平台标识', trigger: 'blur' },
    { pattern: /^[a-z0-9_]+$/, message: '平台标识只能包含小写字母、数字和下划线', trigger: 'blur' }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' }
  ],
  default_base_url: [
    { required: true, message: '请输入默认Base URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
}

const loadProviders = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/providers')
    if (response.data.success) {
      providers.value = response.data.data
    } else {
      message.error(response.data.message || '获取平台列表失败')
    }
  } catch (error) {
    console.error('获取平台列表失败:', error)
    message.error('获取平台列表失败')
  } finally {
    loading.value = false
  }
}

const showAddModal = () => {
  isEdit.value = false
  resetForm()
  modalVisible.value = true
}

const editProvider = (record) => {
  isEdit.value = true
  Object.assign(formData, record)
  modalVisible.value = true
}

const resetForm = () => {
  Object.assign(formData, {
    provider_key: '',
    display_name: '',
    default_base_url: '',
    sort_order: 0,
    is_active: true,
  })
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validateFields()
    submitting.value = true
    
    let response
    if (isEdit.value) {
      response = await request.put(`/api/providers/${formData.id}`, formData)
    } else {
      response = await request.post('/api/providers', formData)
    }
    
    if (response.data.success) {
      message.success(isEdit.value ? '平台更新成功' : '平台创建成功')
      modalVisible.value = false
      loadProviders()
    } else {
      message.error(response.data.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    if (error.response?.data?.message) {
      message.error(error.response.data.message)
    } else {
      message.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  modalVisible.value = false
  resetForm()
}

const deleteProvider = async (id) => {
  try {
    const response = await request.delete(`/api/providers/${id}`)
    if (response.data.success) {
      message.success('平台删除成功')
      loadProviders()
    } else {
      message.error(response.data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除失败')
  }
}

onMounted(() => {
  loadProviders()
})
</script>

<style scoped>
.providers-view {
  height: 30px;
}

.providers-container {
  min-height: 100vh;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  position: relative;
}

.providers-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
  z-index: 1;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px 16px 0 0;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.table-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
  z-index: 1;
}

.table-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  border-radius: 16px 16px 0 0;
}

:deep(.ant-table) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: none;
}

:deep(.ant-table-thead > tr > th) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 700;
  color: #2d3748;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  padding: 20px 16px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  font-weight: 500;
  color: #2d3748;
  transition: all 0.3s ease;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: rgba(102, 126, 234, 0.05);
  transform: translateY(-1px);
}

:deep(.ant-table-tbody > tr) {
  transition: all 0.3s ease;
}

:deep(.ant-table-tbody > tr:hover) {
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
}

:deep(.ant-btn) {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

:deep(.ant-btn-primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

:deep(.ant-btn-primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.ant-btn-link) {
  color: #667eea;
  font-weight: 600;
}

:deep(.ant-btn-link:hover) {
  color: #5a6fd8;
  transform: translateY(-1px);
}

:deep(.ant-btn-link.ant-btn-dangerous) {
  color: #e53e3e;
}

:deep(.ant-btn-link.ant-btn-dangerous:hover) {
  color: #c53030;
  transform: translateY(-1px);
}

:deep(.ant-tag) {
  border-radius: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border: none;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.ant-tag-green) {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

:deep(.ant-tag-red) {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
}

:deep(.ant-modal) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.ant-modal-header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 16px 16px 0 0;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  padding: 20px 24px;
}

:deep(.ant-modal-title) {
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
}

:deep(.ant-modal-body) {
  padding: 24px;
}

:deep(.ant-form-item-label > label) {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

:deep(.ant-input) {
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  padding: 10px 12px;
  transition: all 0.3s ease;
}

:deep(.ant-input:hover) {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

:deep(.ant-input:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.ant-input-number) {
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.ant-input-number:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.ant-input-number-focused) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.ant-switch) {
  background: #cbd5e0;
}

:deep(.ant-switch-checked) {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
}

:deep(.ant-pagination) {
  margin-top: 24px;
  text-align: center;
}

:deep(.ant-pagination-item) {
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  font-weight: 600;
}

:deep(.ant-pagination-item-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

:deep(.ant-pagination-item-active a) {
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .providers-container {
    padding: 16px 12px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    text-align: left;
  }
  
  .header h2 {
    font-size: 20px;
  }
  
  .table-container {
    padding: 16px;
    overflow-x: auto;
  }
  
  :deep(.ant-table-tbody > tr > td) {
    padding: 12px 8px;
    font-size: 12px;
  }
  
  :deep(.ant-table-thead > tr > th) {
    padding: 12px 8px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .providers-container {
    padding: 12px 8px;
  }
  
  .header h2 {
    font-size: 18px;
  }
  
  .header .ant-btn {
    width: 100%;
    justify-self: stretch;
  }
  
  :deep(.ant-modal-body) {
    padding: 16px;
  }
  
  :deep(.ant-form-item) {
    margin-bottom: 16px;
  }
}
</style>