import {createRouter, createWebHashHistory} from 'vue-router'


/* Layout */
import Layout from '@/layout'

const routes = [
    {
        path: '/',
        name: 'index',
        component: Layout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '', // 默认子路由
                name: 'index',
                component: () => import('@/views/AppMain.vue')
            }
        ]
    },
    {
        path: '/docs',
        name: 'docs',
        component: Layout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '', // 默认子路由
                name: 'docs',
                component: () => import('@/views/docs/index.vue')
            }
        ]
    },
    {
        path: '/kb',
        name: 'kb',
        component: Layout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '', // 默认子路由
                name: 'kb',
                component: () => import('@/views/kb/index.vue')
            }
        ]
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/login/index.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('@/views/login/register.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/admin',
        name: 'admin',
        component: Layout,
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
            {
                path: 'users',
                name: 'userManagement',
                component: () => import('@/views/admin/userManagement.vue')
            },
            {
                path: 'tasks',
                name: 'taskManagement',
                component: () => import('@/views/admin/taskManagement.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.meta.requiresAdmin && userInfo.role !== 'admin') {
        next('/')
    } else {
        next()
    }
})

export default router
