<template>
    <div class="container">
        <!-- 上方Logo Start -->
        <div class="logo">
            <img :src="logoSrc" alt="logo" />
            <span>BUPT</span>
        </div>
        <!-- 上方Logo End -->

        <!-- 聊天选项卡 Start -->
        <div class="chats">
            <div class="chats-header">
                <span>{{ $t('AppAside.chat_header_title') }}</span>
                <el-icon class="header-icon" @click="startNewSession">
                    <Plus />
                </el-icon>
            </div>
            <div class="session flex" v-for="x in sessionList" :key="x.sessionId" :class="{ active: x.sessionId === active }"
                @click="pickTab(x.sessionId)">
                <div class="title">
                    <span>{{ x.title }}</span>
                    <div class="btn-box" v-if="x.sessionId === active">
                        <svg @click.stop="delTab(x.sessionId)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                            width="16" height="16" fill="none">
                            <path
                                d="M19.5 5.5L18.8803 15.5251C18.7219 18.0864 18.6428 19.3671 18.0008 20.2879C17.6833 20.7431 17.2747 21.1273 16.8007 21.416C15.8421 22 14.559 22 11.9927 22C9.42312 22 8.1383 22 7.17905 21.4149C6.7048 21.1257 6.296 20.7408 5.97868 20.2848C5.33688 19.3626 5.25945 18.0801 5.10461 15.5152L4.5 5.5"
                                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                            <path
                                d="M3 5.5H21M16.0557 5.5L15.3731 4.09173C14.9196 3.15626 14.6928 2.68852 14.3017 2.39681C14.215 2.3321 14.1231 2.27454 14.027 2.2247C13.5939 2 13.0741 2 12.0345 2C10.9688 2 10.436 2 9.99568 2.23412C9.8981 2.28601 9.80498 2.3459 9.71729 2.41317C9.32164 2.7167 9.10063 3.20155 8.65861 4.17126L8.05292 5.5"
                                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                            <path d="M9.5 16.5L9.5 10.5" stroke="currentColor" stroke-width="1.5"
                                stroke-linecap="round" />
                            <path d="M14.5 16.5L14.5 10.5" stroke="currentColor" stroke-width="1.5"
                                stroke-linecap="round" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>
        <!-- 聊天选项卡 End -->

        <!-- 工具栏 Start -->
        <div class="optionBar">
            <div class="options">
                <div class="option" @click="goToDialog('/setting')">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path
                            d="M15.5 11.5C15.5 13.433 13.933 15 12 15C10.067 15 8.5 13.433 8.5 11.5C8.5 9.567 10.067 8 12 8C13.933 8 15.5 9.567 15.5 11.5Z"
                            stroke="currentColor" stroke-width="1.5" />
                        <path
                            d="M21 13.5995C21.3155 13.5134 21.6503 13.4669 22 13.4669V9.53324C19.1433 9.53324 17.2857 6.43041 18.732 3.96691L15.2679 2.0001C13.8038 4.49405 10.1978 4.49395 8.73363 2L5.26953 3.96681C6.71586 6.43035 4.85673 9.53324 2 9.53324V13.4669C4.85668 13.4669 6.71425 16.5697 5.26795 19.0332L8.73205 21C9.46434 19.7527 10.7321 19.1289 12 19.1286"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path
                            d="M18.5 15L18.7579 15.697C19.0961 16.611 19.2652 17.068 19.5986 17.4014C19.932 17.7348 20.389 17.9039 21.303 18.2421L22 18.5L21.303 18.7579C20.389 19.0961 19.932 19.2652 19.5986 19.5986C19.2652 19.932 19.0961 20.389 18.7579 21.303L18.5 22L18.2421 21.303C17.9039 20.389 17.7348 19.932 17.4014 19.5986C17.068 19.2652 16.611 19.0961 15.697 18.7579L15 18.5L15.697 18.2421C16.611 17.9039 17.068 17.7348 17.4014 17.4014C17.7348 17.068 17.9039 16.611 18.2421 15.697L18.5 15Z"
                            stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
                    </svg>
                    <div class="option-text">设置</div>
                </div>
                <div class="divider">
                    <div class="border"></div>
                </div>
                <div class="option" @click="goToPage('/admin/users')" v-if="isAdmin">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12Z"
                            stroke="currentColor" stroke-width="1.5" />
                        <path d="M18 20V18C18 16.93 17.55 15.95 16.83 15.21L15.46 14.21C14.76 13.65 14 13.38 13.21 13.38H10.79C10 13.38 9.24 13.65 8.54 14.21L7.17 15.21C6.45 15.95 6 16.93 6 18V20"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        <path d="M6 10C6 11.66 7.34 13 9 13H15C16.66 13 18 11.66 18 10V9H6V10Z"
                            stroke="currentColor" stroke-width="1.5" />
                        <path d="M2 20H22"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                    <div class="option-text">用户管理</div>
                </div>
                <div class="option" @click="goToPage('/admin/tasks')">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        <path d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5C15 6.10457 14.1046 7 13 7H11C9.89543 7 9 6.10457 9 5Z"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        <path d="M9 12H15M9 16H12"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                    <div class="option-text">任务管理</div>
                </div>
                <div class="divider" v-if="isAdmin">
                    <div class="border"></div>
                </div>
                <div class="option" @click="handleLogout">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M16 17L21 12L16 7"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M21 12H9"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="option-text">注销</div>
                </div>
                <!-- <div class="option" @click="goToPage('/docs')">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path
                            d="M12 11.5C12.4955 11.5 12.9562 11.3015 13.8775 10.9045L14.5423 10.618C16.1808 9.91202 17 9.55902 17 9C17 8.44098 16.1808 8.08798 14.5423 7.38197L13.8775 7.09549C12.9562 6.6985 12.4955 6.5 12 6.5C11.5045 6.5 11.0438 6.6985 10.1225 7.09549L9.45768 7.38197C7.81923 8.08798 7 8.44098 7 9C7 9.55902 7.81923 9.91202 9.45768 10.618L10.1225 10.9045C11.0438 11.3015 11.5045 11.5 12 11.5ZM12 11.5V17.5"
                            stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
                        <path
                            d="M17 9V15C17 15.559 16.1808 15.912 14.5423 16.618L13.8775 16.9045C12.9562 17.3015 12.4955 17.5 12 17.5C11.5045 17.5 11.0438 17.3015 10.1225 16.9045L9.45768 16.618C7.81923 15.912 7 15.559 7 15V9"
                            stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
                        <path
                            d="M9.14426 2.5C6.48724 2.56075 4.93529 2.81456 3.87493 3.87493C2.81456 4.93529 2.56075 6.48724 2.5 9.14426M14.8557 2.5C17.5128 2.56075 19.0647 2.81456 20.1251 3.87493C21.1854 4.93529 21.4392 6.48724 21.5 9.14426M14.8557 21.5C17.5128 21.4392 19.0647 21.1854 20.1251 20.1251C21.1854 19.0647 21.4392 17.5128 21.5 14.8557M9.14426 21.5C6.48724 21.4392 4.93529 21.1854 3.87493 20.1251C2.81456 19.0647 2.56075 17.5128 2.5 14.8557"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="option-text">{{ $t('AppAside.tool_docs_name') }}</div>
                </div>
                <div class="divider">
                    <div class="border"></div>
                </div>
                <div class="option" @click="goToDialog('/about')">
                    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                        fill="none">
                        <path
                            d="M2.5 16.5C2.5 17.4293 2.5 17.894 2.57686 18.2804C2.89249 19.8671 4.13288 21.1075 5.71964 21.4231C6.10603 21.5 6.57069 21.5 7.5 21.5M21.5 16.5C21.5 17.4293 21.5 17.894 21.4231 18.2804C21.1075 19.8671 19.8671 21.1075 18.2804 21.4231C17.894 21.5 17.4293 21.5 16.5 21.5M21.5 7.5C21.5 6.57069 21.5 6.10603 21.4231 5.71964C21.1075 4.13288 19.8671 2.89249 18.2804 2.57686C17.894 2.5 17.4293 2.5 16.5 2.5M2.5 7.5C2.5 6.57069 2.5 6.10603 2.57686 5.71964C2.89249 4.13288 4.13288 2.89249 5.71964 2.57686C6.10603 2.5 6.57069 2.5 7.5 2.5"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path
                            d="M12 8.5V6.5M10 11.5V12M14 11.5V12M11 8.5H13C14.8856 8.5 15.8284 8.5 16.4142 9.08579C17 9.67157 17 10.6144 17 12.5V12.5C17 14.3856 17 15.3284 16.4142 15.9142C15.8284 16.5 14.8856 16.5 13 16.5H11C9.11438 16.5 8.17157 16.5 7.58579 15.9142C7 15.3284 7 14.3856 7 12.5V12.5C7 10.6144 7 9.67157 7.58579 9.08579C8.17157 8.5 9.11438 8.5 11 8.5Z"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="option-text">{{ $t('AppAside.tool_about_name') }}</div>
                </div> -->
            </div>
        </div>
        <!-- 工具栏 End -->

        <!-- 自定义弹窗 -->
        <CustomDialog
            v-model="dialogVisible"
            :title="dialogTitle"
        >
            <component :is="currentComponent"></component>
        </CustomDialog>
    </div>
</template>

<script>
import Setting from './setting/index.vue'
import About from './about/index.vue'
import logoDark from '../assets/images/logo_dark_2480.png'
import logoLight from '../assets/images/logo_light_2480.png'

export default {
    name: 'AppAside',
    components: {
        Setting,
        About
    },
    data() {
        return {
            isCollapsed: false,
            dialogVisible: false,
            dialogTitle: '',
            currentComponent: null
        }
    },
    computed: {
        active: {
            get() {
                return this.$store.state.chat.active;
            },
            set(val) {
                this.$store.dispatch('setActive', val);
            }
        },
        sessionList() {
            return this.$store.state.chat.chat.list;
        },
        logoSrc() {
            const theme = this.$store.state.setting.theme
            return theme === 'dark' ? logoLight : logoDark
        },
        isAdmin() {
            return this.$store.state.user?.userInfo?.role === 'admin'
        }
    },
    methods: {
        /**
         * 删除历史聊天选项卡
         * @param uuid 要删除的选项卡uuid
         */
        async delTab(uuid) {
            // 获取 session 列表
            const sessions = this.$store.state.chat.chat.list;
            const idx = sessions.findIndex(s => s.sessionId === uuid);
            // 计算前一个 session 的 uuid
            let nextActive = '';
            if (sessions.length > 1) {
                const newIdx = idx === 0 ? 1 : idx - 1;
                nextActive = sessions[newIdx].sessionId;
            }
            // 删除会话（调用 store action，会同步删除 MySQL 数据）
            await this.$store.dispatch('deleteSession', uuid);
            // 更新 active
            this.active = nextActive;
        },

        /**
         * 选择聊天选项卡
         * @param uuid
         */
        pickTab(uuid) {
            // 判断当前是否为聊天页面 如果不是那么跳转到聊天页
            if (this.$router.currentRoute.value.name !== 'index') {
                this.goToPage('/');
            }
            // 更新active
            console.log("uuid",uuid)
            this.active = uuid;
            // 在手机模式下,触发收起侧边栏
            if (this.isMobileDevice()) {
                this.$emit('toggle-sidebar');
            }
        },

        /**
         * 新页面
         */
        isMobileDevice() {
            return window.innerWidth <= 767;
        },

        /**
         * 开始新的会话
         */
        async startNewSession() {
            // 判断当前是否为聊天页面 如果不是那么跳转到聊天页
            if (this.$router.currentRoute.value.name !== 'index') {
                this.goToPage('/');
            }
            // 创建新会话
            const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            try {
                await this.$store.dispatch('createSession', {
                    sessionId,
                    title: '新会话'
                });
            } catch (error) {
                console.error('创建会话失败:', error);
            }

            // 在手机模式下,触发收起侧边栏
            if (this.isMobileDevice()) {
                this.$emit('toggle-sidebar');
            }
        },

        /**
         * 跳转页面函数
         * @param path
         */
        goToPage(path) {
            // 在手机模式下,触发收起侧边栏
            if (this.isMobileDevice()) {
                this.$emit('toggle-sidebar');
            }
            this.$router.push(path)
        },

        /**
         * 跳转弹窗函数
         * @param path
         */
        goToDialog(path) {
            const componentMap = {
                '/setting': {
                    component: 'Setting',
                    title: this.$t('AppAside.tool_setting_name')
                },
                '/about': {
                    component: 'About',
                    title: this.$t('AppAside.tool_about_name') + ' - 本页面暂不配置多语言'
                }
            }

            if (componentMap[path]) {
                // 在手机模式下,触发收起侧边栏
                if (this.isMobileDevice()) {
                    this.$emit('toggle-sidebar');
                }
                this.dialogTitle = componentMap[path].title
                this.currentComponent = componentMap[path].component
                this.dialogVisible = true
            } else {
                this.goToPage(path)
            }
        },

        /**
         * 退出登录
         */
        handleLogout() {
            // Clear all user-related data
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_info')
            // Redirect to login with hash and reload
            window.location.hash = '#/login'
            setTimeout(() => {
                window.location.reload()
            }, 100)
        }
    }
}
</script>

<style lang="scss" scoped>
/**
 * 变量定义
 */
$animation-time: 0.3s;

/**
 * 通用的hover和active效果定义
 */
@mixin hover-active-effect {

    &.active,
    &:hover {
        background: var(--aside-active-hover-bg);
        border-radius: 10px;
    }
}

/**
 * 容器样式
 */
.container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/**
 * 上方Logo
 */
.logo {
    display: flex;
    align-items: center;
    padding: 20px;

    img {
        height: 35px;
        margin-right: 10px;
        border-radius: 5px;
    }

    span {
        font-size: 18px;
    }
}

/**
 * 聊天选项卡
 */
.chats {
    font-size: 14px;
    flex: 1;
    padding: 2px;
    overflow-y: auto;
    scrollbar-width: none;
    width: 240px;

    &::-webkit-scrollbar {
        display: none;
    }

    &-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px;

        span {
            font-size: 12px;
            color: var(--answer-stats-color);
        }

        .header-icon {
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;

            &:hover {
                background-color: var(--aside-active-hover-bg);
            }
        }
    }

    .session {
        padding: 10px 6px 10px 10px;
        margin-bottom: 2px;
        cursor: pointer;

        @include hover-active-effect;

        .title {
            width: 220px;
            display: flex;
            justify-content: space-between;
            align-items: center;

            span {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                flex: 1;
            }

            .btn-box {
                margin-left: 8px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                border-radius: 4px;

                &:hover {
                    color: var(--el-color-primary);
                }
            }
        }
    }
}

/**
 * 工具栏
 */
.optionBar {
    width: 100%;
    border-top: 1px solid var(--app-small-border-color);
    padding: 6px 0;

    .options {
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
        transition: width $animation-time ease;

        .option {
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 8px 16px;
            gap: 8px;
            flex: 0 0 calc(50% - 8px);

            &:hover {
                @include hover-active-effect;
            }

            .icon {
                width: 20px;
                height: 20px;
                flex-shrink: 0;
            }

            .option-text {
                font-size: 13px;
                font-weight: 600;
                line-height: 16px;
                white-space: nowrap;
            }
        }

        .divider {
            display: none;
        }
    }
}

/**
 * 弹窗
 */
:global(.el-dialog) {
    border-radius: 15px;
    background: var(--layout-common-layout-bg);
    overflow: hidden;
    position: relative;
    max-width: 600px;
    min-width: 300px;
    margin: 15vh auto !important;
    max-height: 70vh;
    display: flex;
    flex-direction: column;
}

:global(.el-dialog::after) {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 110%;
    height: 110%;
    z-index: 1;
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    pointer-events: none;
}

:global(.el-dialog__header),
:global(.el-dialog__body) {
    position: relative;
    z-index: 2;
}

:global(.el-dialog__body) {
    flex: 1;
    overflow-y: auto;
    scrollbar-width: none;
}

@media screen and (max-width: 768px) {
    :global(.el-dialog) {
        width: 95% !important;
    }
}

@media screen and (min-width: 1200px) {
    :global(.el-dialog) {
        width: 60% !important;
    }
}
</style>