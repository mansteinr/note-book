```
<template>
    <div
      class="scroll-container"
      ref="containerRef"
      @mouseenter="pauseScroll"
      @mouseleave="resumeScroll"
    >
      <div class="scroll-wrapper">
        <div
          class="scroll-content"
          :style="{ animationPlayState: isPaused ? 'paused' : 'running' }"
        >
          <div
            v-for="(item, index) in tableRawData"
            :key="item.city"
            class="scroll-item"
          >
            <div class="color-00f4df italic">{{ item.city }}</div>
            <div>{{ item.idcIncome }}</div>
            <div>{{ item.idcExpend }}</div>
            <div>{{ item.manIncome }}</div>
            <div>{{ item.manExpend }}</div>
          </div>
          <!-- 复制一份实现无缝 -->
          <div
            v-for="(item, index) in tableRawData"
            :key="'copy-' + item.city"
            class="scroll-item"
          >
            <div class="color-00f4df italic">{{ item.city }}</div>
            <div>{{ item.idcIncome }}</div>
            <div>{{ item.idcExpend }}</div>
            <div>{{ item.manIncome }}</div>
            <div>{{ item.manExpend }}</div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
const duration = '20s'
const isPaused = ref(false)
const tableRawData = ref([{"manIncome":"536.32","city":"杭州市","manExpend":"603.45","idcExpend":"643.38","idcIncome":"511.63"},{"manIncome":"330.41","city":"宁波市","manExpend":"305.70","idcExpend":"828.84","idcIncome":"401.97"},{"manIncome":"220.68","city":"温州市","manExpend":"330.66","idcExpend":"666.39","idcIncome":"286.66"},{"manIncome":"421.59","city":"嘉兴市","manExpend":"209.74","idcExpend":"592.22","idcIncome":"338.24"},{"manIncome":"310.14","city":"湖州市","manExpend":"98.96","idcExpend":"407.64","idcIncome":"287.04"},{"manIncome":"211.37","city":"绍兴市","manExpend":"140.92","idcExpend":"264.72","idcIncome":"168.77"},{"manIncome":"304.51","city":"金华市","manExpend":"204.52","idcExpend":"610.84","idcIncome":"299.74"},{"manIncome":"29.06","city":"衢州市","manExpend":"74.63","idcExpend":"25.58","idcIncome":"31.14"},{"manIncome":"37.67","city":"丽水市","manExpend":"53.08","idcExpend":"24.66","idcIncome":"33.32"},{"manIncome":"358.88","city":"台州市","manExpend":"231.36","idcExpend":"622.89","idcIncome":"329.73"},{"manIncome":"82.38","city":"舟山市","manExpend":"36.98","idcExpend":"94.43","idcIncome":"48.94"}])

const pauseScroll = () => {
  isPaused.value = true
}

const resumeScroll = () => {
  isPaused.value = false
}



</script>

<style scoped>
@keyframes scroll-up {
  0% {
    transform: translateY(0)
  }

  100% {
    transform: translateY(-50%)
  }
}

  .italic {
    font-style: italic;
    font-family: SourceHanSansCN-Regular;
  }

  .linear-gradient {
    background-image: linear-gradient(to right, rgba(76, 181, 218, 0), rgba(76, 181, 218, .2), rgba(76, 181, 218, 0));
  }
  .scroll-container {
    height: 260px;
    overflow: hidden;
    position: relative;

    .scroll-wrapper {
      position: absolute;
      width: 100%;

      .scroll-item {
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 40px;
        line-height: 40px;
        box-sizing: border-box;
        font-size: 16px;

        &:nth-child(even) {
          background-image: linear-gradient(to right, rgba(76, 181, 218, 0), rgba(76, 181, 218, 0.2), rgba(76, 181, 218, 0))
        }

        div {
          flex: 1.5;
          text-align: center;

          &:first-child {
            flex: 1
          }
        }
      }
    }

    .scroll-content {
      animation: scroll-up v-bind('duration') linear infinite;
      transform: translateZ(0);
    }
  }
</style>

```