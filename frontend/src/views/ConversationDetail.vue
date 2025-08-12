<template>
  <div class="conversation-detail">
    <div class="header">
      <div class="header-inner">
        <a-button type="text" class="back-btn" @click="goBack">
          <template #icon><LeftOutlined /></template>
          返回
        </a-button>
        <div class="title-block">
          <h1 class="title">{{ conversation?.title || '对话详情' }}</h1>
          <div class="meta" v-if="conversation">
            <a-tag color="blue">{{ conversation.model || '未知模型' }}</a-tag>
            <span class="divider">•</span>
            <span>创建：{{ formatTime(conversation.created_at) }}</span>
            <span class="divider">•</span>
            <span>更新：{{ formatTime(conversation.updated_at) }}</span>
          </div>
        </div>
        <div class="actions">
          <a-button @click="refresh" :loading="loading" type="default">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <div class="content">
      <a-spin :spinning="loading">
        <div v-if="!conversation && !loading" class="empty">
          <CommentOutlined class="empty-icon" />
          <h3>未找到该对话</h3>
          <p>请返回并从列表中选择一个有效的对话</p>
        </div>

        <div v-else class="messages-wrapper">
          <div class="messages" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message"
              :class="msg.role"
            >
              <div class="avatar">
                <span v-if="msg.role==='user'">🧑</span>
                <span v-else>🤖</span>
              </div>
              <div class="bubble">
                <div class="role">{{ msg.role === 'user' ? '我' : '助手' }}</div>
                
                <!-- 推理过程在结果前面显示 -->
                <div v-if="msg.reasoning && msg.reasoning.trim()" class="reasoning-content">
                  <div class="reasoning-header" @click="toggleReasoning(msg)">
                    <div class="reasoning-header-left">
                      <BulbOutlined />
                      <span>推理过程</span>
                      <span v-if="msg.reasoningCollapsed" class="reasoning-preview">
                        ({{ msg.reasoning.length > 50 ? msg.reasoning.substring(0, 50) + '...' : msg.reasoning }})
                      </span>
                    </div>
                    <div class="reasoning-toggle">
                      <RightOutlined v-if="msg.reasoningCollapsed" class="toggle-icon" />
                      <DownOutlined v-else class="toggle-icon" />
                    </div>
                  </div>
                  <div 
                    v-show="!msg.reasoningCollapsed" 
                    class="reasoning-text"
                  >
                    <MarkdownRenderer :content="msg.reasoning" />
                  </div>
                </div>
                
                <!-- 结果内容使用 Markdown 渲染 -->
                <div class="content-text">
                  <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
                  <span v-else>{{ msg.content }}</span>
                </div>
                
                <div class="time">{{ formatTime(msg.timestamp) }}</div>
              </div>
            </div>
          </div>
          <!-- 上滑至顶部按钮 -->
          <a-button
            v-show="showScrollTop"
            class="scroll-top-btn"
            shape="circle"
            size="large"
            type="primary"
            @click="scrollToTop"
          >
            <template #icon><UpOutlined /></template>
          </a-button>
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script>
import request from '../utils/request'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import {
  LeftOutlined,
  ReloadOutlined,
  CommentOutlined,
  BulbOutlined,
  RightOutlined,
  DownOutlined,
  UpOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'ConversationDetail',
  components: { LeftOutlined, ReloadOutlined, CommentOutlined, MarkdownRenderer, BulbOutlined, RightOutlined, DownOutlined, UpOutlined },
  data() {
    return {
      loading: false,
      conversationId: this.$route.params.id,
      conversation: null,
      messages: [],
      showScrollTop: false
    }
  },
  async mounted() {
    await this.loadData()
    this.$nextTick(() => {
      const el = this.$refs.messagesContainer
      if (el) {
        el.addEventListener('scroll', this.handleScroll, { passive: true })
        this.handleScroll()
      }
    })
  },
  beforeUnmount() {
    const el = this.$refs.messagesContainer
    if (el) el.removeEventListener('scroll', this.handleScroll)
  },
  watch: {
    '$route.params.id': {
      immediate: false,
      async handler(newId) {
        this.conversationId = newId
        await this.loadData()
      }
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        await Promise.all([this.loadConversationMeta(), this.loadMessages()])
        this.$nextTick(() => this.scrollToBottom())
      } catch (e) {
        console.error(e)
        message.error('加载对话详情失败')
      } finally {
        this.loading = false
      }
    },
    async loadConversationMeta() {
      try {
        // 后端暂无获取单个对话详情的GET接口，这里先获取列表后筛选
        const res = await request.get('/api/conversations')
        const list = res.data || []
        this.conversation = list.find(c => c.conversation_id === this.conversationId) || null
      } catch (e) {
        // 如果是403（非管理员），后端不允许拉取列表，这里保持meta为空
        this.conversation = null
      }
    },
    async loadMessages() {
      try {
        const res = await request.get(`/api/conversations/${this.conversationId}/messages`)
        this.messages = (res.data || []).map(m => ({
          role: m.role,
          content: m.content,
          reasoning: m.reasoning,
          reasoningCollapsed: m.reasoning && m.reasoning.trim() ? true : false,
          timestamp: m.timestamp
        }))
      } catch (e) {
        this.messages = []
      }
    },
    refresh() {
      this.loadData()
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push('/dashboard')
      }
    },
    scrollToBottom() {
      const el = this.$refs.messagesContainer
      if (el) el.scrollTop = el.scrollHeight
    },
    scrollToTop() {
      const el = this.$refs.messagesContainer
      if (!el) return
      if (el.scrollTo) {
        el.scrollTo({ top: 0, behavior: 'smooth' })
      } else {
        el.scrollTop = 0
      }
    },
    handleScroll() {
      const el = this.$refs.messagesContainer
      if (!el) {
        this.showScrollTop = false
        return
      }
      this.showScrollTop = el.scrollTop > 240
    },
    toggleReasoning(msg) {
      if (!msg) return
      msg.reasoningCollapsed = !msg.reasoningCollapsed
    },
    formatTime(t) {
      if (!t) return 'N/A'
      const time = dayjs(t)
      const now = dayjs()
      if (time.isSame(now, 'day')) return time.format('HH:mm')
      if (time.isSame(now.subtract(1, 'day'), 'day')) return '昨天 ' + time.format('HH:mm')
      if (time.isSame(now, 'year')) return time.format('MM-DD HH:mm')
      return time.format('YYYY-MM-DD HH:mm')
    }
  }
}
</script>

<style scoped>
.conversation-detail {
  min-height: 100vh;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0,0,0,0.06);
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}
.back-btn {
  margin-right: 8px;
}
.title-block {
  flex: 1;
  padding: 0 12px;
}
.title {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #2d3748;
}
.meta {
  margin-top: 4px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 8px;
}
.divider { color: #cbd5e0; }
.actions { display: flex; gap: 8px; }

.content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}
.messages-wrapper {
  background: rgba(255,255,255,0.95);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  position: relative;
}
.messages {
  padding: 16px;
  overflow-y: auto;
}
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.message.user .bubble { background: #ebf8ff; border-color: #bee3f8; }
.message.assistant .bubble { background: #f7fafc; border-color: #e2e8f0; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #edf2f7; color: #4a5568; font-size: 18px;
}
.bubble {
  flex: 1; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 14px;
}
.role { font-weight: 600; color: #4a5568; margin-bottom: 6px; }
.content-text { color: #2d3748; line-height: 1.6; word-break: break-word; }
.time { margin-top: 8px; font-size: 12px; color: #a0aec0; }
.reasoning { margin-top: 8px; }
.reasoning-text { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; color: #4a5568; }

.empty { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 48px; color: #cbd5e0; margin-bottom: 8px; }

@media (max-width: 768px) {
  .messages-wrapper { height: calc(100vh - 180px); }
}

/* 新增的推理折叠头部样式，复用 Chat.vue 的视觉风格 */
.reasoning-content {
  background: rgba(118, 75, 162, 0.04);
  border: 1px dashed rgba(118, 75, 162, 0.25);
  border-radius: 10px;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.reasoning-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}
.reasoning-header-left {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #6b46c1;
  font-weight: 600;
}
.reasoning-preview { color: #805ad5; font-weight: 400; margin-left: 8px; font-size: 12px; }
.toggle-icon { color: #6b46c1; }

/* 回到顶部按钮样式 */
.scroll-top-btn {
  position: absolute;
  right: 8px;
  bottom: 16px;
  z-index: 5;
  box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
</style>