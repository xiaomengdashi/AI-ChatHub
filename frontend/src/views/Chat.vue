<template>
  <div class="chat-container">
    <div class="chat-layout">
      <!-- 移动端遮罩层 -->
      <div 
        class="sidebar-overlay" 
        :class="{ 'overlay-visible': sidebarVisible }"
        @click="sidebarVisible = false"
      ></div>
      
      <!-- 侧边栏 - 对话列表 -->
      <div class="sidebar" :class="{ 'sidebar-hidden': !sidebarVisible }">
        <div class="sidebar-header">
          <a-button 
            type="primary" 
            class="new-chat-btn"
            @click="startNewChat"
            size="large"
          >
            <template #icon><PlusOutlined /></template>
            <span class="btn-text">新对话</span>
          </a-button>
        </div>
        
        <div class="conversations-list">
          <div 
            v-for="conversation in conversations" 
            :key="conversation.conversation_id"
            class="conversation-item"
            :class="{ 'active': currentConversationId === conversation.conversation_id }"
            @click="selectConversation(conversation.conversation_id)"
          >
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-meta">
              <a-tag class="model-tag" color="blue">{{ getModelDisplayNameWithProvider(conversation.model) }}</a-tag>
              <span class="time">{{ formatTime(conversation.updated_at) }}</span>
            </div>
            <a-popconfirm
              title="确定要删除这个对话吗？"
              ok-text="删除"
              cancel-text="取消"
              placement="left"
              @confirm="deleteConversation(conversation.conversation_id)"
            >
              <a-button 
                class="delete-btn"
                size="small"
                type="text"
                danger
                shape="circle"
                @click.stop="noop"
              >
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </a-popconfirm>
          </div>
        </div>
      </div>
      
      <!-- 主聊天区域 -->
      <div class="chat-main">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-title">
            <!-- 移动端侧边栏切换按钮 -->
            <a-button 
              class="mobile-sidebar-toggle"
              type="text"
              @click="toggleSidebar"
            >
              <template #icon><MenuOutlined /></template>
            </a-button>
            <h3>{{ currentConversationTitle }}</h3>
          </div>
          <div class="header-controls">
            <div class="model-selector">
              <a-select 
                v-model:value="selectedModel" 
                placeholder="选择AI模型"
                style="width: 200px"
                @change="onModelChange"
              >
                <a-select-option
                  v-for="model in availableModels"
                  :key="model.id"
                  :value="model.model_name"
                >
                  <div class="model-option">
                    <span class="model-name">{{ model.display_name }}</span>
                    <span class="model-provider">{{ getProviderDisplayName(model.model_provider) }}</span>
                  </div>
                </a-select-option>
              </a-select>
            </div>
            <ThemeSwitcher />
          </div>
        </div>
        
        <!-- 消息区域 -->
        <div class="messages-container" ref="messagesContainer" @scroll="onScroll">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">💬</div>
            <h3>开始新的对话</h3>
            <p>选择一个AI模型，然后输入您的问题</p>
          </div>
          
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <a-avatar v-if="message.role === 'user'" class="user-avatar">
                <template #icon><UserOutlined /></template>
              </a-avatar>
              <a-avatar v-else class="ai-avatar">
                <template #icon><MessageOutlined /></template>
              </a-avatar>
            </div>
            
            <div class="message-content">
              <!-- 推理内容显示 -->
              <div v-if="message.reasoning && message.reasoning.trim()" class="reasoning-content">
                <div class="reasoning-header" @click="toggleReasoning(message.id)">
                  <div class="reasoning-header-left">
                    <BulbOutlined />
                    <span>推理过程</span>
                    <span v-if="message.reasoningCollapsed" class="reasoning-preview">
                      ({{ message.reasoning.length > 50 ? message.reasoning.substring(0, 50) + '...' : message.reasoning }})
                    </span>
                  </div>
                  <div class="reasoning-toggle">
                    <RightOutlined v-if="message.reasoningCollapsed" class="toggle-icon" />
                    <DownOutlined v-else class="toggle-icon" />
                  </div>
                </div>
                <div 
                  v-show="!message.reasoningCollapsed" 
                  class="reasoning-text"
                >
                  <MarkdownRenderer :content="message.reasoning" />
                </div>
              </div>
              <!-- AI回复内容 -->
              <div class="message-text">
                <MarkdownRenderer v-if="message.role === 'assistant'" :content="message.content" />
                <span v-else>{{ message.content }}</span>
                <span v-if="message.isStreaming" class="streaming-cursor">|</span>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          
          <!-- 滚动到底部按钮 -->
          <a-float-button 
            v-if="showScrollButton" 
            class="scroll-to-bottom-btn"
            @click="scrollToBottom(true)"
            :style="{ right: '24px', bottom: '120px' }"
          >
            <template #icon><DownOutlined /></template>
            <a-badge v-if="hasNewContent" dot class="new-content-indicator" />
          </a-float-button>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <div class="input-wrapper">
              <a-textarea
                ref="messageInput"
                v-model:value="inputMessage"
                :rows="2"
                placeholder="输入您的消息..."
                @keydown="handleKeydown"
                class="message-input"
                :disabled="isLoading"
              />
              <a-button 
                type="primary" 
                class="send-btn"
                @click="sendMessage"
                size="large"
                :disabled="isLoading"
              >
                <template #icon>
                  <SendOutlined />
                </template>
              </a-button>
            </div>
          </div>
          <div class="input-hint">
            <span class="hint-text">按 Enter 发送，Shift + Enter 换行</span>
            <span class="model-info">当前模型: {{ selectedModel }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { message } from 'ant-design-vue'
import request, { API_BASE_URL } from '../utils/request'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'
import { 
  UserOutlined,
  MessageOutlined,
  BulbOutlined, 
  SendOutlined, 
  DownOutlined, 
  DeleteOutlined, 
  PlusOutlined,
  RightOutlined,
  MenuOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'Chat',
  components: {
    MarkdownRenderer,
    ThemeSwitcher,
    UserOutlined,
    MessageOutlined,
    BulbOutlined,
    SendOutlined,
    DownOutlined,
    DeleteOutlined,
    PlusOutlined,
    RightOutlined,
    MenuOutlined
  },
  data() {
    return {
      conversations: [],
      messages: [],
      currentConversationId: null,
      currentConversationTitle: '新对话',
      selectedModel: '',
      previousModel: '', // 用于跟踪之前选择的模型
      availableModels: [],
      providers: [], // 提供商列表
      inputMessage: '',
      isLoading: false,
      userId: null,
      showScrollButton: false,
      hasNewContent: false,
      lastScrollTop: 0,
      currentAbortController: null, // 当前流式请求的控制器
      currentStreamingConversationId: null, // 当前正在流式输出的对话ID
      sidebarVisible: window.innerWidth > 768 // 侧边栏显示状态，移动端默认隐藏
    }
  },
  async mounted() {
    await this.loadModels()
    await this.loadProviders()
    await this.loadConversations()
    
    // 检查URL参数中是否有conversation参数
    const conversationId = this.$route.query.conversation
    if (conversationId) {
      // 等待对话列表加载完成后再选择对话
      await this.$nextTick()
      await this.selectConversation(conversationId)
    } else if (this.conversations.length > 0) {
      // 如果没有指定对话ID且有对话记录，自动选择第一个对话
      await this.$nextTick()
      await this.selectConversation(this.conversations[0].conversation_id)
    }
  },
  methods: {
    async loadModels() {
      try {
        const response = await request.get('/api/models')
        this.availableModels = response.data
        console.log('加载的模型数据:', this.availableModels)
        
        // 如果有可用模型且当前选择的模型不在列表中，选择第一个模型
        if (this.availableModels.length > 0) {
          const currentModelExists = this.availableModels.some(model => model.model_name === this.selectedModel)
          if (!currentModelExists) {
            this.selectedModel = this.availableModels[0].model_name
            console.log('自动选择第一个模型:', this.selectedModel)
          }
          // 初始化previousModel
          this.previousModel = this.selectedModel
        }
      } catch (error) {
        console.error('加载模型失败:', error)
        message.error('加载模型失败')
      }
    },
    
    async loadConversations() {
      try {
        const response = await request.get('/api/conversations')
        this.conversations = response.data
      } catch (error) {
        console.error('加载对话列表失败:', error)
      }
    },
    
    async loadProviders() {
      try {
        const response = await request.get('/api/providers')
        if (response.data.success) {
          this.providers = response.data.data
        } else {
          console.error('获取提供商列表失败:', response.data.message)
        }
      } catch (error) {
        console.error('加载提供商列表失败:', error)
      }
    },
    
    async selectConversation(conversationId) {
      // 检查是否有正在进行的流式输出
      if (this.isLoading && this.currentAbortController) {
        message.warning('AI正在回答问题，请等待回答完成后再切换对话')
        return
      }
      
      this.currentConversationId = conversationId
      const conversation = this.conversations.find(c => c.conversation_id === conversationId)
      
      if (conversation) {
        this.currentConversationTitle = conversation.title
        this.selectedModel = conversation.model
        // 更新previousModel，避免在切换对话时触发新建对话
        this.previousModel = conversation.model
      }
      
      try {
        const response = await request.get(`/api/conversations/${conversationId}/messages`)
        this.messages = response.data.map(message => ({
          ...message,
          reasoningCollapsed: message.reasoning && message.reasoning.trim() ? true : false
        }))
        
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      } catch (error) {
        console.error('加载消息失败:', error)
        message.error('加载消息失败')
      }
    },
    
    startNewChat() {
      this.currentConversationId = null
      this.currentConversationTitle = '新对话'
      this.messages = []
      this.inputMessage = ''
    },
    
    toggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible
    },
    
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return
      
      const userMessage = this.inputMessage.trim()
      
      // 获取认证token，在清空输入框之前检查
      const token = localStorage.getItem('token')
      if (!token) {
        message.error('请先登录')
        return
      }
      
      // 清空输入框
      this.inputMessage = ''
      
      // 直接操作DOM确保清空
      if (this.$refs.messageInput) {
        this.$refs.messageInput.focus()
        this.$refs.messageInput.blur()
      }
      
      // 确保DOM更新
      await this.$nextTick()
      
      // 添加用户消息到界面
      this.messages.push({
        id: Date.now(),
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      })
      
      this.isLoading = true
      this.scrollToBottom()
      
      // 创建AI消息占位符
      const aiMessageId = Date.now() + 1
      const aiMessage = {
        id: aiMessageId,
        role: 'assistant',
        content: '',
        reasoning: '',
        timestamp: new Date().toISOString(),
        isStreaming: true,
        reasoningCollapsed: true // 默认折叠推理内容
      }
      this.messages.push(aiMessage)
      this.scrollToBottom()
      
      try {
        
        // 创建AbortController来控制流式请求
        this.currentAbortController = new AbortController()
        this.currentStreamingConversationId = this.currentConversationId
        
        // 使用流式API
        const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            message: userMessage,
            model: this.selectedModel,
            conversation_id: this.currentConversationId
          }),
          signal: this.currentAbortController.signal
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() // 保留最后一个可能不完整的行
          
          for (const line of lines) {
            if (line.trim()) {
              try {
                // 处理SSE格式：data: {...}
                let jsonStr = line.trim()
                if (jsonStr.startsWith('data: ')) {
                  jsonStr = jsonStr.substring(6) // 移除 "data: " 前缀
                }
                
                if (jsonStr) {
                  const data = JSON.parse(jsonStr)
                  console.log('收到流式数据:', data) // 调试日志
                  
                  if (data.type === 'start') {
                    // 更新对话ID
                    if (!this.currentConversationId) {
                      this.currentConversationId = data.conversation_id
                      this.currentConversationTitle = userMessage.length > 30 
                        ? userMessage.substring(0, 30) + '...' 
                        : userMessage
                    }
                  } else if (data.type === 'content') {
                    // 实时更新AI消息内容
                    const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
                    if (messageIndex !== -1) {
                      this.messages[messageIndex].content += data.content
                      this.smartScrollToBottom()
                    }
                  } else if (data.type === 'reasoning') {
                    // 实时更新推理内容
                    const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
                    if (messageIndex !== -1) {
                      this.messages[messageIndex].reasoning += data.content
                      this.smartScrollToBottom()
                    }
                  } else if (data.type === 'end') {
                    // 流式输出结束
                    const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
                    if (messageIndex !== -1) {
                      this.messages[messageIndex].isStreaming = false
                    }
                    // 清理流式状态
                    this.currentAbortController = null
                    this.currentStreamingConversationId = null
                    // 重新加载对话列表
                    await this.loadConversations()
                  } else if (data.type === 'error') {
                    console.error('流式输出错误:', data.content)
                    message.error(`AI回复出错: ${data.content}`)
                    // 移除错误的消息
                    const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
                    if (messageIndex !== -1) {
                      this.messages.splice(messageIndex, 1)
                    }
                  }
                }
              } catch (parseError) {
                console.error('解析流式数据失败:', parseError, '原始数据:', line)
              }
            }
          }
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('流式请求被用户取消')
          // 检查是否是当前对话的请求被取消
          if (this.currentStreamingConversationId === this.currentConversationId) {
            const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
            if (messageIndex !== -1) {
              const currentMessage = this.messages[messageIndex]
              // 如果消息有内容，保存部分消息
              if (currentMessage.content.trim()) {
                console.log('保存被取消的部分消息')
                currentMessage.isStreaming = false
                // 调用后端API保存部分消息
                try {
                  await request.post('/api/chat/save-partial', {
                    conversation_id: this.currentConversationId,
                    message_id: aiMessageId,
                    content: currentMessage.content,
                    reasoning: currentMessage.reasoning || ''
                  })
                  console.log('部分消息保存成功')
                } catch (saveError) {
                  console.error('保存部分消息失败:', saveError)
                }
              } else {
                // 如果消息为空，删除消息
                this.messages.splice(messageIndex, 1)
              }
            }
          }
        } else {
          console.error('发送消息失败:', error)
          message.error('发送消息失败: ' + error.message)
          // 移除错误的消息
          const messageIndex = this.messages.findIndex(m => m.id === aiMessageId)
          if (messageIndex !== -1) {
            this.messages.splice(messageIndex, 1)
          }
          // 注意：不再恢复输入框内容，因为用户消息已经添加到界面
        }
      } finally {
        this.isLoading = false
        this.currentAbortController = null
        this.currentStreamingConversationId = null
      }
    },
    
    handleKeydown(event) {
      // Handle Enter key without Shift modifier
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        this.sendMessage()
      }
      // Handle Shift+Enter to add new line
      else if (event.key === 'Enter' && event.shiftKey) {
        // Allow default behavior (new line)
        return
      }
    },
    
    async deleteConversation(conversationId) {
      try {
        await request.delete(`/api/conversations/${conversationId}`)
        await this.loadConversations()
        if (this.currentConversationId === conversationId) {
          this.startNewChat()
        }
        message.success('对话已删除')
      } catch (error) {
        console.error('删除对话失败:', error)
        message.error('删除对话失败')
      }
    },
    noop() {},
    onModelChange() {
      // 模型变更时创建新对话
      console.log('模型已切换为:', this.selectedModel)
      
      // 只有在模型真正发生变化时才创建新对话
      if (this.previousModel && this.previousModel !== this.selectedModel) {
        // 如果当前有正在进行的流式输出，先取消
        if (this.isLoading && this.currentAbortController) {
          this.currentAbortController.abort()
        }
        
        // 创建新对话
        this.startNewChat()
        message.info(`已切换到 ${this.getModelDisplayName(this.selectedModel)}，创建新对话`)
      }
      
      // 更新之前的模型记录
      this.previousModel = this.selectedModel
    },
    

    
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // 1分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 24小时内
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return date.toLocaleDateString()
      }
    },
    
    scrollToBottom(smooth = false) {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          const scrollOptions = {
            top: container.scrollHeight,
            behavior: smooth ? 'smooth' : 'auto'
          }
          container.scrollTo(scrollOptions)
        }
      })
    },
    
    shouldAutoScroll() {
      const container = this.$refs.messagesContainer
      if (!container) return true
      
      const { scrollTop, scrollHeight, clientHeight } = container
      return scrollHeight - scrollTop - clientHeight < 100
    },
    
    smartScrollToBottom() {
      if (this.shouldAutoScroll()) {
        this.scrollToBottom(true)
      } else {
        this.hasNewContent = true
      }
    },
    
    onScroll() {
      const container = this.$refs.messagesContainer
      if (!container) return
      
      const { scrollTop, scrollHeight, clientHeight } = container
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
      
      this.showScrollButton = !isNearBottom
      
      if (isNearBottom) {
        this.hasNewContent = false
      }
      
      this.lastScrollTop = scrollTop
    },
    
    toggleReasoning(messageId) {
      const message = this.messages.find(m => m.id === messageId)
      if (message) {
        message.reasoningCollapsed = !message.reasoningCollapsed
      }
    },
    
    getProviderDisplayName(provider) {
      // 从后端获取的providers数据中查找显示名称
      const providerData = this.providers.find(p => p.provider_key === provider)
      if (providerData && providerData.display_name) {
        return providerData.display_name
      }
    },
    
    getModelDisplayName(modelName) {
      const model = this.availableModels.find(m => m.model_name === modelName)
      return model ? model.display_name : modelName
    },
    
    getModelDisplayNameWithProvider(modelName) {
      const model = this.availableModels.find(m => m.model_name === modelName)
      if (model) {
        const providerName = this.getProviderDisplayName(model.model_provider)
        return `${model.display_name} | ${providerName}`
      }
      return modelName
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  position: relative;
  overflow: hidden;
}

.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(102, 126, 234, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.chat-layout {
  display: flex;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* 侧边栏样式 */
.sidebar {
  width: 320px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  border-right: 2px solid rgba(102, 126, 234, 0.12);
  display: flex;
  flex-direction: column;
  box-shadow: 
    8px 0 32px rgba(0, 0, 0, 0.08),
    4px 0 16px rgba(102, 126, 234, 0.05);
  position: relative;
  backdrop-filter: blur(20px);
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  z-index: 1;
}



.sidebar-header {
  padding: 24px 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.08);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: relative;
  z-index: 2;
}

.sidebar-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px;
  right: 20px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.2), transparent);
}

:deep(.new-chat-btn) {
  width: 100%;
  height: 56px;
  font-weight: 700;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  box-shadow: 
    0 10px 30px rgba(99, 102, 241, 0.3),
    0 4px 15px rgba(139, 92, 246, 0.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:deep(.new-chat-btn::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s;
}

:deep(.new-chat-btn:hover::before) {
  left: 100%;
}

:deep(.new-chat-btn:hover) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 15px 40px rgba(99, 102, 241, 0.4),
    0 8px 25px rgba(139, 92, 246, 0.3);
}

:deep(.new-chat-btn:active) {
  transform: translateY(-1px) scale(0.98);
}

:deep(.new-chat-btn .btn-text) {
  margin-left: 8px;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.5) 0%, rgba(241, 245, 249, 0.3) 100%);
}

.conversations-list::-webkit-scrollbar {
  width: 6px;
}

.conversations-list::-webkit-scrollbar-track {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 3px;
}

.conversations-list::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 3px;
  transition: all 0.3s ease;
}

.conversations-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}

.conversation-item {
  padding: 18px 16px;
  margin-bottom: 10px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: 2px solid rgba(102, 126, 234, 0.08);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
  backdrop-filter: blur(20px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.conversation-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.06) 100%);
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.12),
    0 4px 16px rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.conversation-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.2),
    0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.conversation-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 0 4px 4px 0;
}

.conversation-title {
  font-weight: 700;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #1a202c;
  font-size: 1.05rem;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 600;
  margin-top: 4px;
}

:deep(.model-tag) {
  font-size: 0.75rem;
  border-radius: 8px;
  font-weight: 500;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(10px);
}

:deep(.delete-btn:hover) {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
}

.conversation-item:hover .delete-btn {
  opacity: 1;
  transform: translateX(0);
}

/* 主聊天区域样式 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.chat-header {
  height: 40px;
  padding: 24px 32px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  position: relative;
}

.chat-header::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.chat-title h3 {
  margin: 0;
  color: #2d3748;
  font-weight: 700;
  font-size: 1.3rem;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.mobile-sidebar-toggle {
  display: none;
  margin-right: 12px;
  padding: 4px;
  border-radius: 6px;
  color: #667eea;
}

.mobile-sidebar-toggle:hover {
  background-color: rgba(102, 126, 234, 0.1);
  color: #5a67d8;
}

.chat-title {
  display: flex;
  align-items: center;
}

.model-option {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: 600;
  color: #2d3748;
}

.model-provider {
  font-size: 0.85rem;
  color: #718096;
  font-weight: 500;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  position: relative;
  background: linear-gradient(135deg, #fafbfc 0%, #f7fafc 100%);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #718096;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.message {
  display: flex;
  margin-bottom: 32px;
  align-items: flex-start;
  animation: slideUp 0.3s ease;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.08);
  position: relative;
}

.message:last-child {
  border-bottom: none;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 16px;
}

:deep(.user-avatar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

:deep(.ai-avatar) {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
}

.message-content {
  max-width: 75%;
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 2px solid rgba(102, 126, 234, 0.2);
  position: relative;
  transition: all 0.3s ease;
}

.message-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  border-radius: 16px 16px 0 0;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.message.user .message-content::before {
  background: rgba(255, 255, 255, 0.2);
}

.message-content:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.message.user .message-content:hover {
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
}

.reasoning-content {
  margin-bottom: 16px;
  border: 2px solid rgba(102, 126, 234, 0.25);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(102, 126, 234, 0.02);
  transition: all 0.3s ease;
}

.reasoning-header {
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.05);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  font-weight: 600;
}

.reasoning-header:hover {
  background: rgba(102, 126, 234, 0.08);
}

.reasoning-content:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}

.reasoning-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.reasoning-preview {
  font-size: 0.85rem;
  opacity: 0.7;
  font-weight: 500;
  margin-left: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.reasoning-toggle {
  display: flex;
  align-items: center;
}

.toggle-icon {
  transition: all 0.3s ease;
  color: #667eea;
}

.toggle-icon:hover {
  transform: scale(1.2);
}

.reasoning-text {
  padding: 16px;
  background: white;
  line-height: 1.6;
  font-weight: 500;
  color: #4a5568;
}

.message-text {
  line-height: 1.7;
  font-weight: 500;
  color: #2d3748;
}

.message.user .message-text {
  color: white;
}

.message-time {
  font-size: 0.8rem;
  color: #a0aec0;
  margin-top: 12px;
  font-weight: 500;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.streaming-cursor {
  animation: blink 1s infinite;
  color: #667eea;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

:deep(.scroll-to-bottom-btn) {
  position: fixed !important;
  border-radius: 50%;
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  box-shadow: 
    0 10px 30px rgba(99, 102, 241, 0.3),
    0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

:deep(.scroll-to-bottom-btn:hover) {
  transform: translateY(-3px) scale(1.1);
  box-shadow: 
    0 15px 40px rgba(99, 102, 241, 0.4),
    0 8px 25px rgba(0, 0, 0, 0.15);
}

:deep(.scroll-to-bottom-btn:active) {
  transform: translateY(-1px) scale(1.05);
}

.new-content-indicator {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 12px;
  height: 12px;
  background: #ff4d4f;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

/* 输入区域样式 */
.input-area {
  padding: 16px 32px 1px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  background: linear-gradient(135deg, #fafbfc 0%, #f8fafc 100%);
  position: relative;
}

.input-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.input-container {
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 12px 60px 12px 16px;
  box-shadow: 
    0 8px 30px rgba(0, 0, 0, 0.08),
    0 4px 15px rgba(0, 0, 0, 0.04);
  border: 2px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrapper:focus-within {
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 
    0 12px 40px rgba(99, 102, 241, 0.15),
    0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

:deep(.message-input) {
  flex: 1;
  border: none;
  box-shadow: none;
}

:deep(.message-input .ant-input) {
  border: none;
  border-radius: 0;
  padding: 0;
  font-size: 16px;
  line-height: 1.5;
  background: transparent;
  resize: none;
}

:deep(.message-input .ant-input:focus) {
  border: none;
  box-shadow: none;
  outline: none;
}

:deep(.message-input .ant-input::placeholder) {
  color: #94a3b8;
  font-weight: 500;
}

:deep(.send-btn) {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  box-shadow: 
    0 6px 20px rgba(99, 102, 241, 0.35),
    0 3px 10px rgba(139, 92, 246, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

:deep(.send-btn::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s;
}

:deep(.send-btn:hover::before) {
  left: 100%;
}

:deep(.send-btn:hover:not(:disabled)) {
  transform: translateY(-3px) scale(1.1);
  box-shadow: 
    0 12px 35px rgba(99, 102, 241, 0.45),
    0 6px 18px rgba(139, 92, 246, 0.35);
}

:deep(.send-btn:active) {
  transform: translateY(-1px) scale(1.05);
}

:deep(.send-btn:disabled) {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  box-shadow: 
    0 4px 12px rgba(226, 232, 240, 0.3),
    0 2px 6px rgba(203, 213, 225, 0.2);
  cursor: not-allowed;
  opacity: 0.6;
}

:deep(.send-btn .anticon) {
  font-size: 16px;
  color: white;
}



.input-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  padding: 0 4px;
}

.hint-text {
  color: #94a3b8;
}

.model-info {
  color: #6366f1;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

/* 遮罩层样式 */
.sidebar-overlay {
  display: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 80px);
    max-height: calc(100vh - 80px);
  }
  
  .sidebar-overlay {
    display: block;
    position: fixed;
    top: 80px;
    left: 0;
    width: 100%;
    height: calc(100vh - 80px);
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
  }
  
  .overlay-visible {
    opacity: 1;
    visibility: visible;
  }
  
  .sidebar {
    position: fixed;
    left: 0;
    top: 80px;
    height: calc(100vh - 80px);
    width: 280px;
    z-index: 1000;
    transition: transform 0.3s ease;
    box-shadow: 
      6px 0 24px rgba(0, 0, 0, 0.1),
      3px 0 12px rgba(102, 126, 234, 0.08);
  }
  
  .sidebar-hidden {
    transform: translateX(-100%);
  }
  
  .chat-main {
    margin-left: 0;
    width: 100%;
  }
  
  .chat-header {
    padding: 16px 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    height: auto;
  }
  
  .mobile-sidebar-toggle {
    display: inline-flex;
  }
  
  .chat-title {
    width: 100%;
    justify-content: flex-start;
  }
  
  .chat-title h3 {
    font-size: 1.1rem;
    margin-bottom: 0;
    flex: 1;
  }
  
  .header-controls {
    width: 100%;
    justify-content: space-between;
    gap: 12px;
  }
  
  .model-selector {
    flex: 1;
  }
  
  .model-selector .ant-select {
    width: 100% !important;
    max-width: 200px;
  }
  
  .messages-container {
    padding: 16px 20px;
  }
  
  .input-wrapper {
    padding: 12px 60px 12px 12px;
    border-radius: 16px;
  }
  
  :deep(.send-btn) {
    width: 44px;
    height: 44px;
    right: 10px;
    bottom: 10px;
  }
  
  :deep(.send-btn .anticon) {
    font-size: 16px;
  }
  
  .message-content {
    max-width: 85%;
    padding: 12px 16px;
  }
  
  .conversation-item {
    padding: 12px;
  }
  
  .sidebar-header {
    padding: 16px;
  }
  
  :deep(.new-chat-btn) {
    height: 48px;
    border-radius: 14px;
  }
  
  :deep(.new-chat-btn .btn-text) {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .chat-container {
    height: calc(100vh - 100px);
    max-height: calc(100vh - 100px);
  }
  
  .sidebar {
    width: 260px;
    border-right: 1px solid rgba(102, 126, 234, 0.15);
    box-shadow: 
      4px 0 16px rgba(0, 0, 0, 0.12),
      2px 0 8px rgba(102, 126, 234, 0.1);
  }
  
  .chat-header {
    padding: 12px 16px;
    gap: 10px;
  }
  
  .chat-title h3 {
    font-size: 1rem;
  }
  
  .header-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .model-selector .ant-select {
    width: 100% !important;
    max-width: none;
  }
  
  .model-option {
    padding: 2px 0;
  }
  
  .model-name {
    font-size: 0.9rem;
  }
  
  .model-provider {
    font-size: 0.8rem;
  }
  
  .sidebar-header {
    padding: 18px 16px;
  }
  
  .conversations-list {
    padding: 16px 12px;
  }
  
  .conversation-item {
    padding: 14px 12px;
    margin-bottom: 8px;
    border-radius: 12px;
  }
  
  .conversation-title {
    font-size: 0.95rem;
  }
  
  .conversation-meta {
    font-size: 0.78rem;
  }
  
  .chat-main {
    border-radius: 16px 0 0 0;
  }
  
  .message-content {
    max-width: 90%;
    border-radius: 12px;
  }
  
  .input-wrapper {
    padding: 10px 56px 10px 10px;
    border-radius: 14px;
  }
  
  :deep(.send-btn) {
    width: 40px;
    height: 40px;
    right: 8px;
    bottom: 8px;
  }
  
  :deep(.send-btn .anticon) {
    font-size: 14px;
  }
}
</style>