<template>
  <div id="app">
    <a-layout class="app-container">
      <!-- 顶部导航栏 -->
      <a-layout-header class="app-header">
        <div class="header-content">
          <div class="logo logo-responsive gradient-text" @click="$router.push('/')">
            <CommentOutlined class="logo-icon responsive-icon" />
            <span class="logo-text">ChatHub</span>
          </div>
          
          <!-- 桌面端导航菜单 -->
          <a-menu
            v-model:selectedKeys="selectedKeys"
            class="nav-menu desktop-menu"
            mode="horizontal"
            @click="handleMenuClick"
          >
            <a-menu-item key="/">首页</a-menu-item>
            <a-menu-item v-if="isLoggedIn" key="/chat">聊天</a-menu-item>
            <a-menu-item key="/pricing">价格</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/dashboard">控制台</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/providers">模型平台</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/api-keys">API密钥</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/models">大模型管理</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/users">用户管理</a-menu-item>
          </a-menu>
          
          <!-- 移动端汉堡菜单按钮 -->
          <a-button 
            class="mobile-menu-btn"
            type="text"
            @click="toggleMobileMenu"
          >
            <MenuOutlined v-if="!mobileMenuOpen" />
            <CloseOutlined v-if="mobileMenuOpen" />
          </a-button>
          
          <div class="header-actions">
            <template v-if="isLoggedIn">
              <span class="username">{{ username }}</span>
              <a-button @click="logout" type="primary" ghost size="small">退出</a-button>
            </template>
            <template v-else>
              <a-button @click="$router.push('/register')" type="primary" ghost size="small" class="hidden-mobile">注册</a-button>
              <a-button @click="$router.push('/login')" type="primary" size="small">登录</a-button>
            </template>
          </div>
        </div>
        
        <!-- 移动端下拉菜单 -->
        <div class="mobile-menu" :class="{ 'mobile-menu-open': mobileMenuOpen }">
          <a-menu
            v-model:selectedKeys="selectedKeys"
            class="mobile-nav-menu"
            mode="vertical"
            @click="handleMobileMenuClick"
          >
            <a-menu-item key="/">首页</a-menu-item>
            <a-menu-item v-if="isLoggedIn" key="/chat">聊天</a-menu-item>
            <a-menu-item key="/pricing">价格</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/dashboard">控制台</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/providers">模型平台</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/api-keys">API密钥</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/models">大模型管理</a-menu-item>
            <a-menu-item v-if="isLoggedIn && userRole === 'admin'" key="/users">用户管理</a-menu-item>
            <a-menu-divider v-if="!isLoggedIn" />
            <a-menu-item v-if="!isLoggedIn" key="/register" class="mobile-only">注册</a-menu-item>
          </a-menu>
        </div>
      </a-layout-header>
      
      <!-- 主要内容区域 -->
      <a-layout-content class="app-main">
        <router-view />
      </a-layout-content>
      

    </a-layout>
  </div>
</template>

<script>
import { CommentOutlined, MenuOutlined, CloseOutlined } from '@ant-design/icons-vue'

export default {
  name: 'App',
  components: {
    CommentOutlined,
    MenuOutlined,
    CloseOutlined
  },
  data() {
    return {
      isLoggedIn: false,
      username: '',
      userRole: '',
      selectedKeys: [this.$route.path],
      mobileMenuOpen: false
    }
  },
  watch: {
    '$route'(to) {
      this.selectedKeys = [to.path]
    }
  },
  mounted() {
     this.checkLoginStatus()
     this.selectedKeys = [this.$route.path]
     // 监听路由变化，更新登录状态
     this.$router.afterEach(() => {
       this.checkLoginStatus()
     })
   },
   methods: {
     handleMenuClick({ key }) {
       this.$router.push(key)
     },
     toggleMobileMenu() {
       this.mobileMenuOpen = !this.mobileMenuOpen
     },
     handleMobileMenuClick({ key }) {
       this.$router.push(key)
       this.mobileMenuOpen = false // 点击菜单项后关闭移动端菜单
     },
     checkLoginStatus() {
      const token = localStorage.getItem('token')
      const username = localStorage.getItem('username')
      
      if (token && username) {
        // 验证token是否过期
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          if (payload.exp > Date.now() / 1000) {
            this.isLoggedIn = true
            this.username = username
            this.userRole = payload.role || 'user'
          } else {
            // token过期，清除登录信息
            this.clearLoginInfo()
          }
        } catch (error) {
          // token格式错误，清除登录信息
          this.clearLoginInfo()
        }
      } else {
        this.isLoggedIn = false
        this.username = ''
        this.userRole = ''
      }
    },
    clearLoginInfo() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_info')
      this.isLoggedIn = false
      this.username = ''
      this.userRole = ''
    },
    logout() {
      this.clearLoginInfo()
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 64px;
  display: block !important;
  visibility: visible !important;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex !important;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
  min-height: 64px;
  visibility: visible !important;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  margin-right: 12px;
  font-size: 28px;
  color: #667eea;
  transition: all 0.3s ease;
}

.logo:hover .logo-icon {
  transform: rotate(360deg);
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
  border-bottom: none;
  background: transparent;
}

:deep(.ant-menu-horizontal) {
  border-bottom: none;
  background: transparent;
}

:deep(.ant-menu-item) {
  border-radius: 8px;
  margin: 0 4px;
  transition: all 0.3s ease;
  font-weight: 500;
}

:deep(.ant-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

:deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
}

:deep(.ant-menu-item-selected::after) {
  display: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 20px;
}

.app-main {
  min-height: calc(100vh - 64px);
  padding: 0;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}

/* 全局按钮样式增强 */
:deep(.ant-btn-primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.ant-btn-primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.ant-btn-primary.ant-btn-background-ghost) {
  background: transparent;
  border: 2px solid #667eea;
  color: #667eea;
  box-shadow: none;
}

:deep(.ant-btn-primary.ant-btn-background-ghost:hover) {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 移动端汉堡菜单按钮 */
.mobile-menu-btn {
  display: none;
  font-size: 18px;
  color: #667eea;
  border: none;
  background: transparent;
  transition: all 0.3s ease;
  align-items: center;
  justify-content: center;
}

.mobile-menu-btn:hover {
  color: #764ba2;
  background: rgba(102, 126, 234, 0.1);
}

/* 移动端下拉菜单 */
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  z-index: 999;
}

.mobile-menu-open {
  max-height: 400px;
}

.mobile-nav-menu {
  border: none;
  background: transparent;
  padding: 8px 0;
}

:deep(.mobile-nav-menu .ant-menu-item) {
  margin: 2px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.mobile-nav-menu .ant-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

:deep(.mobile-nav-menu .ant-menu-item-selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
}

/* 响应式工具类 */
.hidden-mobile {
  display: inline-block;
}

.mobile-only {
  display: none;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .desktop-menu {
    display: none;
  }
  
  .mobile-menu-btn {
    display: inline-flex;
  }
  
  .header-actions .username {
    display: none;
  }
}

@media (min-width: 1025px) {
  .desktop-menu {
    display: flex !important;
  }
  
  .mobile-menu-btn {
    display: none !important;
  }
  
  .mobile-menu {
    display: none !important;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    position: relative;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .logo-icon {
    font-size: 24px;
    margin-right: 8px;
  }
  
  .header-actions {
    gap: 8px;
  }
  
  .header-actions .ant-btn {
    font-size: 12px;
    padding: 4px 12px;
  }
  
  .hidden-mobile {
    display: none;
  }
  
  .mobile-only {
    display: block;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 12px 16px;
  }
  
  .logo {
    font-size: 18px;
  }
  
  .logo-icon {
    font-size: 20px;
    margin-right: 6px;
  }
  
  .header-actions {
    gap: 6px;
  }
  
  .header-actions .ant-btn {
    font-size: 11px;
    padding: 3px 8px;
  }
}
</style>