<template>
    <div class="user-management">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>用户管理</span>
                    <el-button type="primary" @click="showCreateDialog">创建用户</el-button>
                </div>
            </template>

            <el-table :data="users" v-loading="loading" stripe>
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="username" label="用户名" />
                <el-table-column prop="email" label="邮箱" />
                <el-table-column prop="role" label="角色" width="100">
                    <template #default="{ row }">
                        <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small">
                            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="is_active" label="状态" width="100">
                    <template #default="{ row }">
                        <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                            {{ row.is_active ? '启用' : '禁用' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                    <template #default="{ row }">
                        <el-button type="primary" size="small" @click="editUser(row)">编辑</el-button>
                        <el-button type="danger" size="small" @click="handleDelete(row)" :disabled="row.id === currentUserId">
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <el-pagination
                v-if="total > 0"
                layout="prev, pager, next"
                :total="total"
                :page-size="pageSize"
                :current-page="currentPage"
                @current-change="handlePageChange"
                style="margin-top: 20px; text-align: center;"
            />
        </el-card>

        <!-- 创建/编辑对话框 -->
        <el-dialog v-model="showDialog" :title="editingUser ? '编辑用户' : '创建用户'" width="500px">
            <el-form :model="userForm" :rules="formRules" ref="dialogFormRef" label-width="80px">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="userForm.username" :disabled="!!editingUser" placeholder="请输入用户名" />
                </el-form-item>
                <el-form-item label="密码" :prop="editingUser ? '' : 'password'">
                    <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
                    <span v-if="editingUser" style="color: #999; font-size: 12px;">留空则不修改密码</span>
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="userForm.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="角色" prop="role">
                    <el-select v-model="userForm.role" style="width: 100%">
                        <el-option label="普通用户" value="normal" />
                        <el-option label="管理员" value="admin" />
                    </el-select>
                </el-form-item>
                <el-form-item label="启用状态">
                    <el-switch v-model="userForm.is_active" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showDialog = false">取消</el-button>
                <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { listUsers, createUser, updateUser, deleteUser } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
    name: 'UserManagement',
    data() {
        return {
            users: [],
            loading: false,
            total: 0,
            pageSize: 20,
            currentPage: 1,
            showDialog: false,
            editingUser: null,
            saving: false,
            userForm: {
                username: '',
                password: '',
                email: '',
                role: 'normal',
                is_active: true
            },
            formRules: {
                username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
                password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
                role: [{ required: true, message: '请选择角色', trigger: 'change' }]
            }
        }
    },
    computed: {
        currentUserId() {
            return this.$store.state.user?.userInfo?.user_id || this.$store.state.user?.userInfo?.id
        }
    },
    mounted() {
        this.fetchUsers()
    },
    methods: {
        async fetchUsers() {
            this.loading = true
            try {
                const skip = (this.currentPage - 1) * this.pageSize
                const response = await listUsers(skip, this.pageSize)
                this.users = response.users || response
                this.total = response.total || this.users.length
            } catch (error) {
                ElMessage.error(error.message || '获取用户列表失败')
            } finally {
                this.loading = false
            }
        },
        handlePageChange(page) {
            this.currentPage = page
            this.fetchUsers()
        },
        showCreateDialog() {
            this.editingUser = null
            this.userForm = {
                username: '',
                password: '',
                email: '',
                role: 'normal',
                is_active: true
            }
            this.showDialog = true
        },
        editUser(user) {
            this.editingUser = user
            this.userForm = {
                username: user.username,
                password: '',
                email: user.email || '',
                role: user.role,
                is_active: user.is_active
            }
            this.showDialog = true
        },
        async handleSave() {
            const valid = await this.$refs.dialogFormRef.validate().catch(() => false)
            if (!valid) return

            this.saving = true
            try {
                const data = { ...this.userForm }
                if (!data.password) {
                    delete data.password
                }
                if (this.editingUser) {
                    await updateUser(this.editingUser.id, data)
                    ElMessage.success('用户已更新')
                } else {
                    await createUser(data)
                    ElMessage.success('用户已创建')
                }
                this.showDialog = false
                this.fetchUsers()
            } catch (error) {
                ElMessage.error(error.message || '保存失败')
            } finally {
                this.saving = false
            }
        },
        async handleDelete(user) {
            try {
                await ElMessageBox.confirm(`确定删除用户 ${user.username}？`, '警告', {
                    type: 'warning'
                })
                await deleteUser(user.id)
                ElMessage.success('用户已删除')
                this.fetchUsers()
            } catch (error) {
                if (error !== 'cancel') {
                    ElMessage.error(error.message || '删除失败')
                }
            }
        }
    }
}
</script>

<style scoped>
.user-management {
    padding: 20px;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
