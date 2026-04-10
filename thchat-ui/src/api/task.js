/**
 * 任务 API 调用
 */

const API_BASE = '/local/tasks'
const ADMIN_API_BASE = '/local/admin/tasks'

async function request(url, options = {}) {
    const token = localStorage.getItem('access_token')
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(url, {
        ...options,
        headers
    })

    if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        window.location.hash = '#/login'
        throw new Error('登录已过期')
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '请求失败' }))
        throw new Error(error.detail || '请求失败')
    }

    return response.json()
}

// ============ Task (User) ============

export async function getTasks(skip = 0, limit = 100) {
    return request(API_BASE, {
        method: 'GET'
    })
}

export async function createTask(data) {
    return request(API_BASE, {
        method: 'POST',
        body: JSON.stringify(data)
    })
}

export async function getTask(taskId) {
    return request(API_BASE + '/' + taskId, {
        method: 'GET'
    })
}

export async function updateTask(taskId, data) {
    return request(API_BASE + '/' + taskId, {
        method: 'PUT',
        body: JSON.stringify(data)
    })
}

export async function deleteTask(taskId) {
    return request(API_BASE + '/' + taskId, {
        method: 'DELETE'
    })
}

// ============ Admin Task ============

export async function adminGetAllTasks(skip = 0, limit = 100, userId = null) {
    let url = ADMIN_API_BASE + '?skip=' + skip + '&limit=' + limit
    if (userId) {
        url += '&user_id=' + userId
    }
    return request(url, {
        method: 'GET'
    })
}

export async function adminDeleteTask(taskId) {
    return request(ADMIN_API_BASE + '/' + taskId, {
        method: 'DELETE'
    })
}
