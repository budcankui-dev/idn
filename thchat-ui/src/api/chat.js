/**
 * 聊天 API 调用
 */

const API_BASE = '/local/chat'

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

// ============ Chat History ============

export async function getChatHistories(skip = 0, limit = 100) {
    return request(API_BASE + '/history', {
        method: 'GET'
    })
}

export async function createChatHistory(sessionId, title = '') {
    return request(API_BASE + '/history', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, title })
    })
}

export async function deleteChatHistory(sessionId) {
    return request(API_BASE + '/history/' + sessionId, {
        method: 'DELETE'
    })
}

export async function updateChatHistory(sessionId, title) {
    return request(API_BASE + '/history/' + sessionId, {
        method: 'PUT',
        body: JSON.stringify({ title })
    })
}

// ============ Chat Messages ============

export async function getChatMessages(sessionId) {
    return request(API_BASE + '/history/' + sessionId + '/messages', {
        method: 'GET'
    })
}

export async function createChatMessage(sessionId, message) {
    return request(API_BASE + '/history/' + sessionId + '/messages', {
        method: 'POST',
        body: JSON.stringify(message)
    })
}

export async function updateChatMessage(qaId, data) {
    return request(API_BASE + '/message/' + qaId, {
        method: 'PUT',
        body: JSON.stringify(data)
    })
}
