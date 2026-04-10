<template>
    <div class="login-container">
        <el-card class="login-card">
            <template #header>
                <div class="card-header">
                    <span>用户注册</span>
                </div>
            </template>
            <el-form :model="registerForm" :rules="rules" ref="formRef" label-width="80px">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="registerForm.username" placeholder="请输入用户名" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="registerForm.email" placeholder="请输入邮箱（可选）" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" :loading="loading" @click="handleRegister" style="width: 100%">
                        注册
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-button text @click="goToLogin" style="width: 100%">
                        已有账号？去登录
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script>
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

export default {
    name: 'RegisterView',
    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value !== this.registerForm.password) {
                callback(new Error('两次输入的密码不一致'))
            } else {
                callback()
            }
        }
        return {
            registerForm: {
                username: '',
                password: '',
                confirmPassword: '',
                email: ''
            },
            rules: {
                username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
                password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
                confirmPassword: [{ required: true, message: '请再次输入密码', trigger: 'blur' }, { validator: validateConfirmPassword, trigger: 'blur' }]
            },
            loading: false
        }
    },
    methods: {
        async handleRegister() {
            const valid = await this.$refs.formRef.validate().catch(() => false)
            if (!valid) return

            this.loading = true
            try {
                await register(
                    this.registerForm.username,
                    this.registerForm.password,
                    this.registerForm.email || undefined
                )
                ElMessage.success('注册成功，请登录')
                window.location.hash = '#/login'
            } catch (error) {
                ElMessage.error(error.message || '注册失败')
            } finally {
                this.loading = false
            }
        },
        goToLogin() {
            window.location.hash = '#/login'
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
