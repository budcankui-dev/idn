<template>
    <div class="login-container">
        <el-card class="login-card">
            <template #header>
                <div class="card-header">
                    <span>智算业务助手 - 登录</span>
                </div>
            </template>
            <el-form :model="loginForm" :rules="rules" ref="formRef" label-width="80px">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="loginForm.username" placeholder="请输入用户名" @keyup.enter="handleLogin" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">
                        登录
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-button text @click="goToRegister" style="width: 100%">
                        没有账号？去注册
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script>
import { login } from '@/api/auth'
import { ElMessage } from 'element-plus'

export default {
    name: 'LoginView',
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            rules: {
                username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
                password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
            },
            loading: false
        }
    },
    methods: {
        async handleLogin() {
            // 简单检查
            if (!this.loginForm.username || !this.loginForm.password) {
                ElMessage.error('请输入用户名和密码')
                return
            }

            this.loading = true
            try {
                const username = String(this.loginForm.username)
                const password = String(this.loginForm.password)
                console.log('Login request:', { username, password })
                const data = await login(username, password)
                console.log('Login response:', data)
                // 直接操作 localStorage 和 state
                localStorage.setItem('access_token', data.access_token)
                localStorage.setItem('user_info', JSON.stringify({
                    user_id: data.user_id,
                    username: data.username,
                    role: data.role
                }))
                // 更新 Vuex state
                this.$store.state.user.token = data.access_token
                this.$store.state.user.userInfo = {
                    user_id: data.user_id,
                    username: data.username,
                    role: data.role
                }
                ElMessage.success('登录成功')
                // 重新加载聊天历史
                await this.$store.dispatch('initChatFromServer', null, { root: true })
                window.location.hash = '#/'
            } catch (error) {
                console.error('Login error:', error)
                ElMessage.error(error.message || '登录失败')
            } finally {
                this.loading = false
            }
        },
        goToRegister() {
            window.location.hash = '#/register'
        }
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
    width: 400px;
}
.card-header {
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}
</style>
