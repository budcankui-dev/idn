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
                                    <div class="sub-title-line">例如：我计划进行视联网任务的部署，源IP为从192.168.5.3目的IP为192.65.36.25。
                                    </div>
                                    <div class="sub-title-line">
                                        <el-link type="primary" href="https://unagi-cq.github.io/BUPT/#/docs"
                                            @click="goTo('/about')">
                                            {{ $t('AppMain.viewDocs') }}
                                        </el-link>
                                    </div>
                                </div>
                            </el-col>


                        </el-row>


                        <canvas id="live2d"></canvas>
                    </div>
                </el-col>
            </el-row>
        </el-main>
        <el-aside v-if="!is_show" width="30%" style="  padding-top: 20px; border-left: 1px solid #999; ">
            <el-cotainer style="display: flex; flex-direction: column; height: 100%; width: 100%; align-items: center;">
                <el-main style="padding: 0; display: flex; flex-direction: column; width: 100%; ">
                    <!-- <el-space direction="vertical" :size="30" style="width: 100%;">
                        <el-tag type="primary" style="font-size: 24px; font-weight: bold;" size="large">
                            智算业务id： job_001 
                        </el-tag>
                       
                        <el-tag type="primary" style="font-size: 24px; font-weight: bold;" size="large">
                            意图解析结果
                        </el-tag>

                        <v-md-preview :text="previewText"></v-md-preview>


                        <el-tag type="primary" style="font-size: 24px; font-weight: bold; " size="large">
                            任务DAG
                        </el-tag>

                        <v-md-preview :text="previewText"></v-md-preview>
                    </el-space> -->

                    <el-space direction="vertical" :size="30" style="width: 100%; ">
                        <!-- 智算业务id -->
                        <!-- <div class="card"> -->
                        <el-tag type="primary" size="large" class="card-header">
                            智算业务id： {{ active }}
                        </el-tag>
                        <!-- </div> -->

                        <!-- 意图解析结果 -->
                        <div class="card">
                            <el-tag type="info" class="card-header">
                                意图解析结果
                            </el-tag>
                            <v-md-preview :text="previewText" class="card-body"></v-md-preview>
                        </div>

                        <!-- 任务DAG -->
                        <div class="card">
                            <el-tag type="warning" class="card-header">
                                任务DAG
                            </el-tag>
                            <v-md-preview :text="previewText" class="card-body"></v-md-preview>
                        </div>
                    </el-space>
                </el-main>

                <el-footer
                    style="text-align: center; width: 100%; border-top: 1px solid #999; display: flex;justify-content: center; align-items: center;">
                    <el-button :style="{ width: '100px' }" type="primary">提交</el-button>
                </el-footer>
            </el-cotainer>

        </el-aside>
    </el-container>



</template>

<script>
import loadLive2d from 'live2d-helper'

export default {
    name: 'AppMain',
    data() {
        return {
            previewText: '```json\n{"business_type": "视频AI推理"}\n```',
            isLive2dLoading: false,
            live2dError: null,
            live2dInstance: null  // 添加实例引用
        }
    },
    computed: {
        // 当前激活的聊天记录uuid
        active() {
            return this.$store.state.app.active;
        },
        // 激活会话的QA对
        active_session_qa_data() {
            const activeSession = this.$store.state.app.chat.findSession(this.active);
            return activeSession?.data || [];
        },
        // 等app数据加载之后再执行逻辑 否则会闪屏
        is_show() {
            return this.$store.state.app.ready && this.active_session_qa_data.length === 0;
        },
        // 看板娘启用状态
        live2dEnabled() {
            return this.$store.state.setting.live2d_enabled || false;
        },
        // 当前看板娘模型
        currentLive2dModel() {
            return this.$store.state.setting.live2d_model || null;
        }
    },
    methods: {
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
         * 跳转页面函数
         * @param path
         */
        goTo(path) {
            this.$router.push(path)
        }
    },
    watch: {
        "$store.state.app.chat": {
            deep: true,
            handler: function (newVal, oldVal) {
                const isAtBottom = this.$refs.homeRef.scrollTop + this.$refs.homeRef.clientHeight >= this.$refs.homeRef.scrollHeight - 200;
                if (isAtBottom) {
                    this.scrollToBottom();
                }
            }
        },
        "$store.state.app.active": {
            deep: true,
            handler: function () {
                this.scrollToBottom();
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
    font-size: 20px;
    font-weight: bold;
    // padding: 10px 20px;
    border-radius: 4px;
    color: rgba(53, 49, 111, 0.704);
    // margin-bottom: 12px;
    display: inline-block;
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
    padding: 20px;
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
