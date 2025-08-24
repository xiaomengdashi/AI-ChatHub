<template>
  <div class="management-container">
    <a-tabs v-model:activeKey="activeTab" class="management-tabs">
      <a-tab-pane key="providers" tab="模型提供商">
        <Providers />
      </a-tab-pane>
      <a-tab-pane key="api-keys" tab="API密钥">
        <ApiKeys />
      </a-tab-pane>
      <a-tab-pane key="models" tab="大模型管理">
        <Models />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script>
import { ref } from 'vue'
import Models from './Models.vue'
import ApiKeys from './ApiKeys.vue'
import Providers from './Providers.vue'

export default {
  name: 'Management',
  components: {
    Models,
    ApiKeys,
    Providers
  },
  setup() {
    const activeTab = ref('models')

    return {
      activeTab
    }
  }
}
</script>

<style scoped>
.management-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.management-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

:deep(.ant-tabs-tab) {
  font-size: 16px;
  padding: 12px 0;
}

:deep(.ant-tabs-tab-active) {
  font-weight: 600;
}

:deep(.ant-tabs-ink-bar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>