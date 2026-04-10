import { createStore } from 'vuex'
import app from './app'
import setting from './setting'
import user from './user'
import chat from './chat'

export default createStore({
  modules: {
    app,
    setting,
    user,
    chat
  }
})
