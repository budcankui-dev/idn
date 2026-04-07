import store from '@/store'

export default {
    /**
     * 删除历史聊天 Session
     * @param {string} sessionId 要删除的会话id
     */
    delSession(sessionId) {
        let chat = store.state.app.chat;
        chat.removeSession(sessionId);
        store.dispatch('setChat', chat);
    },

    /**
     * 删除Session内的QA
     * @param {string} sessionId 会话id
     * @param {string} qaId QA的id
     */
    delQA(sessionId, qaId) {
        let chat = store.state.app.chat;
        let session = chat.findSession(sessionId);
        session.removeQA(qaId);
        store.dispatch('setChat', chat);
    },

    /**
     * 添加新的Session
     * @param {Session} session Session对象
     */
    addSession(session) {
        let chat = store.state.app.chat;
        chat.addSession(session);
        store.dispatch('setChat', chat);
    },

    /**
     * 添加新的QA
     * @param {string} sessionId 会话id
     * @param {QA} qa QA对象
     */
    addQA(sessionId, qa) {
        let chat = store.state.app.chat;
        let session = chat.findSession(sessionId);
        if (session) {
            let existingQA = session.data.find(item => item.qaId === qa.qaId);
            if (existingQA) {
                
                // 如果找到相同id的QA,替换它
                let index = session.data.indexOf(existingQA);
               
                // 创建新的数组以触发响应式更新
                session.data = [
                    ...session.data.slice(0, index),
                    qa,
                    ...session.data.slice(index + 1)
                ];
            } else {
                // 如果没找到,添加新的QA
                session.data = [...session.data, qa];
            }
            // 创建新的chat对象以触发响应式更新
            store.dispatch('setChat', Object.assign({}, chat));
        }
    },

    setSessionState(sessionId, state) {
        let chat = store.state.app.chat;
        let session = chat.findSession(sessionId);
        if (session) {
     
            // session.state=state
                // session_id: str = ""
                // type: str = "state"
                // stage: str = "intent_parsing"
                // workflow: str = "intent_parsing"
                // parse_success: bool = False
                // missing_params: list = []
                // reason_params: list = []
                // intent_result: dict = {}
                // dag: dict = {}
                // code:int =0
                // msg:str = ""
            session.state = {
            // ...state,
            session_id: String(sessionId),
             intent_result: { ...state.intent_result }, // 保证深层响应式触发
             dag: { ...state.dag },
             type: "state",
             stage: state.stage ,
             workflow: state.workflow ,
             parse_success: state.parse_success ,
             missing_params: state.missing_params ,
             reason_params: state.reason_params ,
             code: state.code ,
             msg: state.msg 
            };
            // session.state = { ...state }; 
            // session.state.session_id=String(sessionId)
             // 创建新的chat对象以触发响应式更新
            store.dispatch('setChat', Object.assign({}, chat));
            
        }
    },
    getSession(sessionId){
        let chat = store.state.app.chat;
        let session = chat.findSession(sessionId);
        return session
    }
}
