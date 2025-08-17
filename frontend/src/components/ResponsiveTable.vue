<template>
  <div class="responsive-table-wrapper">
    <!-- 移动端列选择器 -->
    <div class="mobile-column-selector" v-if="showColumnSelector">
      <a-button 
        type="text" 
        @click="toggleColumnSelector"
        class="column-toggle-btn"
      >
        <template #icon>
          <SettingOutlined />
        </template>
        选择列
      </a-button>
      
      <div class="column-selector-dropdown" v-show="columnSelectorVisible">
        <div class="column-selector-header">
          <span>显示列</span>
          <a-button type="text" size="small" @click="toggleColumnSelector">
            <CloseOutlined />
          </a-button>
        </div>
        <div class="column-selector-content">
          <a-checkbox-group v-model:value="visibleColumns" @change="onColumnChange">
            <div class="column-option" v-for="col in selectableColumns" :key="col.dataIndex || col.key">
              <a-checkbox :value="col.dataIndex || col.key">{{ col.title }}</a-checkbox>
            </div>
          </a-checkbox-group>
        </div>
      </div>
    </div>

    <!-- 表格容器 -->
    <div class="table-container" :class="{ 'mobile-optimized': isMobile }">
      <a-table
        v-bind="$attrs"
        :columns="computedColumns"
        :scroll="computedScroll"
        :size="tableSize"
        class="responsive-table"
      >
        <template v-for="(_, name) in $slots" #[name]="slotData">
          <slot :name="name" v-bind="slotData" />
        </template>
      </a-table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { SettingOutlined, CloseOutlined } from '@ant-design/icons-vue'

export default {
  name: 'ResponsiveTable',
  components: {
    SettingOutlined,
    CloseOutlined
  },
  props: {
    columns: {
      type: Array,
      required: true
    },
    // 移动端隐藏的列（按优先级）
    mobileHiddenColumns: {
      type: Array,
      default: () => []
    },
    // 平板端隐藏的列
    tabletHiddenColumns: {
      type: Array,
      default: () => []
    },
    // 是否显示列选择器
    showColumnSelector: {
      type: Boolean,
      default: true
    },
    // 最小滚动宽度
    minScrollWidth: {
      type: Number,
      default: 800
    }
  },
  setup(props) {
    const screenWidth = ref(window.innerWidth)
    const columnSelectorVisible = ref(false)
    const visibleColumns = ref([])

    // 响应式断点
    const isMobile = computed(() => screenWidth.value <= 768)
    const isTablet = computed(() => screenWidth.value <= 1024 && screenWidth.value > 768)
    const isDesktop = computed(() => screenWidth.value > 1024)

    // 表格尺寸
    const tableSize = computed(() => {
      if (isMobile.value) return 'small'
      if (isTablet.value) return 'middle'
      return 'middle'
    })

    // 可选择的列（排除固定列）
    const selectableColumns = computed(() => {
      if (!props.columns || !Array.isArray(props.columns)) {
        return []
      }
      return props.columns.filter(col => !col.fixed)
    })

    // 计算需要隐藏的列
    const hiddenColumns = computed(() => {
      if (isMobile.value) {
        return props.mobileHiddenColumns
      }
      if (isTablet.value) {
        return props.tabletHiddenColumns
      }
      return []
    })

    // 计算显示的列
    const computedColumns = computed(() => {
      if (!props.columns || !Array.isArray(props.columns)) {
        return []
      }
      
      let filteredColumns = []
      
      if (isMobile.value && props.showColumnSelector) {
        // 移动端使用用户选择的列
        filteredColumns = props.columns.filter(col => {
          if (col.fixed) return true // 固定列始终显示
          return visibleColumns.value.includes(col.dataIndex || col.key)
        })
      } else {
        // 其他情况使用自动隐藏逻辑
        filteredColumns = props.columns.filter(col => {
          const columnKey = col.dataIndex || col.key
          return !hiddenColumns.value.includes(columnKey)
        })
      }
      
      // 在移动端取消固定列设置，避免占用过多空间
      if (isMobile.value) {
        return filteredColumns.map(col => ({
          ...col,
          fixed: undefined // 移除固定列设置
        }))
      }
      
      return filteredColumns
    })

    // 计算滚动配置
    const computedScroll = computed(() => {
      const baseScroll = { x: props.minScrollWidth }
      
      if (isMobile.value) {
        baseScroll.x = Math.max(600, props.minScrollWidth * 0.6)
      } else if (isTablet.value) {
        baseScroll.x = Math.max(800, props.minScrollWidth * 0.8)
      }
      
      return baseScroll
    })

    // 初始化可见列
    const initVisibleColumns = () => {
      if (!selectableColumns.value || selectableColumns.value.length === 0) {
        visibleColumns.value = []
        return
      }
      
      if (isMobile.value) {
        // 移动端默认显示前3个非固定列
        const nonFixedColumns = selectableColumns.value.slice(0, 3)
        visibleColumns.value = nonFixedColumns.map(col => col.dataIndex || col.key)
      } else {
        // 其他情况显示所有列
        visibleColumns.value = selectableColumns.value.map(col => col.dataIndex || col.key)
      }
    }

    // 切换列选择器
    const toggleColumnSelector = () => {
      columnSelectorVisible.value = !columnSelectorVisible.value
    }

    // 列变化处理
    const onColumnChange = (checkedValues) => {
      visibleColumns.value = checkedValues
    }

    // 窗口大小变化处理
    const handleResize = () => {
      screenWidth.value = window.innerWidth
      if (!isMobile.value) {
        columnSelectorVisible.value = false
      }
    }

    onMounted(() => {
      initVisibleColumns()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      screenWidth,
      columnSelectorVisible,
      visibleColumns,
      isMobile,
      isTablet,
      isDesktop,
      tableSize,
      selectableColumns,
      computedColumns,
      computedScroll,
      toggleColumnSelector,
      onColumnChange
    }
  }
}
</script>

<style scoped>
.responsive-table-wrapper {
  position: relative;
}

/* 移动端列选择器 */
.mobile-column-selector {
  position: relative;
  margin-bottom: 16px;
}

.column-toggle-btn {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  color: #667eea;
  font-weight: 500;
}

.column-toggle-btn:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.column-selector-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.column-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  color: #262626;
}

.column-selector-content {
  padding: 12px 16px;
}

.column-option {
  margin-bottom: 8px;
}

.column-option:last-child {
  margin-bottom: 0;
}

/* 表格容器 */
.table-container {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-container.mobile-optimized {
  border-radius: 6px;
}

/* 响应式表格样式 */
:deep(.responsive-table) {
  font-size: 14px;
}

:deep(.responsive-table .ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
  color: #262626;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.responsive-table .ant-table-tbody > tr > td) {
  border-bottom: 1px solid #f5f5f5;
}

:deep(.responsive-table .ant-table-tbody > tr:hover > td) {
  background: #f8f9ff;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .mobile-column-selector {
    display: block;
  }
  
  :deep(.responsive-table) {
    font-size: 12px;
  }
  
  :deep(.responsive-table .ant-table-thead > tr > th) {
    padding: 8px 4px;
    font-size: 12px;
  }
  
  :deep(.responsive-table .ant-table-tbody > tr > td) {
    padding: 8px 4px;
    font-size: 12px;
  }
  
  :deep(.responsive-table .ant-table-cell) {
    word-break: break-word;
  }
}

/* 平板端优化 */
@media (max-width: 1024px) and (min-width: 769px) {
  .mobile-column-selector {
    display: none;
  }
  
  :deep(.responsive-table) {
    font-size: 13px;
  }
  
  :deep(.responsive-table .ant-table-thead > tr > th) {
    padding: 12px 8px;
  }
  
  :deep(.responsive-table .ant-table-tbody > tr > td) {
    padding: 12px 8px;
  }
}

/* 桌面端 */
@media (min-width: 1025px) {
  .mobile-column-selector {
    display: none;
  }
}

/* 水平滚动条样式 */
:deep(.ant-table-body) {
  overflow-x: auto;
}

:deep(.ant-table-body::-webkit-scrollbar) {
  height: 6px;
}

:deep(.ant-table-body::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(.ant-table-body::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

:deep(.ant-table-body::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}
</style>