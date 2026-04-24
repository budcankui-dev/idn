<template>
    <el-container style="height: 100%;">
        <el-main style="height: 100%; padding: 0;">
            <el-row justify="center" style="height: 100%;">
                <el-col :md="18" :sm="20" :xs="24" style="padding-left: 0;padding-right: 0; ">
                    <div class="home" ref="homeRef">

                        <el-row :gutter="12" justify="center" style="margin-left: 0;margin-right: 0;">
                            <!-- <el-row :gutter="24" style="margin-left: 0;margin-right: 0;"> -->
                            <el-col :md="24" :sm="24" :xs="24">
                                <ChatCard :qaId="c['qaId']" :query="c['query']" :answer="c['answer']"
                                    :modelName="c['modelName']" :series="c['series']" :responseTime="c['responseTime']"
                                    :finishTime="c['finishTime']" :files="c['files']" :modelType="c['modelType']"
                                    :recall="c['recall']" :reason="c['reason']" v-for="c in active_session_qa_data" />

                                <div class="title-container" v-if="is_show">
                                    <div class="title-line">{{ $t('AppMain.title') }} <span>BUPT</span></div>
                                    <div class="sub-title-line">{{ $t('AppMain.welcome') }}</div>
                                    <div class="sub-title-line">例如：我想部署视频AI推理业务。
                                    </div>
                                    <!-- <div class="sub-title-line">
                                        <el-link type="primary" href="https://unagi-cq.github.io/BUPT/#/docs"
                                            @click="goTo('/about')">
                                            {{ $t('AppMain.viewDocs') }}
                                        </el-link>
                                    </div> -->
                                </div>
                            </el-col>


                        </el-row>


                        <canvas id="live2d"></canvas>
                    </div>
                </el-col>
            </el-row>
        </el-main>
        <el-aside style="width: 25%; min-width: 300px; max-width: 400px; padding: 20px 0 0 8px; border-left: 1px solid #999; overflow-x: hidden; overflow-y: auto;">
            <el-container style="display: flex; flex-direction: column; height: 100%; width: 100%; align-items: center; overflow-x: hidden;">
                <el-main style="padding: 0; display: flex; flex-direction: column; width: 100%; overflow-x: hidden; overflow-y: auto;">

                    <el-space direction="vertical" :size="30" style="max-width: 100%; width: 100%; overflow-x: hidden;">
                        <!-- 智算业务id -->
                        <!-- <div class="card"> -->
                        <el-tag type="primary" size="default" class="session-id-tag" style="padding: 6px 10px; width: 100%; box-sizing: border-box; margin-bottom: 2px;">
                            <span style="font-size: 13px;">智算业务id</span>
                        </el-tag>
                        <el-tag type="info" size="default" style="padding: 6px 10px; width: 100%; box-sizing: border-box;">
                            <span class="session-id-text" style="font-size: 12px; word-break: break-all;">{{ active ? active : "暂未开始解析" }}</span>
                        </el-tag>
                        <!-- </div> -->

                        <!-- 意图解析结果 -->
                        <div class="card" style="padding: 8px;">
                            <el-tag type="info" class="card-header">
                                意图解析结果
                                <el-tag v-if="intentBusinessType" type="success" size="small" style="margin-left: 8px;">
                                    {{ intentBusinessType }}
                                </el-tag>
                                <el-tag v-if="intentModality" type="warning" size="small" style="margin-left: 4px;">
                                    {{ intentModality }}
                                </el-tag>
                            </el-tag>

                            <div v-if="showIntentPreview && active" class="card-body" style="padding: 4px;">
                                <!-- 业务参数表格 -->
                                <el-table v-if="intentParamsList.length > 0" :data="intentParamsList" size="small" border style="width: 100%; table-layout: fixed;">
                                    <el-table-column prop="name" label="参数" />
                                    <el-table-column prop="value" label="值" />
                                </el-table>
                                <span v-else class="empty-text">暂无业务参数</span>
                                <!-- 原始JSON -->
                                <div class="json-raw">
                                    <span class="json-label">原始JSON:</span>
                                    <v-md-preview :text="sessionStateIntentText"></v-md-preview>
                                </div>
                            </div>
                        </div>

                        <!-- 任务DAG -->
                        <div class="card dag-card" style="padding: 8px; max-height: none;">
                            <el-tag type="warning" class="card-header">
                                任务DAG
                            </el-tag>
                            <div class="dag-preview-wrapper" style="max-height: none; overflow-y: visible;">
                                <v-md-preview v-if="showDagPreview && active" :key="sessionStateDagText" :text="sessionStateDagText" style="max-height: 600px; overflow-y: auto;"></v-md-preview>
                            </div>
                        </div>
                    </el-space>
                </el-main>

                <el-footer
                    style="text-align: center; width: 100%; border-top: 1px solid #999; display: flex;justify-content: center; align-items: center;">

                    <el-button
                        :style="{ width: '100px' }"
                        type="primary"
                        :disabled="!canSubmit || alreadySubmitted || isSubmitting"
                        :loading="isSubmitting"
                        @click="onClickSubmit">
                        {{ alreadySubmitted ? '已提交' : '提交' }}

                    </el-button>
                </el-footer>
            </el-container>

        </el-aside>
    </el-container>



</template>

<script>

import { nextTick, ref, computed } from 'vue'
import loadLive2d from 'live2d-helper'
import chatStoreHelper from '@/schema/chatStoreHelper'
import { MdPreview } from 'md-editor-v3';
import { createTask } from '@/api/task';
import { getTasksBySession } from '@/api/chat';
export default {
    name: 'AppMain',
    components: { MdPreview },
    data() {
        return {

            isLive2dLoading: false,
            live2dError: null,
            live2dInstance: null,  // 添加实例引用
            isSubmitted: false,  // 是否已提交
            isSubmitting: false  ,// 是否正在提交
             showIntentPreview: true,
      showDagPreview: true,

        }
    },
    computed: {
        // 当前激活的聊天记录uuid
        active() {
            return this.$store.state.chat.active || '';
        },
        // 意图解析 - 任务名称
        intentBusinessType() {
            const activeSession = this.$store.getters.activeSession;
            return activeSession?.state?.intent_result?.["任务名称"] || '';
        },
        // 意图解析 - 模态
        intentModality() {
            const activeSession = this.$store.getters.activeSession;
            return activeSession?.state?.intent_result?.["参数"]?.["模态"] || '';
        },
        // 意图解析 - 业务参数列表（用于表格展示）
        intentParamsList() {
            const activeSession = this.$store.getters.activeSession;
            const params = activeSession?.state?.intent_result?.["参数"] || {};
            return Object.entries(params).map(([name, value]) => ({ name, value: String(value) }));
        },
        // 会话状态
        sessionState() {
            const activeSession = this.$store.getters.activeSession;
            // console.log('计算属性 aactiveSession?.state 重新计算，active:', this.active, 'sessionState:', activeSession?.state);
            return activeSession ? { ...activeSession.state } : {};
            // return activeSession?toRaw(activeSession.state)  : {};
        },
        // 激活会话的QA对
        active_session_qa_data() {
            return this.$store.getters.activeSessionData || [];
        },
        // 等app数据加载之后再执行逻辑 否则会闪屏
        is_show() {
            return this.$store.state.chat.ready && this.active_session_qa_data.length === 0;
        },
        // DAG文本
        sessionStateDagText() {
            const activeSession = this.$store.getters.activeSession;
            // 优先读取 state.dag（解析成功但未提交的），其次读取 session.dag（提交后的）
            // 使用 ?? 而不是 || 避免空对象被短路
            const dag = activeSession?.state?.dag ?? activeSession?.dag ?? {};
            return `\`\`\`json\n${JSON.stringify(dag, null, 2)}\n\`\`\``
        },
        sessionStateIntentText() {
            const activeSession = this.$store.getters.activeSession;
            const intent_result = activeSession?.state?.intent_result || {};
            return `\`\`\`json\n${JSON.stringify(intent_result, null, 2)}\n\`\`\``
        },
        // 判断当前会话是否已提交过任务
        alreadySubmitted() {
            const activeSession = this.$store.getters.activeSession;
            // 通过 job_id 是否存在判断是否已提交（更可靠）
            return !!(activeSession?.dag?.job_id);
        },
        // 判断是否可以提交
        canSubmit() {
            const activeSession = this.$store.getters.activeSession;
            return activeSession?.state?.parse_success === true;
        }
    },
    watch: {
        active: {
            handler(newVal, oldVal) {
                // console.log('watch active:', newVal, oldVal);
                if (newVal && newVal !== oldVal) {
                    this.loadSessionData(newVal);
                }
            },
            immediate: true
        },
        '$store.state.chat.active': {
            handler(newVal) {
                // console.log('$store.state.chat.active watcher:', newVal);
                if (newVal) {
                    this.loadSessionData(newVal);
                }
            },
            immediate: true
        }
    },
    mounted() {
        this.initLive2d();
        this.checkInitialState();
    },
    beforeUnmount() {
        this.destroyLive2d();
    },
    methods: {
        async initLive2d() {
            if (this.isLive2dLoading) return;

            this.isLive2dLoading = true;

            try {
                await nextTick();
                const container = document.getElementById('live2d');
                if (container) {
                    this.live2dInstance = await loadLive2d(container);
                    console.log('Live2D initialized successfully');
                }
            } catch (error) {
                console.error('Failed to initialize Live2D:', error);
                this.live2dError = error.message;
            } finally {
                this.isLive2dLoading = false;
            }
        },
        destroyLive2d() {
            if (this.live2dInstance) {
                try {
                    this.live2dInstance.destroy();
                    this.live2dInstance = null;
                } catch (error) {
                    console.error('Error destroying Live2D:', error);
                }
            }
        },
        async loadSessionData(sessionId) {
            if (!sessionId) return;

            try {
                // 检查是否已加载过该会话的数据
                const existingSession = this.$store.getters.activeSession;
                if (existingSession && existingSession.sessionId === sessionId && existingSession.data && existingSession.data.length > 0) {
                    console.log('Session data already loaded:', sessionId);
                    this.isSubmitted = !!(existingSession.dag && Object.keys(existingSession.dag).length > 0);
                    return;
                }

                // 获取历史消息
                const messages = await getTasksBySession(sessionId);
                if (messages && messages.length > 0) {
                    const sessionData = messages;
                    chatStoreHelper.setSessionData(sessionId, sessionData);
                    this.$store.commit('chat/SET_SESSION_DATA', { sessionId, data: sessionData });
                    this.$store.commit('chat/SET_ACTIVE', sessionId);
                    this.isSubmitted = !!(messages[0]?.dag && Object.keys(messages[0]?.dag).length > 0);
                }
            } catch (error) {
                console.error('加载会话数据失败:', error);
            }
        },
        checkInitialState() {
            const activeId = this.$store.state.chat.active;
            if (activeId) {
                this.loadSessionData(activeId);
            }
        },
        goTo(path) {
            this.$router.push(path);
        },
        async onClickSubmit() {
            console.log('onClickSubmit called');
            if (!this.canSubmit) {
                this.$message.warning('当前会话无法提交，请检查状态');
                return;
            }

            this.isSubmitting = true;
            try {
                const taskData = {
                    session_id: String(this.active),
                    business: this.sessionState?.intent_result?.["任务名称"] || 'default',
                    state: this.sessionState || {},
                    params: this.sessionState?.intent_result || {},
                    dag: {}
                };
                console.log('Submitting task:', taskData);

                const result = await createTask(taskData);

                // 更新本地 session dag
                if (result && result.dag && Object.keys(result.dag).length > 0) {
                    this.$store.dispatch('setSessionState', this.sessionState, result.dag);
                }

                this.$message.success(`任务已提交成功！`);
            } catch (error) {
                console.error('提交失败, error:', error);
                console.error('error.message:', error.message);
                const errorMsg = error.message || '';
                if (errorMsg.includes('已存在') || errorMsg.includes('任务已存在')) {
                    this.$message.warning('该会话已提交过任务');
                    // 后端说已存在，说明任务已提交，更新本地dag状态防止重复提交
                    const fakeDag = { job_id: 'already_submitted_' + this.active };
                    // 直接操作 store 更新 dag
                    const session = this.$store.state.chat.chat.list.find(s => s.sessionId === this.active);
                    if (session) {
                        session.dag = fakeDag;
                        console.log('Dag updated directly, now job_id:', session.dag?.job_id);
                    }
                    // 标记组件状态
                    this.isSubmitted = true;
                    console.log('after update, alreadySubmitted computed should be true');
                } else {
                    this.$message.error('提交失败:' + errorMsg);
                }
            } finally {
                this.isSubmitting = false;
            }
        }
    }
}
</script>

<style lang="scss" scoped>
$animation-time: 0.3s;

.title-container {
    display: -webkit-box;
    display: -webkit-flex;
    display: -moz-box;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -webkit-flex-direction: column;
    -moz-box-orient: vertical;
    -moz-box-direction: normal;
    flex-direction: column;
    padding: 20px;
    gap: 4px;
    max-width: 1000px;
    margin: 0 auto;
}

.title-line {
    font-size: 30px;
    font-weight: bold;
    color: var(--app-title-color);
    margin: 0;

    span {
        color: var(--app-theme-color);
    }
}

.sub-title-line {
    font-size: 16px;
    color: var(--app-small-title-color);
}

.home {
    height: 100%;
    overflow-y: auto;
    scrollbar-width: none;
    padding-bottom: 120px;

    &::-webkit-scrollbar {
        display: none;
    }
}

#live2d {
    position: fixed;
    bottom: 0;
    left: 20%;
    width: 200px;
    height: 250px;
    z-index: 1;
    pointer-events: none;
    // 如果需要隐藏live2d可以设置display:none
}

.card {
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

    .card-header {
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
    }

    .card-body {
        font-size: 13px;
    }
}

.json-raw {
    margin-top: 8px;
    font-size: 12px;

    .json-label {
        display: block;
        margin-bottom: 4px;
        color: #666;
    }
}

.empty-text {
    color: #999;
    font-size: 13px;
}

/* 右侧边栏内容不超出 */
.el-aside {
    .el-main {
        overflow-x: hidden;
    }

    .el-space {
        width: 100%;

        :deep(.el-space__item) {
            width: 100%;
        }
    }
}

.session-id-tag {
    border-radius: 4px;
}

.dag-preview-wrapper {
    overflow-y: auto;
    max-height: none;
}

@media screen and (max-width: 768px) {
    .title-line {
        font-size: 24px;
    }

    .sub-title-line {
        font-size: 14px;
    }

    #live2d {
        display: none;
    }
}
</style>
