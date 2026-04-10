<template>
    <el-container style="height: 100%;">
        <el-main style="height: 100%; padding: 0;">
            <el-row justify="center" style="height: 100%;">
                <el-col :md="14" :sm="14" :xs="14" style="padding-left: 0;padding-right: 0; ">
                    <div class="home" ref="homeRef">

                        <el-row :gutter="24" justify="center" style="margin-left: 0;margin-right: 0;">
                            <!-- <el-row :gutter="24" style="margin-left: 0;margin-right: 0;"> -->
                            <el-col :md="22" :sm="22" :xs="22">
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
        <el-aside  width="30%" style="  padding-top: 20px; border-left: 1px solid #999; ">
            <el-container style="display: flex; flex-direction: column; height: 100%; width: 100%; align-items: center;">
                <el-main style="padding: 0; display: flex; flex-direction: column; width: 100%; ">

                    <el-space direction="vertical" :size="30" style="max-width: 100%; ">
                        <!-- 智算业务id -->
                        <!-- <div class="card"> -->
                        <el-tag type="primary" size="large" class="card-header" >
                            智算业务id： {{ active ?active:"暂未开始解析"}}
                        </el-tag>
                        <!-- </div> -->

                        <!-- 意图解析结果 -->
                        <div class="card"   >
                            <el-tag type="info" class="card-header">
                                意图解析结果
                    
                            </el-tag>
            
                            <v-md-preview   v-if="showIntentPreview && active"  :key="sessionStateIntentText"  :text="sessionStateIntentText" class="card-body"></v-md-preview>
                        </div>

                        <!-- 任务DAG -->
                        <div class="card">
                            <el-tag type="warning" class="card-header">
                                任务DAG
                
                            </el-tag>
                            <v-md-preview    v-if="showDagPreview && active" :key="sessionStateDagText"   :text="sessionStateDagText" class="card-body"></v-md-preview>
                        </div>
                    </el-space>
                </el-main>

                <el-footer
                    style="text-align: center; width: 100%; border-top: 1px solid #999; display: flex;justify-content: center; align-items: center;">
                   
                    <el-button 
                        :style="{ width: '100px' }" 
                        type="primary" 
                        :disabled="!canSubmit || isSubmitted|| isSubmitting"
                        :loading="isSubmitting"
                        @click="onClickSubmit">
                        {{ isSubmitted ? '已提交' : '提交' }}
                       
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
        sessionStateIntentText() {
            const activeSession = this.$store.getters.activeSession;
            // const state=
            // console.log('计算属性 sessionStateIntentText 重新计算，active:', this.active, 'sessionState.intent_result:', activeSession.state.intent_result);
             return `\`\`\`json\n${JSON.stringify( activeSession?.state?.intent_result|| {},null,2)}\n\`\`\``;
  },
    sessionStateDagText() {
        const activeSession = this.$store.getters.activeSession;
      return `\`\`\`json\n${JSON.stringify( activeSession?.state?.dag|| {}, null, 2)}\n\`\`\``
    },
        sessionState(){
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
        // 看板娘启用状态
        live2dEnabled() {
            return this.$store.state.setting.live2d_enabled || false;
        },
        // 当前看板娘模型
        currentLive2dModel() {
            return this.$store.state.setting.live2d_model || null;
        },
        // 当前激活的会话对象
        activeSession() {
            return this.$store.getters.activeSession;
        },
        // 提交按钮是否可用：workflow===\"dag\" 且未提交过
        canSubmit() {
            const activeSession = this.$store.getters.activeSession;
            // const sessionState = activeSession?.sessionState;
            
            return  this.active && this.active !== "" && activeSession?.state?.workflow === 'dag' ;
        }

    },
    methods: {
        refreshIntentPreview() {
      this.showIntentPreview = false
      nextTick(() => {
        this.showIntentPreview = true
      })
    },
    refreshDagPreview() {
      this.showDagPreview = false
      nextTick(() => {
        this.showDagPreview = true
      })
    },
        // 统一处理滚动
        scrollToBottom() {
            this.$nextTick(() => {
                if (this.$refs.homeRef) {
                    this.$refs.homeRef.scrollTop = this.$refs.homeRef.scrollHeight;
                }
            });
        },
        // 初始化Live2D
        async initLive2d() {
            if (window.innerWidth <= 768 || !this.live2dEnabled || !this.currentLive2dModel) {
                if (this.live2dInstance) {
                    // 清理现有实例
                    this.live2dInstance.dispose && this.live2dInstance.dispose();
                    this.live2dInstance = null;
                }
                return;
            }

            this.isLive2dLoading = true;
            this.live2dError = null;

            try {
                // 清理现有实例
                if (this.live2dInstance) {
                    this.live2dInstance.dispose && this.live2dInstance.dispose();
                }

                this.live2dInstance = await loadLive2d({
                    canvas: "live2d",
                    baseUrl: this.currentLive2dModel.substring(0, this.currentLive2dModel.lastIndexOf('/')),
                    model: this.currentLive2dModel,
                    globalFollowPointer: true,
                    allowSound: true,
                    height: "800"
                });
            } catch (error) {
                console.error('Live2D 加载失败:', error);
                this.live2dError = error.message || '初始化失败';
            } finally {
                this.isLive2dLoading = false;
            }
        },
        /**
         * 提交会话到后端
         */
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
                    business: this.sessionState?.intent_result?.["业务类型"] || 'default',
                    state: this.sessionState || {},
                    params: this.sessionState?.intent_result || {},
                    dag: this.sessionState?.dag || {}
                };
                console.log('Submitting task:', taskData);

                await createTask(taskData);
                this.isSubmitted = true;
                this.$message.success(`任务已提交成功！`);
            } catch (error) {
                console.log('提交失败:', error);
                if (error.message && error.message.includes('已存在')) {
                    this.isSubmitted = true;
                    this.$message.success(`已提交，请勿重复提交`);
                } else {
                    this.$message.error(`提交失败: ${error.message}`);
                }
            } finally {
                this.isSubmitting = false;
            }
        },
        /**
         * 跳转页面函数
         * @param path
         */
        goTo(path) {
            this.$router.push(path)
        }
    },
    watch: {
        "$store.state.chat.active": {
            handler: function () {
                this.scrollToBottom();
               this.isSubmitted = false;
            }
        },
        sessionState: {
        handler(newVal) {
            this.refreshIntentPreview();
            this.refreshDagPreview();
        }
    },
        query() {
            this.scrollToBottom();
        },
        currentLive2dModel: {
            handler: function () {
                this.initLive2d();
            }
        },
        live2dEnabled: {
            handler: function () {
                this.initLive2d();
            }
        }
    },
    mounted() {
        this.initLive2d();
    },
    created() {
        this.scrollToBottom();
    }
}
</script>

<style lang="scss" scoped>
.card {
    background-color: #9babf1;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 16px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
}

.card-header {
    // width: 50%;
    font-size: 20px;
    font-weight: bold;
    // padding: 10px 20px;
    border-radius: 4px;
    color: rgba(53, 49, 111, 0.704);
    // margin-bottom: 12px;
    display: block;
}

.card-header[type="success"] {
    background-color: #4CAF50;
    /* Green */
}

.card-header[type="info"] {
    background-color: #409EFF;
    /* Blue */
}

.card-header[type="warning"] {
    background-color: #FF9800;
    /* Orange */
}

.card-body {

    background-color: #f5f5f5;
    padding: 2px;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
}

.card-body code {
    font-size: 14px;
    color: #333;
    word-wrap: break-word;
}

/* 确保容器可以滚动 */
.home {
    height: 100%;
    overflow-y: scroll;
    scrollbar-width: none;
    /* Firefox */
}

.home::-webkit-scrollbar {
    display: none;
    /* Chrome, Safari 和 Opera */
}

.el-link {
    margin-right: 8px;
}

.el-link .el-icon--right.el-icon {
    vertical-align: text-bottom;
}

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
    margin: 2vh auto;
    width: fit-content;
    text-align: center;
    border-radius: 20px;
}

.title-container .title-line {
    font-style: normal;
    font-weight: 700;
    font-size: 34px;
    line-height: 52px;
    color: #1a2029;
    margin-bottom: 14px;
}

.title-container .title-line span {
    color: #2454ff;
}

.title-container .sub-title-line {
    font-size: 15px;
}

/* 修改live2d容器样式 */
#live2d {
    // border: 1px solid #000;
    width: 200px;
    position: fixed;
    /* 改为固定定位 */
    bottom: 82px;
    /* 固定在底部 */
    right: -20px;
    /* 固定在右侧 */
    z-index: 100;
    /* 确保在其他元素上层 */

    /* 在小屏幕设备上隐藏live2d */
    @media screen and (max-width: 768px) {
        display: none;
    }
}
</style>
