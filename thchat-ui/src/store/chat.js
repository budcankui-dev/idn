/**
 * 聊天状态管理 - 基于 MySQL API
 */

import * as chatApi from '@/api/chat'

// QA 类
class QA {
    constructor(data = {}) {
        this.qaId = data.qa_id || data.qaId || ''
        this.query = data.query || ''
        this.answer = data.answer || ''
        this.files = data.files || []
        this.responseTime = data.response_time || data.responseTime || 0
        this.finishTime = data.finish_time || data.finishTime || null
        this.series = data.series || ''
        this.modelName = data.model_name || data.modelName || ''
        this.modelType = data.model_type || data.modelType || ''
        this.recall = data.recall || []
        this.reason = data.reason || ''
    }
}

// Session 类
class Session {
    constructor(data = {}) {
        this.sessionId = data.session_id || data.sessionId || ''
        this.title = data.title || ''
        this.state = data.state || {}
        this.data = (data.data || []).map(qa => qa instanceof QA ? qa : new QA(qa))
        this.createdAt = data.created_at || data.createdAt
        this.updatedAt = data.updated_at || data.updatedAt
    }
}

// Chat 类
class Chat {
    constructor(data = {}) {
        let list = []
        if (data.list && Array.isArray(data.list)) {
            list = data.list
        }
        this.list = list.map(s => s instanceof Session ? s : new Session(s))
    }
}

const chat = {
    // 非 namespace 模块，直接挂载到 root state

    state: {
        ready: false,
        active: '',
        sessionState: {},
        tab: { list: [] },
        chat: new Chat({ list: [] })
    },

    mutations: {
        SET_READY: (state, ready) => {
            state.ready = ready
        },
        SET_ACTIVE: (state, active) => {
            state.active = active
        },
        SET_SESSION_STATE: (state, { sessionId, sessionState }) => {
            const session = state.chat.list.find(s => s.sessionId === sessionId)
            if (session) {
                session.state = sessionState
            }
        },
        SET_TAB: (state, ins) => {
            state.tab = ins
        },
        SET_CHAT: (state, ins) => {
            state.chat = ins instanceof Chat ? ins : new Chat(ins)
            state.chat._updateTimestamp = Date.now()
        },
        ADD_SESSION: (state, session) => {
            state.chat.list.unshift(session)
            state.active = session.sessionId
        },
        UPDATE_SESSION: (state, { sessionId, updates }) => {
            const session = state.chat.list.find(s => s.sessionId === sessionId)
            if (session) {
                Object.assign(session, updates)
            }
            state.chat._updateTimestamp = Date.now()
        },
        DELETE_SESSION: (state, sessionId) => {
            state.chat.list = state.chat.list.filter(s => s.sessionId !== sessionId)
            if (state.active === sessionId) {
                state.active = state.chat.list.length > 0 ? state.chat.list[0].sessionId : ''
            }
            state.chat._updateTimestamp = Date.now()
        },
        ADD_MESSAGE: (state, { sessionId, message }) => {
            console.log('ADD_MESSAGE mutation: looking for sessionId=', sessionId);
            console.log('ADD_MESSAGE mutation: state.chat.list=', state.chat.list.map(s => s.sessionId));
            const session = state.chat.list.find(s => s.sessionId === sessionId)
            if (session) {
                console.log('ADD_MESSAGE: session found, pushing message');
                session.data.push(message instanceof QA ? message : new QA(message))
                console.log('ADD_MESSAGE: sessionId=', sessionId, 'message.qaId=', message.qaId, 'answer=', message.answer, 'data.length=', session.data.length)
            } else {
                console.log('ADD_MESSAGE: session not found, sessionId=', sessionId)
            }
            state.chat._updateTimestamp = Date.now()
        },
        UPDATE_MESSAGE_ANSWER: (state, { sessionId, qaId, answer, finishTime }) => {
            console.log('UPDATE_MESSAGE_ANSWER mutation: sessionId=', sessionId, 'qaId=', qaId, 'answer=', answer ? answer.substring(0, 50) : null);
            console.log('UPDATE_MESSAGE_ANSWER mutation: state.chat.list=', state.chat.list.map(s => s.sessionId));
            const session = state.chat.list.find(s => s.sessionId === sessionId)
            if (session) {
                console.log('UPDATE_MESSAGE_ANSWER: session found, data=', session.data.map(m => m.qaId));
                // Use string comparison to avoid type mismatch issues
                const msgIndex = session.data.findIndex(m => String(m.qaId) === String(qaId))
                if (msgIndex !== -1) {
                    // Create a new array to ensure Vue detects the change
                    const newData = [...session.data]
                    newData[msgIndex] = { ...newData[msgIndex], answer: answer, finishTime: finishTime !== undefined ? finishTime : newData[msgIndex].finishTime }
                    session.data = newData
                    console.log('UPDATE_MESSAGE_ANSWER: msg found, new answer length=', answer ? answer.length : 0)
                } else {
                    console.log('UPDATE_MESSAGE_ANSWER: msg not found, qaId=', qaId, 'available qaIds=', session.data.map(m => m.qaId))
                }
            } else {
                console.log('UPDATE_MESSAGE_ANSWER: session not found')
            }
            state.chat._updateTimestamp = Date.now()
        }
    },

    actions: {
        async initChatFromServer({ commit }) {
            try {
                commit('SET_READY', false)

                // 从 API 加载聊天历史
                const histories = await chatApi.getChatHistories()

                // 转换为 Session 对象，同时获取 session state
                const sessions = await Promise.all(
                    histories.map(async (h) => {
                        const messages = await chatApi.getChatMessages(h.session_id)
                        // 从 task 表获取 session state（包含 intent_result 和 dag）
                        let sessionState = {}
                        try {
                            const taskData = await chatApi.getTasksBySession(h.session_id)
                            if (taskData && taskData.state) {
                                sessionState = taskData.state
                            }
                        } catch (e) {
                            // task 不存在，保持空 state
                        }

                        return new Session({
                            session_id: h.session_id,
                            title: h.title,
                            created_at: h.created_at,
                            updated_at: h.updated_at,
                            data: messages,
                            state: sessionState
                        })
                    })
                )

                commit('SET_CHAT', new Chat({ list: sessions }))
                commit('SET_ACTIVE', sessions.length > 0 ? sessions[0].sessionId : '')
                commit('SET_READY', true)
            } catch (error) {
                console.error('初始化聊天状态失败:', error)
                commit('SET_READY', true)
            }
        },

        setActive({ commit }, active) {
            commit('SET_ACTIVE', active)
        },

        async createSession({ commit }, { sessionId, title }) {
            try {
                await chatApi.createChatHistory(sessionId, title)
                const session = new Session({
                    session_id: sessionId,
                    title: title,
                    data: []
                })
                commit('ADD_SESSION', session)
                return session
            } catch (error) {
                console.error('创建会话失败:', error)
                throw error
            }
        },

        async deleteSession({ commit }, sessionId) {
            try {
                await chatApi.deleteChatHistory(sessionId)
                commit('DELETE_SESSION', sessionId)
            } catch (error) {
                console.error('删除会话失败:', error)
                throw error
            }
        },

        async addMessage({ commit, state }, { sessionId, message }) {
            try {
                console.log('addMessage called: sessionId=', sessionId, 'message.qaId=', message.qaId);
                console.log('state.chat.list=', state.chat.list.map(s => s.sessionId));
                const msgData = {
                    qa_id: String(message.qaId || message.qa_id),
                    query: message.query,
                    answer: message.answer,
                    files: message.files,
                    response_time: message.responseTime || message.response_time,
                    finish_time: message.finishTime || message.finish_time,
                    series: message.series,
                    model_name: message.modelName || message.model_name,
                    model_type: message.modelType || message.model_type,
                    recall: message.recall,
                    reason: message.reason
                }
                await chatApi.createChatMessage(sessionId, msgData)
                commit('ADD_MESSAGE', { sessionId, message: new QA(msgData) })
            } catch (error) {
                console.error('添加消息失败:', error)
                throw error
            }
        },

        updateMessageAnswer({ commit }, { sessionId, qaId, answer, finishTime }) {
            commit('UPDATE_MESSAGE_ANSWER', { sessionId, qaId, answer, finishTime })
        },

        async updateMessage(_, { qaId, updates }) {
            try {
                await chatApi.updateChatMessage(qaId, updates)
            } catch (error) {
                console.error('更新消息失败:', error)
                throw error
            }
        },

        setSessionState({ commit, state }, sessionState) {
            // 只更新本地状态，不同步到后端
            // DAG 在提交时才保存到数据库
            commit('SET_SESSION_STATE', { sessionId: state.active, sessionState })
        },

        async updateSessionTitle({ commit }, { sessionId, title }) {
            try {
                // Update in backend
                await chatApi.updateChatHistory(sessionId, title)
                // Update in frontend state
                commit('UPDATE_SESSION', { sessionId, updates: { title } })
            } catch (error) {
                console.error('更新会话标题失败:', error)
                throw error
            }
        }
    },

    getters: {
        active: state => state.active,
        sessionState: state => state.sessionState,
        chatList: state => state.chat.list,
        activeSession: state => {
            return state.chat.list.find(s => s.sessionId === state.active)
        },
        activeSessionData: state => {
            const session = state.chat.list.find(s => s.sessionId === state.active)
            return session ? session.data : []
        }
    }
}

export default chat
