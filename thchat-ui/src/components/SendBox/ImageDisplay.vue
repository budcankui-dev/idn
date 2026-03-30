<template>
    <div class="image-container">
      <img src="@/assets/images/test.png" alt="Test Image" class="display-image" />
      <p class="debug-info">调试：图片生成成功</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ImageDisplay',
  };
  </script>
  
  <style scoped>
  .image-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    background: rgba(0, 0, 0, 0.8); /* 与 loading.vue 相同的灰暗背景 */
    padding: 20px;
    border-radius: 8px;
    border: 2px solid yellow; /* 调试边框，保持与 loading.vue 一致 */
  }
  
  .display-image {
    max-width: 80vw; /* 限制图片宽度，防止溢出 */
    max-height: 80vh; /* 限制图片高度 */
    object-fit: contain; /* 保持图片比例 */
  }
  
  .debug-info {
    font-size: 12px;
    color: #00ff00; /* 绿色调试信息，与 loading.vue 一致 */
  }
  </style>