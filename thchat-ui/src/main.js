import { createApp } from 'vue'

/* 导入ElementUIPlus */
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/display.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElNotification, ElImageViewer } from 'element-plus';

/* 导入功能性组件或方法 */
import App from './App.vue'
import router from './router'
import store from './store'
import plugins from './plugins' // 引入第三方的插件或组件
import components from "@/components"  // 引入自定义的组件
import '@/assets/styles/index.scss' // 全局css


const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

// 全局方法挂载
app.config.globalProperties.$notify = ElNotification;
app.config.globalProperties.$imageViewer = ElImageViewer;

// Pending: 添加全局标志用于控制 alert 只触发一次
app.config.globalProperties.$hasAlerted = false;


app.use(plugins)
    .use(components)
    .use(ElementPlus, { size: 'default', zIndex: 3000 })
    .use(store)
    .use(router)
    .mount('#app')

// 初始化app数据
store.dispatch('initializeState').then(async () => {
    console.log('应用IndexedDB数据库初始化成功')

    // 验证token有效性
    const token = localStorage.getItem('access_token')
    if (token) {
        try {
            const response = await fetch('/local/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (response.ok) {
                const userInfo = await response.json()
                // 直接设置 state
                store.state.user.token = token
                store.state.user.userInfo = {
                    user_id: userInfo.id,
                    username: userInfo.username,
                    role: userInfo.role
                }
            } else {
                // token无效，清除
                store.state.user.token = ''
                store.state.user.userInfo = {}
                localStorage.removeItem('access_token')
                localStorage.removeItem('user_info')
            }
        } catch (e) {
            console.error('验证token失败:', e)
        }
    }
}).catch(error => {
    console.error('应用IndexedDB数据库初始化失败:', error)
})