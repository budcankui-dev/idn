<template>
    <div class="search-container">
        <!-- 输入框 -->
         <!-- @input="forceUpdate($event)" -->
        <el-input :placeholder="$t('SendBox.placeholder')" ref="queryInput"  v-model="this.query" 
            :autosize="{ minRows: 1, maxRows: 8 }" resize="none" @keydown.enter="onEnterKeyDown" @input="forceUpdate($event)" 
            @keydown.up="onEnterKeyUp" type="textarea" :class="{ 'has-files': uploadedFiles.length > 0 }"></el-input>

        <div class="left-icons" v-if="uploadedFiles.length === 0">
            <!-- 上传图标 -->
            <el-upload class="upload-icon" action="" :show-file-list="false" :auto-upload="false" accept="image/*"
                :multiple="false" :on-change="handleImageUpload" :limit="upload_limit"
                :disabled="uploadedFiles.length >= upload_limit">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
                    <path
                        d="M6.93745 10C6.24652 10.0051 5.83076 10.0263 5.4996 10.114C3.99238 10.5131 2.96048 11.8639 3.00111 13.3847C3.01288 13.8252 3.18057 14.3696 3.51595 15.4585C4.32309 18.079 5.67958 20.3539 8.7184 20.8997C9.27699 21 9.90556 21 11.1627 21L12.8372 21C14.0943 21 14.7229 21 15.2815 20.8997C18.3203 20.3539 19.6768 18.079 20.4839 15.4585C20.8193 14.3696 20.987 13.8252 20.9988 13.3847C21.0394 11.8639 20.0075 10.5131 18.5003 10.114C18.1691 10.0263 17.7534 10.0051 17.0625 10"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    <path
                        d="M12 3L12 14M12 3C12.4683 3 12.8243 3.4381 13.5364 4.3143L14.5 5.5M12 3C11.5316 3 11.1756 3.4381 10.4635 4.3143L9.49995 5.5"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
            </el-upload>
            <!-- 知识库图标 -->
            <div class="web-search-icon-wrapper" :class="{ 'selected': knowledgeEnabled }"
                @click="knowledgeEnabled = !knowledgeEnabled">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none"
                    class="rag">
                    <path
                        d="M8.85746 12.5061C6.36901 10.6456 4.59564 8.59915 3.62734 7.44867C3.3276 7.09253 3.22938 6.8319 3.17033 6.3728C2.96811 4.8008 2.86701 4.0148 3.32795 3.5074C3.7889 3 4.60404 3 6.23433 3H17.7657C19.396 3 20.2111 3 20.672 3.5074C21.133 4.0148 21.0319 4.8008 20.8297 6.37281C20.7706 6.83191 20.6724 7.09254 20.3726 7.44867C19.403 8.60062 17.6261 10.6507 15.1326 12.5135C14.907 12.6821 14.7583 12.9567 14.7307 13.2614C14.4837 15.992 14.2559 17.4876 14.1141 18.2442C13.8853 19.4657 12.1532 20.2006 11.226 20.8563C10.6741 21.2466 10.0043 20.782 9.93278 20.1778C9.79643 19.0261 9.53961 16.6864 9.25927 13.2614C9.23409 12.9539 9.08486 12.6761 8.85746 12.5061Z"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span v-if="knowledgeEnabled" class="search-text rag">{{ selectedRepo?.name }}</span>
            </div>
            <!-- 联网图标 -->
            <div class="web-search-icon-wrapper" :class="{ 'selected': webSearchEnabled }"
                @click="webSearchEnabled = !webSearchEnabled">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none">
                    <path
                        d="M8.9835 1.99998C6.17689 2.06393 4.53758 2.33109 3.41752 3.44727C2.43723 4.42416 2.10954 5.79742 2 7.99998M15.0165 1.99998C17.8231 2.06393 19.4624 2.33109 20.5825 3.44727C21.5628 4.42416 21.8905 5.79742 22 7.99998M15.0165 22C17.8231 21.9361 19.4624 21.6689 20.5825 20.5527C21.5628 19.5758 21.8905 18.2026 22 16M8.9835 22C6.17689 21.9361 4.53758 21.6689 3.41752 20.5527C2.43723 19.5758 2.10954 18.2026 2 16"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    <path
                        d="M15 15L17 17M16 11.5C16 9.01468 13.9853 6.99998 11.5 6.99998C9.01469 6.99998 7 9.01468 7 11.5C7 13.9853 9.01469 16 11.5 16C13.9853 16 16 13.9853 16 11.5Z"
                        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span v-if="webSearchEnabled" class="search-text">{{ $t('SendBox.webSearch') }}</span>
            </div>
        </div>

        <div class="right-icons">
            <!-- 发送ICON with label -->
            <div class="icon-with-label" v-if="controller === undefined" @click="onSubmitChat">
                <span>意图解析</span>
                <el-button type="primary" @click="onSubmitChat" class="right-send-stop-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none">
                        <path
                            d="M11.922 4.79004C16.6963 3.16245 19.0834 2.34866 20.3674 3.63261C21.6513 4.91656 20.8375 7.30371 19.21 12.078L18.1016 15.3292C16.8517 18.9958 16.2267 20.8291 15.1964 20.9808C14.9195 21.0216 14.6328 20.9971 14.3587 20.9091C13.3395 20.5819 12.8007 18.6489 11.7231 14.783C11.4841 13.9255 11.3646 13.4967 11.0924 13.1692C11.0134 13.0742 10.9258 12.9866 10.8308 12.9076C10.5033 12.6354 10.0745 12.5159 9.21705 12.2769C5.35111 11.1993 3.41814 10.6605 3.0909 9.64127C3.00292 9.36724 2.97837 9.08053 3.01916 8.80355C3.17088 7.77332 5.00419 7.14834 8.6708 5.89838L11.922 4.79004Z"
                            stroke="currentColor" stroke-width="3.5" />
                    </svg>
                </el-button>
            </div>
            <!-- 停止发送ICON -->
            <el-button type="danger" @click="stopChat" v-else class="right-send-stop-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3.5" />
                    <path d="M9.5 9L9.5 15M14.5 9V15" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
            </el-button>

        </div>

        <!-- 文件预览容器 -->
        <div class="file-preview-container" v-if="uploadedFiles.length > 0">
            <div class="file-preview-item" v-for="(file, index) in uploadedFiles" :key="index">
                <img :src="file.base64" alt="uploaded file" />
                <div class="delete-icon" @click="removeFile(index)">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none">
                        <path d="M19.0005 4.99988L5.00049 18.9999M5.00049 4.99988L19.0005 18.9999" stroke="currentColor"
                            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                </div>
            </div>
        </div>


    </div>
</template>

<script>
import { postProcess } from "@/util/config";
import tabStoreHelper from "@/schema/tabStoreHelper";
import chatStoreHelper from "@/schema/chatStoreHelper";
import { QA, Session } from "@/schema/chat";
import { Segment, useDefault } from 'segmentit';
import Loading from '@/components/SendBox/loading.vue'; // 引入 loading.vue//ILOVEU
import ImageDisplay from '@/components/SendBox/ImageDisplay.vue'; //ILOVEU
import { v4 as uuidv4 } from 'uuid'
console.log('Loading component:', Loading); // 确认组件是否导入//ILOVEUimpo
console.log('Loading component:', ImageDisplay); // 确认组件是否导入//ILOVEUimpo

const segmentit = useDefault(new Segment());

export default {
    name: 'SendBox',
    components: {
        Loading, // 注册 loading 组件 ILOVEU
        ImageDisplay,// 注册 ImageDisplay 组件 ILOVEU
    },
    data() {
        return {
            query: "",
            key:0,
            controller: undefined,
            uploadedFiles: [],
            isWebSearchEnabled: false,
            routeDialogVisible: false, // 控制弹窗显示状态
            routeResult: '', // 存储路径计算结果
            isCalculating: false, // 控制加载状态
            showLoading: false, // 控制 loading 组件显示的状态ILOVEU
            showImage: false, // 控制图片展示ILOVEU
        }
    },
    mounted() {
        document.addEventListener('paste', this.handlePaste);
    },
    beforeDestroy() {
        document.removeEventListener('paste', this.handlePaste);
    },
    computed: {
        active: {
            get() {
                return this.$store.state.app.active;
            },
            set(val) {
                this.$store.dispatch('setActive', val);
            }
        },
        chat() {
            return this.$store.state.app.chat;
        },
        active_session_qa_data() {
            const activeSession = this.chat.findSession(this.active);
            return activeSession?.data || [];
        },
        platform() {
            return this.$store.state.setting.platform;
        },
        model_config() {
            return this.$store.state.setting.model_config;
        },
        upload_limit() {
            return this.$store.state.setting.upload_limit;
        },
        upload_size() {
            return this.$store.state.setting.upload_size;
        },
        knowledgeEnabled: {
            get() {
                return this.$store.state.setting.kb_enabled || false;
            },
            set(val) {
                this.$store.dispatch('changeSetting', {
                    key: 'kb_enabled',
                    value: val
                })
            }
        },
        webSearchEnabled: {
            get() {
                return this.$store.state.setting.web_search_enabled;
            },
            set(val) {
                this.$store.dispatch('changeSetting', {
                    key: 'web_search_enabled',
                    value: val
                })
            }
        },
        selectedRepo() {
            const repoList = this.$store.state.app.kb.list || [];
            const selectedId = this.$store.state.setting.selected_repoId;
            const selectedRepo = repoList.find(repo => repo.repoId === selectedId);
            return selectedRepo;
        }
    },
    methods: {
        forceUpdate(e) {
            
            this.$forceUpdate()
        },
        onEnterKeyDown(e) {

            if (e.key === 'Enter') {
                if (!e.shiftKey) {
                    e.preventDefault();
                    this.onSubmitChat();
                 
                }
            }
        },
        onEnterKeyUp() {
            if (this.query === '') {
                console.log("dadasdas")
                if (this.active_session_qa_data.length > 0) {
                    this.query = this.active_session_qa_data[this.active_session_qa_data.length - 1].query;
                }
            }
        },
        stopChat() {
            if (this.controller) {
                this.controller.abort();
                this.controller = undefined;
            }
        },
        getDynamicCall() {
            if (this.platform === 'Ali_DashScope') {
                return import("@/api/Ali_DashScope").then(module => module.fetchAPI);
            } else if (this.platform === 'Xunfei_Spark') {
                return import("@/api/Xunfei_Spark").then(module => module.fetchAPI);
            } else if (this.platform === 'Zhipu_BigModel') {
                return import("@/api/Zhipu_BigModel").then(module => module.fetchAPI);
            } else if (this.platform === 'Baidu_QianFan') {
                return import("@/api/Baidu_QianFan").then(module => module.fetchAPI);
            } else if (this.platform === 'Local') {
                return import("@/api/Local").then(module => module.fetchAPI);
            } else if (this.platform === 'Moonshot_AI') {
                return import("@/api/Moonshot_AI").then(module => module.fetchAPI);
            } else if (this.platform === 'OpenAI') {
                return import("@/api/OpenAI").then(module => module.fetchAPI);
            } else if (this.platform === 'TT_Volcengine') {
                return import("@/api/TT_Volcengine").then(module => module.fetchAPI);
            } else if (this.platform === 'Yidong_CMECloud') {
                return import("@/api/Yidong_CMECloud").then(module => module.fetchAPI);
            }
        },


        handleOverlayClick(event) {
            // 仅当点击 image-overlay 本身（而非其子元素）时关闭
            if (event.target.classList.contains('image-overlay')) {
                console.log('Clicked outside image, hiding image');
                this.showImage = false;
            }
        },

        async onSubmitChat() {
            this.query = this.query.trim();
            if (this.query === '') return;

            let [query, qaId, files] = [
                this.query,
                Date.now(),
                JSON.parse(JSON.stringify(this.uploadedFiles))
            ];

               // 清空输入框数据
            this.query = ""
            this.uploadedFiles = [];
            this.forceUpdate()
            


            let qa = new QA(qaId, query, "", files, undefined, undefined,
                this.model_config.series, this.model_config.name, this.model_config.type);

            if (this.active === '') {
                 const sessionId = uuidv4()
                tabStoreHelper.add(query, sessionId);
               
                console.log("Generated sessionId:", sessionId); // 调试日志
                let new_state={
                    session_id:sessionId,
                    // workflow:"intent_parsing",
                    // stage:"start",
                    // parse_success:false,
                }
                let session = new Session(sessionId, [qa],new_state);
                // console.log("session",session)
                chatStoreHelper.addSession(session);
                this.active =sessionId ;

            } else {
                chatStoreHelper.addQA(this.active, qa);
            }
            let session = chatStoreHelper.getSession(this.active)
            let history = [];
            if (this.$store.state.setting.memory) {
                history = this.active_session_qa_data
                    .slice((this.$store.state.setting.memory_limit + 1) * -1)
                    .filter(item => item.answer && item.answer.trim());
            }

            if (this.knowledgeEnabled && this.selectedRepo) {
                const matches = this.matchKnowledgeBase(query);
                if (matches.length > 0) {
                    query = `基于以下知识库内容回答问题:${matches.map(chunk => chunk.content).join('\n')}问题: ${query}`;
                    qa.recall = matches;
                    chatStoreHelper.addQA(this.active, qa);
                }
            }

            try {
                this.controller = new AbortController();
                const fetchAPI = await this.getDynamicCall();

                fetchAPI({

                    state: session.state,
                    prompt: query,
                    history: history,
                    files: files,
                    controller: this.controller,
                    onopen: (event) => {
                        console.log('连接成功');
                        qa.responseTime = new Date().getTime();
                        chatStoreHelper.addQA(this.active, qa);
                    },
                    onmessage: (event) => {
                        try {
                            if (event.data) {
                                // SSE 特殊结束符处理
                                if (event.data === '[DONE]') {
                                    // qa.answer = (qa.answer || '') 
                                    // 对完整内容的进行操作
                                    qa.finishTime = new Date().getTime();
                                    this.stopChat();
                                    chatStoreHelper.addQA(this.active, qa);
                                    console.log('流式结束');
                                    return;
                                }

                                // 1. 检查是否是 JSON 消息
                                const data = JSON.parse(event.data);
                                // 如果是 content chunk
                                if (data.content) {
                                    qa.answer = (qa.answer || '') + data.content;
                                    chatStoreHelper.addQA(this.active, qa);
                                }
                                // 如果是 state
                                if (data.type == "state") {
                                    if (data.parse_success && data.stage == "complete" && data.workflow == "intent_parsing") {
                                        data.workflow = "dag"
                                        // let qa = new QA(Date.now(), "", "", [], undefined, undefined,
                                        //     this.model_config.series, this.model_config.name, this.model_config.type);
                                        // qa.answer = "意图解析已完成，点击确认按钮提交解析结果。系统已为业务生成任务DAG。有疑问可以继续与我交流"
                                        // chatStoreHelper.addQA(this.active, qa)
                                         console.log("dag set", this.active, data)
                                    }
                                    // 更新 vuex store 中的 session 的state
                                    console.log("update", this.active, data)
                                    chatStoreHelper.setSessionState(this.active, data)

                                    // this.$store.commit('updateState', data.state);
                                }

                            }
                        } catch (e) {
                            console.error("解析 SSE 消息错误:", e, event);
                        }
                    },
                    onclose: () => {
                        console.log("连接关闭");
                        qa.finishTime = new Date().getTime();
                        this.stopChat();
                        chatStoreHelper.addQA(this.active, qa);
                    },
                    onerror: (error) => {
                        console.error('流式接口错误:', error);
                        this.stopChat();
                        this.$message.error(this.$t('SendBox.errors.system', { error }));
                    }
                });

            } catch (e) {
                console.error("提交聊天异常:", e);
            }
        },
        // async onSubmitChat() {
        //     this.query = this.query.trim();
        //     if (this.query === '') {
        //         return;
        //     }
        //     let [query, qaId, files] = [
        //         this.query,
        //         Date.now(),
        //         JSON.parse(JSON.stringify(this.uploadedFiles))
        //     ];
        //     this.query = '';
        //     this.uploadedFiles = [];
        //     let qa = new QA(qaId, query, "", files, undefined, undefined, this.model_config.series, this.model_config.name, this.model_config.type);
        //     if (this.active === '') {
        //         tabStoreHelper.add(query, qaId);
        //         let session = new Session(qaId, [qa]);
        //         chatStoreHelper.addSession(session);
        //         this.active = qaId;
        //     } else {
        //         chatStoreHelper.addQA(this.active, qa);
        //     }
        //     let history = [];
        //     if (this.$store.state.setting.memory) {
        //         history = this.active_session_qa_data
        //             .slice((this.$store.state.setting.memory_limit + 1) * -1)
        //             .filter(item => item.answer && item.answer.trim());
        //     }
        //     if (this.knowledgeEnabled && this.selectedRepo) {
        //         const matches = this.matchKnowledgeBase(query);
        //         if (matches.length > 0) {
        //             query = `基于以下知识库内容回答问题:${matches.map(chunk => chunk.content).join('\n')}问题: ${query}`;
        //             qa.recall = matches;
        //             chatStoreHelper.addQA(this.active, qa);
        //         }
        //     }
        //     try {
        //         this.controller = new AbortController();
        //         this.getDynamicCall().then(fetchAPI => {
        //             fetchAPI({
        //                 prompt: query,
        //                 history: history,
        //                 files: files,
        //                 controller: this.controller,
        //                 onopen: (event) => {
        //                     console.log('连接成功');
        //                     if (event !== undefined && event.status === 401) {
        //                         this.$notify({
        //                             title: this.$t('SendBox.notifications.remoteFailed'),
        //                             message: this.$t('SendBox.errors.apiKey'),
        //                             type: 'error',
        //                         });
        //                     }
        //                     if (event !== undefined && (event.status === 500 || event.status === 404)) {
        //                         this.$notify({
        //                             title: this.$t('SendBox.notifications.connectionFailed'),
        //                             message: this.$t('SendBox.errors.connection'),
        //                             type: 'error',
        //                         });
        //                     } else if (event !== undefined && event.status === 422) {
        //                         this.$notify({
        //                             title: this.$t('SendBox.notifications.interfaceError'),
        //                             message: this.$t('SendBox.errors.interface'),
        //                             type: 'error',
        //                         });
        //                     }
        //                     qa.responseTime = new Date().getTime();
        //                     chatStoreHelper.addQA(this.active, qa);
        //                 },
        //                 onmessage: (event) => {
        //                     console.log("消息传输");
        //                     if (event.event === 'error') {
        //                         this.$notify({
        //                             title: this.$t('SendBox.notifications.interfaceError'),
        //                             message: this.$t('SendBox.errors.internalError'),
        //                             type: 'error',
        //                         });
        //                         qa.finishTime = new Date().getTime();
        //                         this.stopChat();
        //                         return;
        //                     }
        //                     if (event !== undefined && event.error && event.error.code === '1301') {
        //                         this.$notify({
        //                             title: this.$t('Common.failed'),
        //                             message: event.error.message,
        //                             type: 'error',
        //                         });
        //                         return;
        //                     }
        //                     try {
        //                         console.log("原始消息:", event);
        //                         const newContent = postProcess(event, this.model_config.post_method);
        //                         if (newContent && newContent.content) {
        //                             qa.answer = (qa.answer || '') + newContent.content;
        //                             chatStoreHelper.addQA(this.active, qa);
        //                         } else if (newContent && newContent.reasoning_content) {
        //                             qa.reason = (qa.reason || '') + newContent.reasoning_content;
        //                             chatStoreHelper.addQA(this.active, qa);
        //                         }
        //                     } catch (e) {
        //                         console.error("解析响应错误:", e, event);
        //                     }
        //                 },
        //                 onclose: () => {
        //                     console.log("连接关闭");
        //                     qa.finishTime = new Date().getTime();
        //                     this.stopChat();
        //                     chatStoreHelper.addQA(this.active, qa);
        //                 },
        //                 onerror: (error) => {
        //                     console.log('close', error);
        //                     this.stopChat();
        //                     this.$message.error(this.$t('SendBox.errors.system', { error }));
        //                 }
        //             });
        //         });
        //     } catch (e) {
        //         console.error(e);
        //     }
        // },
        processImage(file) {
            if (this.uploadedFiles.length >= this.upload_limit) {
                this.$notify({
                    title: this.$t('SendBox.notifications.uploadFailed'),
                    message: this.$t('SendBox.uploadLimit.error', { limit: this.upload_limit }),
                    type: 'error'
                });
                return false;
            }
            const isImage = file.type.startsWith(this.$store.state.setting.upload_type);
            const isLt2M = file.size / 1024 / 1024 <= this.upload_size;
            if (!isImage) {
                this.$notify({
                    title: this.$t('SendBox.notifications.uploadFailed'),
                    message: this.$t('SendBox.uploadType.error'),
                    type: 'error'
                });
                return false;
            }
            if (!isLt2M) {
                this.$notify({
                    title: this.$t('SendBox.notifications.uploadFailed'),
                    message: this.$t('SendBox.uploadSize.error', { size: this.upload_size }),
                    type: 'error'
                });
                return false;
            }
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                this.uploadedFiles.push({
                    base64: reader.result,
                    file: file
                });
            };
            return true;
        },
        handleImageUpload(file) {
            this.processImage(file.raw);
        },
        handlePaste(event) {
            const items = (event.clipboardData || event.originalEvent.clipboardData).items;
            for (const item of items) {
                if (item.type.indexOf('image') !== -1) {
                    const file = item.getAsFile();
                    this.processImage(file);
                    break;
                }
            }
        },
        removeFile(index) {
            this.uploadedFiles.splice(index, 1);
        },
        calculateRelevanceScore(query, words) {
            const k1 = 1.5;
            const b = 0.75;
            const queryWords = segmentit.doSegment(query.toLowerCase()).map(word => word.w);
            const avgDocLength = words.length;
            let score = 0;
            const wordFreq = new Map();
            words.forEach(word => {
                wordFreq.set(word, (wordFreq.get(word) || 0) + 1);
            });
            queryWords.forEach(qWord => {
                const tf = wordFreq.get(qWord) || 0;
                if (tf === 0) return;
                const idf = Math.log(1.5);
                const numerator = tf * (k1 + 1);
                const denominator = tf + k1 * (1 - b + b * (words.length / avgDocLength));
                score += idf * (numerator / denominator);
            });
            return Math.min(score, 1);
        },
        matchKnowledgeBase(query) {
            if (!this.selectedRepo) return [];
            const allChunks = [];
            this.selectedRepo.list.forEach(file => {
                file.list.forEach(chunk => {
                    allChunks.push({
                        content: chunk.content,
                        score: this.calculateRelevanceScore(query, chunk.words),
                        filename: file.name
                    });
                });
            });
            allChunks.sort((a, b) => b.score - a.score);
            return allChunks
                .slice(0, this.$store.state.setting.recall_count)
                .filter(chunk => chunk.score > 0.6);
        },
        // 显示路径计算弹窗
        async showRouteDialog() {
            console.log('Route dialog triggered');
            this.isCalculating = true;
            try {
                this.routeResult = await this.calculateRoute();
            } catch (error) {
                this.routeResult = '计算路径失败';
                console.error('Route calculation error:', error);
            } finally {
                this.isCalculating = false;
                this.routeDialogVisible = true;
            }
        },
        // 关闭弹窗
        handleCloseDialog(done) {
            console.log('Closing route dialog');
            this.routeDialogVisible = false;
            this.routeResult = ''; // Reset result on close
            done();
        },
        // 模拟路径计算逻辑
        calculateRoute() {
            // Placeholder for actual route calculation logic (e.g., API call)
            return new Promise((resolve) => {
                setTimeout(() => resolve('从A到B的最短路径为10km'), 1000);
            });
        }
    }
}
</script>

<style lang="scss" scoped>
/**
 * 变量定义
 */
$icon-length: 32px;

/**
 * 通用的hover效果定义
 */
@mixin hover-effect {

    &.active,
    &:hover {
        background: var(--aside-active-hover-bg);
        border-radius: 4px;
    }
}

/**
 * 发送框容器
 */
.search-container {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    min-height: 40px;
}

/**
 * 左侧icons
 */

/**
 * 左侧icons
 */
.left-icons {
    position: absolute;
    left: 6px;
    bottom: 0;
    display: flex;
    gap: 8px;
    z-index: 88;

    svg {
        padding: 2px;
        cursor: pointer;
        color: var(--common-color);
        opacity: 0.6;
        transition: opacity 0.2s;

        &:hover {
            opacity: 1;
        }

        @include hover-effect;
    }

    .web-search-icon-wrapper {
        height: 24px;
        display: flex;
        align-items: center;
        gap: 4px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        min-width: 24px;
        overflow: hidden;

        svg {
            flex-shrink: 0;
        }

        .search-text {
            font-size: 12px;
            color: var(--el-color-primary);
            white-space: nowrap;
            opacity: 0;
            max-width: 0;
            transition: all 0.3s ease;
        }

        &.selected {
            svg {
                color: rgb(2 133 255);
                opacity: 1;
                pointer-events: none;

                &.rag {
                    color: var(--el-color-danger);
                }
            }

            background-color: var(--el-color-primary-light-9);
            padding: 0 8px 0 0;
        }

        .search-text {
            opacity: 1;
            max-width: 100px;
            font-size: 12px;
            font-weight: bold;
            color: rgb(2 133 255);

            &.rag {
                color: var(--el-color-danger);
            }
        }
    }
}

/**
 * 右侧icons 右下角定位篇章
 */
.right-icons {
    position: absolute;
    bottom: 4px;
    right: 2px;
    z-index: 88;
    display: flex;
    align-items: center;
    gap: 4px;

    .right-send-stop-button {
        height: $icon-length;
        width: $icon-length;
        border-radius: 10px;
    }

    .icon-with-label {
        display: flex;
        align-items: center;
        height: $icon-length;
        border: 1px solid var(--el-color-primary);
        border-radius: 10px;
        background: var(--el-color-primary-light-9);
        padding: 0 8px;
        cursor: pointer;
        transition: background 0.3s ease;

        span {
            font-size: 16px;
            color: var(--el-color-primary);
            margin-right: 4px;
            white-space: nowrap;
            /* 在这里添加 */
            font-weight: bold;
            /* 或者使用 font-weight: 700; 设置字体*/
        }

        .right-send-stop-button {
            border: none;
            background: transparent;
            padding: 0;
            margin: 0;
        }

        .image-button-wrapper {
            height: $icon-length;
            width: $icon-length;
            border: none;
            background: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;

            img {
                width: 50%;
                height: 50%;
                object-fit: cover;
            }

            &.disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
        }

        &:hover {
            background: var(--el-color-primary-light-8);
        }
    }
}

/**
 * elementui输入框
 */
:deep(.el-textarea) {
    z-index: 2;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    // ILOVEU
    border-radius: 10px;
    border: 2px solid var(--common-color);
    background: var(--sendBox-bg-color);
    padding-bottom: $icon-length;
    transition: padding-bottom 0.2s ease;

    &.has-files {
        padding-bottom: $icon-length * 2;
    }
}

/**
 * 输入框内部样式
 */
:deep(.el-textarea__inner) {
    max-height: 200px;
    font-size: 14px;
    color: var(--common-color);
    background: var(--sendBox-bg-color);
    padding: 6px 32px 0 6px;
    border-radius: 10px;
    box-shadow: 0 0;
    font-weight: 100;
    height: calc(100% - $icon-length);
    scrollbar-width: none;

    &::placeholder {
        color: var(--common-color);
        opacity: 0.2;
    }
}

:deep(.el-textarea__inner)::-webkit-scrollbar {
    display: none;
}

/**
 * 文件预览容器样式
 */
.file-preview-container {
    z-index: 3;
    position: absolute;
    left: 3px;
    top: -20px;
    display: flex;
    gap: 8px;
    max-width: 100%;
    height: 50px;
    overflow-x: auto;
    padding: 4px;

    .file-preview-item {
        position: relative;
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid var(--app-small-border-color);
        width: 50px;

        img {
            width: 300%;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            object-fit: cover;
            object-position: center;
        }

        .delete-icon {
            position: absolute;
            top: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10%;
            padding: 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.3s ease;

            svg {
                color: white;
            }

            &:hover {
                background: rgba(0, 0, 0, 0.7);
            }
        }
    }
}

/**
 * 弹窗样式
 */
:deep(.route-dialog) {
    z-index: 2000 !important;

    .el-dialog {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        background: var(--sendBox-bg-color);

        .el-dialog__header {
            background: var(--el-color-primary-light-9);
            border-bottom: 1px solid var(--el-color-primary-light-5);
            padding: 15px 20px;
        }

        .el-dialog__title {
            color: var(--el-color-primary);
            font-weight: bold;
        }

        .el-dialog__body {
            padding: 20px;
            font-size: 14px;
            color: var(--common-color);
        }

        .el-dialog__footer {
            padding: 10px 20px;
            border-top: 1px solid var(--el-color-primary-light-5);
            text-align: right;
        }
    }

    .dialog-content {
        min-height: 50px;
    }
}
</style>
<style scoped>
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    /* 灰暗背景，与 loading.vue 一致 */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    border: 2px solid red;
    /* 调试边框 */
}

.image-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    /* 与 loading-overlay 相同的背景 */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    border: 2px solid red;
    /* 调试边框 */
}
</style>