<template>
    <div class="json-viewer">
      <!-- JSON 内容 间距-->
      <div v-for="(line, index) in formattedJson" :key="index" class="json-line" :style="{ paddingLeft: `${line.depth * 26}px` }">
        <span class="line-number">{{ index + 1 }}</span>
        <span class="json-content">
          <!-- 折叠/展开图标 -->
          <span v-if="line.isCollapsible" class="collapse-icon" @click="toggleCollapse(line.fullKey)">
            <svg v-if="collapsed[line.fullKey]" xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </span>
          <!-- 类型图标 -->
          <span v-if="line.isObject || line.isArray" class="type-icon">
            <svg v-if="line.isObject" xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-if="line.isArray" xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 12h10M7 17h10" />
            </svg>
          </span>
          <!-- 键/值 -->
          <span class="json-key" v-if="line.key !== null">{{ line.key }}:</span>
          <span class="json-value" :class="getValueClass(line.value)">
            <span v-if="line.isCollapsible && collapsed[line.fullKey]">
              {{ line.isObject ? '{...}' : '[...]' }}
            </span>
            <span v-else-if="line.isCollapsible && !collapsed[line.fullKey]">
              {{ line.isObject ? '{' : '[' }}
            </span>
            <span v-else-if="line.isCollapsibleEnd">
              {{ line.isObject ? '}' : ']' }}
            </span>
            <span v-else>
              {{ formatValue(line.value) }}
            </span>
          </span>
        </span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  
  // Props
  const props = defineProps({
    jsonData: {
      type: [Object, Array],
      required: true,
    },
  });
  
  // 折叠状态
  const collapsed = ref({});
  
  // 设置默认折叠状态（只展开一级）
  const setDefaultCollapse = (data, parentKey = 'root', depth = 0) => {
    if (Array.isArray(data) && data.length > 0) {
      collapsed.value[parentKey] = depth > 0; // 仅在 depth > 0 时折叠
      if (!collapsed.value[parentKey]) {
        data.forEach((item, index) => {
          if (typeof item === 'object' && item !== null) {
            setDefaultCollapse(item, `${parentKey}[${index}]`, depth + 1);
          }
        });
      }
    } else if (typeof data === 'object' && data !== null && Object.keys(data).length > 0) {
      collapsed.value[parentKey] = depth > 0; // 仅在 depth > 0 时折叠
      if (!collapsed.value[parentKey]) {
        Object.entries(data).forEach(([key, value]) => {
          if (typeof value === 'object' && value !== null) {
            setDefaultCollapse(value, parentKey ? `${parentKey}.${key}` : key, depth + 1);
          }
        });
      }
    }
  };
  
  // 初始化时默认只展开一级
  onMounted(() => {
    setDefaultCollapse(props.jsonData);
  });
  
  // 切换折叠状态
  const toggleCollapse = (fullKey) => {
    collapsed.value[fullKey] = !collapsed.value[fullKey];
  };
  
  // 格式化 JSON 为行
  const formattedJson = computed(() => {
    const lines = [];
    let lineNumber = 1;
  
    const parseJson = (data, depth = 0, parentKey = '', keyName = null) => {
      const fullKey = parentKey ? `${parentKey}.${keyName || depth}` : keyName || 'root';
  
      if (Array.isArray(data)) {
        // 开始数组
        lines.push({
          key: keyName,
          value: data,
          isArray: true,
          isObject: false,
          isCollapsible: data.length > 0,
          isCollapsed: collapsed.value[fullKey],
          isCollapsibleEnd: false,
          depth,
          lineNumber: lineNumber++,
          fullKey,
        });
        if (!collapsed.value[fullKey]) {
          data.forEach((item, index) => {
            const childKey = `${fullKey}[${index}]`;
            if (typeof item === 'object' && item !== null) {
              parseJson(item, depth + 1, fullKey, `[${index}]`);
            } else {
              lines.push({
                key: `[${index}]`,
                value: item,
                isArray: false,
                isObject: false,
                isCollapsible: false,
                isCollapsed: false,
                isCollapsibleEnd: false,
                depth: depth + 1,
                lineNumber: lineNumber++,
                fullKey: childKey,
              });
            }
          });
          // 结束数组
          lines.push({
            key: null,
            value: data,
            isArray: true,
            isObject: false,
            isCollapsible: false,
            isCollapsed: false,
            isCollapsibleEnd: true,
            depth,
            lineNumber: lineNumber++,
            fullKey,
          });
        }
      } else if (typeof data === 'object' && data !== null) {
        // 开始对象
        lines.push({
          key: keyName,
          value: data,
          isArray: false,
          isObject: true,
          isCollapsible: Object.keys(data).length > 0,
          isCollapsed: collapsed.value[fullKey],
          isCollapsibleEnd: false,
          depth,
          lineNumber: lineNumber++,
          fullKey,
        });
        if (!collapsed.value[fullKey]) {
          Object.entries(data).forEach(([key, value]) => {
            const childKey = parentKey ? `${fullKey}.${key}` : key;
            if (typeof value === 'object' && value !== null) {
              parseJson(value, depth + 1, fullKey, key);
            } else {
              lines.push({
                key,
                value,
                isArray: false,
                isObject: false,
                isCollapsible: false,
                isCollapsed: false,
                isCollapsibleEnd: false,
                depth: depth + 1,
                lineNumber: lineNumber++,
                fullKey: childKey,
              });
            }
          });
          // 结束对象
          lines.push({
            key: null,
            value: data,
            isArray: false,
            isObject: true,
            isCollapsible: false,
            isCollapsed: false,
            isCollapsibleEnd: true,
            depth,
            lineNumber: lineNumber++,
            fullKey,
          });
        }
      } else {
        lines.push({
          key: keyName,
          value: data,
          isArray: false,
          isObject: false,
          isCollapsible: false,
          isCollapsed: false,
          isCollapsibleEnd: false,
          depth,
          lineNumber: lineNumber++,
          fullKey,
        });
      }
    };
  
    // 处理根节点（可能是对象或数组）
    if (Array.isArray(props.jsonData)) {
      parseJson(props.jsonData, 0, '', null);
    } else if (typeof props.jsonData === 'object' && props.jsonData !== null) {
      parseJson(props.jsonData, 0, '', null);
    }
  
    return lines;
  });
  
  // 格式化值
  const formatValue = (value) => {
    if (value === null) return 'null';
    if (typeof value === 'string') return `"${value}"`;
    return String(value);
  };
  
  // 根据值类型设置类
  const getValueClass = (value) => ({
    'json-string': typeof value === 'string',
    'json-number': typeof value === 'number',
    'json-boolean': typeof value === 'boolean',
    'json-null': value === null,
    'json-object': typeof value === 'object' && value !== null,
  });
  </script>
  
  <style scoped>
  .json-viewer {
    font-family: monospace;
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 8px;
    max-height: 80vh;
    overflow: auto;
    font-size: 28px; /* 默认增大到 16px，你可以根据需要调整 */
    /* 若需调整字体大小，请修改这里的 font-size，例如：
       font-size: 14px;  // 较小
       font-size: 18px;  // 较大
    */
    /* 隐藏滚动条但保持滚动功能 */
    /* Firefox */
    scrollbar-width: none;
    /* Chrome, Safari, Edge */
    &::-webkit-scrollbar {
      display: none;
    }
  }
  
  .json-line {
    display: flex;
    align-items: flex-start;
    line-height: 1.5;
  }
  
  .line-number {
    width: 40px;
    text-align: right;
    color: #6e7681;
    margin-right: 8px;
    user-select: none;
  }
  
  .json-content {
    display: flex;
    align-items: flex-start;
    flex: 1;
  }
  
  .collapse-icon {
    cursor: pointer;
    margin-right: 4px;
    width: 16px;
    height: 16px;
  }
  
  .type-icon {
    margin-right: 4px;
    width: 16px;
    height: 16px;
  }
  
  .icon {
    width: 16px;
    height: 16px;
    stroke: #d4d4d4;
  }
  
  .json-key {
    color: #c792ea; /* 紫色键 */
    margin-right: 4px;
  }
  
  .json-value {
    color: #d4d4d4;
  }
  
  .json-string {
    color: #a5d6a7; /* 绿色字符串 */
  }
  
  .json-number {
    color: #f9c2ff; /* 粉色数字 */
  }
  
  .json-boolean {
    color: #82aaff; /* 蓝色布尔值 */
  }
  
  .json-null {
    color: #ffcb6b; /* 黄色 null */
  }
  
  .json-object {
    color: #d4d4d4;
  }
  </style>