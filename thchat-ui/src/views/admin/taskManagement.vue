<template>
    <div class="task-management">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>任务管理</span>
                </div>
            </template>

            <el-table :data="tasks" v-loading="loading" stripe>
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="session_id" label="会话ID" width="200" show-overflow-tooltip />
                <el-table-column prop="username" label="用户" width="120" />
                <el-table-column prop="business" label="业务类型" width="120" />
                <el-table-column prop="created_at" label="创建时间" width="180">
                    <template #default="{ row }">
                        {{ formatTime(row.created_at) }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                        <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
    </div>
</template>

<script>
import { adminGetAllTasks, adminDeleteTask } from '@/api/task'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
    name: 'TaskManagement',
    data() {
        return {
            tasks: [],
            loading: false,
            total: 0,
            pageSize: 20,
            currentPage: 1
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
                this.tasks = await adminGetAllTasks(skip, this.pageSize)
                this.total = this.tasks.length // 简化，实际应该从API获取总数
            } catch (error) {
                ElMessage.error(error.message || '获取任务列表失败')
            } finally {
                this.loading = false
            }
        },
        async handleDelete(task) {
            try {
                await ElMessageBox.confirm(`确定删除任务 #${task.id}？`, '警告', {
                    type: 'warning'
                })
                await adminDeleteTask(task.id)
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
</style>
