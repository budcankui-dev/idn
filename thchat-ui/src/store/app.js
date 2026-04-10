/**
 * @fileoverview Vuex应用状态管理模块
 * 该模块管理整个应用的核心状态，包括：
 * - 活动会话状态 (委托给 chat 模块)
 * - 标签页管理
 * - 知识库存储
 */
import indexDBUtil from '@/util/indexdb'
import { Tab } from '@/schema/tab'
import { Kb } from '@/schema/kb'

/**
 * Store存放整个Vue项目的状态数据 全局公用
 * chat 相关数据已迁移到 chat 模块 (MySQL)
 * */
const app = {
    state: {
        // 数据加载状态 (由 chat 模块控制)
        ready: false,
        // 所有标签页
        tab: new Tab({list: []}),
        // 所有的上传文件
        kb: new Kb({list: []})
    },

    mutations: {
        SET_TAB: (state, ins) => {
            state.tab = ins instanceof Tab ? ins : new Tab(ins);
            indexDBUtil.set('tabStorage', 'value', state.tab)
        },
        SET_KB: (state, kb) => {
            state.kb = kb instanceof Kb ? kb : new Kb(kb)
            indexDBUtil.set('kbStorage', 'value', state.kb)
        },
        SET_READY: (state, ready) => {
            state.ready = ready
        }
    },

    actions: {
        async initializeState({commit, dispatch}) {
            try {
                const tabData = await indexDBUtil.get('tabStorage', 'value') || {list: []}
                const kbData = await indexDBUtil.get('kbStorage', 'value') || {list: []}

                commit('SET_TAB', tabData)
                commit('SET_KB', kbData)

                // 初始化 chat 模块 (从 MySQL 加载)
                await dispatch('initChatFromServer', null, { root: true })

                commit('SET_READY', true)
            } catch (error) {
                console.error('初始化状态失败:', error)
            }
        },
        setTab({commit}, ins) {
            commit('SET_TAB', ins)
        },
        setKb({commit}, kb) {
            commit('SET_KB', kb)
        },
        clearAll({commit}) {
            const tabData = {list: []}
            const kbData = {list: []}

            commit('SET_TAB', tabData)
            commit('SET_KB', kbData)
        }
    },

    getters: {
        tab: state => state.tab,
        kb: state => state.kb,
        ready: state => state.ready
    }
}

export default app
