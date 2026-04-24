/**
 * 认证 API 调用
 */

const API_BASE = '/local/auth'
const USER_API_BASE = '/local/users'

async function request(url, options = {}) {
    const token = localStorage.getItem('access_token')
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }

    console.log('request:', { url, method: options.method, headers })
    const response = await fetch(url, {
        ...options,
        headers
    })
    console.log('response status:', response.status, response.statusText)

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

export async function login(username, password) {
    console.log('login called with:', { username, password })
    const url = API_BASE + '/login'
    console.log('login url:', url)
    const token = localStorage.getItem('access_token')
    console.log('token before request:', token)
    return request(url, {
        method: 'POST',
        body: JSON.stringify({ username, password })
    })
}

export async function register(username, password, email) {
    return request(API_BASE + '/register', {
        method: 'POST',
        body: JSON.stringify({ username, password, email })
    })
}

export async function getCurrentUser() {
    return request(API_BASE + '/me', {
        method: 'GET'
    })
}

export async function logout() {
    return request(API_BASE + '/logout', {
        method: 'POST'
    })
}

// 用户管理 API
export async function listUsers(skip = 0, limit = 20) {
    return request(USER_API_BASE + '?skip=' + skip + '&limit=' + limit, {
        method: 'GET'
    })
}

export async function createUser(userData) {
    return request(USER_API_BASE, {
        method: 'POST',
        body: JSON.stringify(userData)
    })
}

export async function updateUser(userId, userData) {
    return request(`${USER_API_BASE}/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(userData)
    })
}

export async function deleteUser(userId) {
    return request(`${USER_API_BASE}/${userId}`, {
        method: 'DELETE'
    })
}
