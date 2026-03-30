<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <p>路径计算中，请稍候...</p>
    <!-- <p class="debug-info">调试信息：组件已加载</p> -->
  </div>
</template>

<script>
export default {
  name: 'Loading',
};
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.7); /* 深色半透明背景，便于调试 */
  padding: 20px;
  border-radius: 8px;
  font-size: 22px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #ffffff;
  border-top: 5px solid #3498db; /* 蓝色高对比度，便于观察 */
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.debug-info {
  font-size: 12px;
  color: #ffcc00; /* 黄色调试信息，易于区分 */
}
</style>