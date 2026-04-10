/**
 * 用户状态管理
 */

const user = {
    state: {
        token: localStorage.getItem('access_token') || '',
        userInfo: JSON.parse(localStorage.getItem('user_info') || '{}')
    },

    mutations: {
        SET_TOKEN: (state, token) => {
            state.token = token
            if (token) {
                localStorage.setItem('access_token', token)
            } else {
                localStorage.removeItem('access_token')
            }
        },
        SET_USER_INFO: (state, userInfo) => {
            state.userInfo = userInfo
            if (userInfo) {
                localStorage.setItem('user_info', JSON.stringify(userInfo))
            } else {
                localStorage.removeItem('user_info')
            }
        },
        CLEAR_USER: (state) => {
            state.token = ''
            state.userInfo = {}
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_info')
        }
    },

    actions: {
        setToken({commit}, token) {
            commit('SET_TOKEN', token)
        },
        setUserInfo({commit}, userInfo) {
            commit('SET_USER_INFO', userInfo)
        },
        logout({commit}) {
            commit('CLEAR_USER')
        },
        login({dispatch}, {token, userInfo}) {
            dispatch('setToken', token)
            dispatch('setUserInfo', userInfo)
        }
    },

    getters: {
        token: state => state.token,
        userInfo: state => state.userInfo,
        isLoggedIn: state => !!state.token,
        isAdmin: state => state.userInfo?.role === 'admin',
        userId: state => state.userInfo?.user_id || state.userInfo?.id,
        username: state => state.userInfo?.username || ''
    }
}

export default user
