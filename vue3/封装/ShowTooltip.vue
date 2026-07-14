<script setup name="ShowTooltip">
import { isEmpty } from '@/util'
import { useThrottleFn } from '@vueuse/core'
const props = defineProps({
  content: {
    type: [String, Number]
  },
  effect: {
    type: String,
    default: 'dark'
  },
  placement: {
    type: String,
    default: 'top-start'
  }
})
const visible = ref(true)
const contentDom = ref(null)
const getVisible = () => {
  const offsetWidth = contentDom.value?.offsetWidth
  const scrollWidth = contentDom.value?.scrollWidth
  visible.value = offsetWidth < scrollWidth
}
const throttledFn = useThrottleFn(() => {
  getVisible()
}, 1000)

watch(() => props.content, newValue => {
  if (!newValue) return
  nextTick(() => {
    throttledFn()
    getVisible()
  })
}, {
  immediate: true
})
let initTimer = null
let resizeObserver = null
onMounted(() => {
  window.addEventListener('resize', throttledFn)
  initTimer = setTimeout(() => {
    getVisible()
  }, 300)
  if (window.ResizeObserver && contentDom.value) {
    resizeObserver = new ResizeObserver(() => {
      getVisible()
    })
    resizeObserver.observe(contentDom.value)
  }
})
onActivated(() => {
  nextTick(() => {
    getVisible()
  })
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', throttledFn)
  if (initTimer) {
    clearTimeout(initTimer)
    initTimer = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

</script>
<template>
  <div
    class="m-tooltip"
    :class="{ 'active': visible }"
  >
    <el-tooltip
      v-if="visible"
      :effect="props.effect"
      :content="isEmpty(props.content)"
      :placement="props.placement"
    >
      <div
        class="content"
        ref="contentDom"
      >{{ isEmpty(props.content) }}</div>
    </el-tooltip>
    <div
      v-else
      class="content"
      ref="contentDom"
    >{{ isEmpty(props.content) }}</div>
  </div>
</template>

<style lang="scss" scoped>
.m-tooltip {
  position: relative;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  padding-right: 5px;

  &.active {
    cursor: pointer;
  }

  .content {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    width: 100%;
  }

  .tooltip {
    position: absolute;
    top: -50px;
    padding: 4px 8px;
    background: #ccc;
    border-radius: 6px;
    z-index: 999;
  }

  &.align-center {
    .content {
      text-align: center;
    }
  }
}
</style>
