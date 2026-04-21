<template>
    <div class="task-management">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>{{ isAdmin ? '任务管理' : '我的任务' }}</span>
                </div>
            </template>

            <el-table :data="tasks" v-loading="loading" stripe>
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="session_id" label="会话ID" width="200" show-overflow-tooltip />
                <el-table-column prop="username" label="用户" width="120" v-if="isAdmin" />
                <el-table-column prop="business" label="任务名称" width="140">
                    <template #default="{ row }">
                        <el-tag type="success" size="small">{{ row.business }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="modality" label="模态" width="140">
                    <template #default="{ row }">
                        {{ row.params?.["参数"]?.["模态"] || '-' }}
                    </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180">
                    <template #default="{ row }">
                        {{ formatTime(row.created_at) }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" min-width="150" fixed="right">
                    <template #default="{ row }">
                        <el-space>
                            <el-button type="primary" size="small" @click="showDetail(row)">详情</el-button>
                            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
                        </el-space>
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

        <!-- 任务详情弹窗 -->
        <el-dialog v-model="detailVisible" title="任务详情" width="700px">
            <el-descriptions :column="2" border v-if="currentTask">
                <el-descriptions-item label="任务ID">{{ currentTask.id }}</el-descriptions-item>
                <el-descriptions-item label="会话ID">{{ currentTask.session_id }}</el-descriptions-item>
                <el-descriptions-item label="任务名称">
                    <el-tag type="success">{{ currentTask.business }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="模态">
                    <el-tag type="warning">{{ currentTask.params?.["参数"]?.["模态"] || '-' }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="用户" v-if="isAdmin">{{ currentTask.username }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ formatTime(currentTask.created_at) }}</el-descriptions-item>
            </el-descriptions>

            <el-divider>业务参数</el-divider>
            <el-table :data="taskParamsList" size="small" border v-if="taskParamsList.length > 0">
                <el-table-column prop="name" label="参数" width="140" />
                <el-table-column prop="value" label="值" />
            </el-table>
            <span v-else class="empty-text">暂无业务参数</span>

            <el-divider>原始数据</el-divider>
            <el-input type="textarea" :rows="8" v-model="taskJson" readonly class="json-viewer" />
        </el-dialog>
    </div>
</template>

<script>
import { getTasks, deleteTask } from '@/api/task'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
    name: 'TaskManagement',
    data() {
        return {
            tasks: [],
            loading: false,
            total: 0,
            pageSize: 20,
            currentPage: 1,
            detailVisible: false,
            currentTask: null
        }
    },
    computed: {
        isAdmin() {
            const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
            return userInfo.role === 'admin'
        },
        taskParamsList() {
            if (!this.currentTask) return []
            const params = this.currentTask?.params?.["参数"] || {}
            return Object.entries(params).map(([name, value]) => ({ name, value: value ?? '-' }))
        },
        taskJson() {
            if (!this.currentTask) return '{}'
            return JSON.stringify({
                business: this.currentTask.business,
                params: this.currentTask.params,
                state: this.currentTask.state,
                dag: this.currentTask.dag
            }, null, 2)
        }
    },
    mounted() {
        this.fetchTasks()
    },
    methods: {
        async fetchTasks() {
            this.loading = true
            try {
                const skip = (this.currentPage - 1) * this.pageSize
                this.tasks = await getTasks(skip, this.pageSize)
                this.total = this.tasks.length
            } catch (error) {
                ElMessage.error(error.message || '获取任务列表失败')
            } finally {
                this.loading = false
            }
        },
        showDetail(task) {
            this.currentTask = task
            this.detailVisible = true
        },
        async handleDelete(task) {
            try {
                await ElMessageBox.confirm(`确定删除任务 #${task.id}？`, '警告', {
                    type: 'warning'
                })
                await deleteTask(task.id)
                ElMessage.success('任务已删除')
                this.fetchTasks()
            } catch (error) {
                if (error !== 'cancel') {
                    ElMessage.error(error.message || '删除失败')
                }
            }
        },
        handlePageChange(page) {
            this.currentPage = page
            this.fetchTasks()
        },
        formatTime(time) {
            if (!time) return '-'
            const date = new Date(time)
            return date.toLocaleString()
        }
    }
}
</script>

<style scoped>
.task-management {
    padding: 20px;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.empty-text {
    color: #999;
    text-align: center;
    display: block;
    padding: 20px;
}
.json-viewer {
    font-family: monospace;
    font-size: 12px;
}
</style>
