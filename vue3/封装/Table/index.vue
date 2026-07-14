<template>
  <div
    :class="`${bem.b()} table-wrapper ${isNeedPage ? '' : 'no-pagination'} ${isShowSummary ? 'summary-table' : ''} `">
    <!-- <div :class="`${border ? 'bordertable' : ''}`" style="width: 100%"> -->
    <div
      class="table-wrapper__content"
      :class="{
        bordertable: border,
      }"
    >
      <div
        v-if="Object.keys($slots).length"
        style="display: flex; margin: 0 0 6px; align-items: center;"
      >
        <div
          v-if="title && !border"
          :class="`${titleClass} table-title`"
        >
          <slot name="title">{{ title }}</slot>
        </div>
        <div
          v-if="title"
          style="margin-left: auto;"
        >
          <slot name="titleOperateTool" />
        </div>
        <div
          v-else
          style="width: 100%;"
          class="table-title-tool"
        >
          <slot name="titleOperateTool" />
        </div>
      </div>
      <el-table
        ref="tableRef"
        v-bind="$attrs"
        :border="true"
        :data="tableData"
        :span-method="spanMethod"
        :show-summary="isShowSummary"
        :show-overflow-tooltip="true"
        :row-class-name="rowClassName"
        :summary-method="getSummaries"
        :cell-class-name="cellClassName"
        :tooltip-options="tooltipOptions"
        :header-cell-style="setCellStyle"
        :row-key="rowKey"
        @cell-click="cellClick"
        @sort-change="handlesortChange"
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty
            v-if="emptyIcon"
            :description="emptyText"
          />
          <span v-else>{{ emptyText }}</span>
        </template>
        <slot name="start" />
        <el-table-column
          v-if="localSelection"
          type="selection"
          :reserve-selection="reserveSelection"
        />
        <el-table-column
          v-if="special"
          prop="expand"
          width="50px"
        >
          <template #header>
            <div
              class="changeExpand expand"
              @click="expandAll(scope)"
            >
              <el-icon class="icon  ">
                <svg-icon name="bExpand" />
              </el-icon>
            </div>
          </template>
          <template #default="scope">
            <div
              class="changeExpand expand"
              @click="changeExpand(scope)"
            >
              <el-icon class="icon ">
                <svg-icon name="Expand" />
              </el-icon>
            </div>
          </template>
        </el-table-column>
        <template
          v-for="column in computedColumns"
          :key="column.prop"
        >
          <el-table-column
            v-if="column.type == 'index'"
            :type="column.type"
            :width="column.width"
            v-bind="{ ...$attrs, ...column }"
            :class-name="column.className || column.prop"
          />
          <el-table-column
            v-else-if="column.prop === 'settingIcon'"
            :type="column.type"
            :width="column.width"
            v-bind="{ ...$attrs, ...column }"
            :class-name="column.className || column.prop"
          >
            <template #header>
              <el-popover
                trigger="click"
                placement="left-start"
                popper-class="filter-column-popover"
              >
                <template #reference>
                  <el-icon>
                    <Setting />
                  </el-icon>
                </template>
                <el-tree
                  ref="treeRef"
                  node-key="prop"
                  show-checkbox
                  :props="{
                    id: 'prop',
                    label: data => formatterLabel(data),
                    children: 'children'
                  }"
                  :data="columnsList"
                  default-expand-all
                  check-on-click-node
                  :default-checked-keys="checkList"
                  @check="columnsChange"
                />
              </el-popover>
            </template>
          </el-table-column>
          <TableColumn
            v-else
            :key="column.prop"
            :column="{ ...$attrs, ...column, special }"
          >
            <template
              v-for="slot in Object.keys($slots)"
              #[slot]="scope"
            >
              <slot
                :name="slot"
                v-bind="scope"
              />
            </template>
          </TableColumn>
        </template>
        <template
          v-if="hasMore"
          #append
        >
          <div
            v-loading="true"
            class="load-more-btn"
          />
        </template>
      </el-table>
    </div>
    <el-pagination
      v-if="isNeedPage && isDynamicNeedPage"
      v-model:page-size="opt.pageSize"
      v-model:current-page="opt.pageNum"
      :total="total"
      :layout="layout"
      :page-sizes="pageSizes"
      :background="background"
      :key="isDynamicNeedPage"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>
<script setup name="EcsTable2">
import { isEmptyNULL } from '@/util'
import { ref, computed, watch } from 'vue'
import TableColumn from './TableColumn.vue'
import ShowTooltip from '@/components/ShowTooltip/index.vue'
import { createNamespace } from '@trendy/ecs-plus/utils/create'
import { formatterTable, expandAll, changeExpand } from './tableUtil'
// 是否构建表头
const bem = createNamespace('table')
const tableRef = ref(null)
const checkList = ref([])
const columnsList = ref([])
// table添加key 防止排序高亮一些问题
const { proxy } = getCurrentInstance()
const props = defineProps({
  total: {
    type: Number,
    default: 0
  },
  background: {
    type: Boolean,
    default: true
  },
  emptyIcon: {
    type: Boolean,
    default: true
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  title: {
    type: String,
    default: ''
  },
  rowClassName: {
    type: String,
    default: ''
  },
  cellClassName: {
    type: String,
    default: ''
  },
  hideOnSinglePage: {
    type: Boolean,
    default: false
  },
  border: {
    type: Boolean,
    default: false
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  columns: {
    type: Array,
    default: () => []
  },
  layout: {
    type: String,
    default: '->,total, sizes, prev, pager, next, jumper'
  },
  isNeedPage: {
    type: Boolean,
    default: false
  },
  isDynamicNeedPage: {
    type: Boolean,
    default: true
  },
  isNeedSetting: {
    type: Boolean,
    default: true
  },
  isNeedNumber: {
    type: Boolean,
    default: true
  },
  isOperate: {
    type: Boolean,
    default: false
  },
  spanMethod: {
    type: Function
  },
  notShowSummary: {
    type: Boolean,
    default: false
  },
  rawData: {
    type: Object,
    default: () => { }
  },
  widthMap: {
    type: Object,
    default: () => { }
  },
  operateFixed: {
    type: Boolean,
    default: false
  },
  titleClass: {
    type: String,
    default: ''
  },
  serialLabel: {
    type: String,
    default: '编号'
  },
  special: {
    type: Boolean,
    default: false
  },
  sidePagination: {
    type: String,
    default: 'service' // customer 前端分页 rollPagination 前端滚动分页 roll 后端滚动加载
  },
  // 是否是大模型
  isGpt: {
    type: Boolean,
    default: false
  },
  // 是否是虚拟渲染
  // isVirturalTable: {
  //   type: Boolean,
  //   default: false
  // },
  tooltipOptions: {
    type: Object,
    default: () => ({
      // offset: 50,
      placement: 'left',
      popperOptions: {
        modifiers: [
          {
            name: 'offset',
            options: {
              offset: [30, -30]
            }
          }
        ]
      }
    })
  },
  rowKey: {
    type: String,
    default: ''
  },
  reserveSelection: {
    type: Boolean,
    default: false
  },
  isSelection: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: 'auto'
  },
  maxHeight: {
    type: String,
    default: 'none'
  }
})
let timer = null
let timerMergeTable = null
const localTotal = ref(0)
const localColumns = ref(null)
const localShowSummary = ref(false)
const opt = ref({
  pageNum: 1,
  pageSize: 10,
  orderBy: '',
  orderType: ''
})

const setCellStyle = ({ column }) => {
  const orderBy = props.rawData.orderBy || opt.value.orderBy
  const orderType = props.rawData.orderType || opt.value.orderType
  if (column.sortable && column.property === orderBy && orderType) {
    column.order = orderType === 'desc' ? 'descending' : 'ascending'
  } else {
    column.order = ''
  }
}

const columnsNodeMap = new Map()
const flatMap = list => {
  if (list && list.length) {
    for (let i = 0; i < list.length; i++) {
      if (!list[i].prop || list[i].prop === 'settingIcon') continue
      // data[list[i].prop || list[i].label] = list[i]
      columnsNodeMap.set(list[i].prop || list[i].label, list[i])
      if (list[i].children?.length) {
        flatMap(list[i].children)
      }
    }
  }
}
const tableData = ref([])
let localResponseNodes = []
const localTableData = ref([])
const localSelection = ref(false)
const isNeedPage = ref(props.isNeedPage)
const computedColumns = computed(() => localColumns.value || [])
const total = computed(() => localTotal.value || props.total)
const isShowSummary = computed(() => props.notShowSummary ? false : localShowSummary.value)
const emit = defineEmits(['handleChange', 'handleSelectionChange', 'update:columns', 'update:totalData'])
const formatterLabel = ({ label }) => label.includes('_prefix_') ? label.replace('_prefix_', '/') : label

const hasMore = computed(() => {
  // 前端滚动加载
  if (props.sidePagination === 'rollPagination') {
    return localTableData.value.length > tableData.value.length
  } else if (props.sidePagination === 'roll') {
    return tableData.value.length < localTotal.value
  }
  return false
})
// 前端分页
const customerPage = () => {
  if (props.sidePagination === 'roll') {
    tableData.value = [...tableData.value, ...localTableData.value]
    return
  }
  const start = opt.value.pageSize * (opt.value.pageNum - 1)
  const end = Math.min(opt.value.pageSize * opt.value.pageNum, localTableData.value.length)
  tableData.value = localTableData.value.slice(props.sidePagination === 'rollPagination' ? 0 : start, end)
}
/** 切换分页 */
const handleSizeChange = val => {
  opt.value.pageNum = 1
  opt.value.pageSize = val
  const obj = {
    pageNum: opt.value.pageNum,
    pageSize: opt.value.pageSize
  }
  if (opt.value.orderBy) {
    obj.orderBy = opt.value.orderBy
    obj.orderType = opt.value.orderType
  }
  ['service', 'roll'].includes(props.sidePagination)
    ? emit('handleChange', obj)
    : customerPage()
}
/** 翻页 */
const handleCurrentChange = val => {
  opt.value.pageNum = val
  const obj = {
    pageNum: opt.value.pageNum,
    pageSize: opt.value.pageSize
  }
  if (opt.value.orderBy) {
    obj.orderBy = opt.value.orderBy
    obj.orderType = opt.value.orderType
  }
  ['service', 'roll'].includes(props.sidePagination)
    ? emit('handleChange', obj)
    : customerPage()
}
const handleSelectionChange = data => {
  emit('handleSelectionChange', data)
}

const toggleSelection = (ids, key, flag, callback) => {
  tableData.value.filter(v => ids.includes(v[key])).forEach(v => {
    tableRef.value.toggleRowSelection(v, flag)
  })
  nextTick(() => {
    callback()
    handleSelectionChange(getSelectionRows())
  })
}

const getSelectionRows = () => {
  return tableRef.value.getSelectionRows()
}

const clearSelection = () => {
  return tableRef.value.clearSelection()
}
const toggleRowSelection = (row, flag) => {
  tableRef.value.toggleRowSelection(row, flag)
}
let observer = null
let targetDom = null
watch(() => props.rawData, newValue => {
  if (!newValue) return
  if (observer) {
    targetDom && observer.unobserve(targetDom)
    observer.disconnect()
    observer = null
  }
  if (props.isGpt) {
    localColumns.value = (newValue?.columns || []).map(v => ({
      prop: v,
      label: v,
      minWidth: 100
    }))
    localTotal.value = 1000
    tableData.value = (newValue?.data || []).map(item => {
      const obj = item.reduce(prev => {
        localColumns.value.forEach((v, index) => {
          prev[v.prop] = item[index]
        })
        return prev
      }, {})
      return obj
    })
  } else {
    // 前端分页
    if (['customer'].includes(props.sidePagination)) {
      const { list } = newValue || {}
      localTotal.value = list?.length || 0
      localTableData.value = list || []
      isNeedPage.value = true
      localColumns.value = props.columns
      customerPage()
    } else {
      if (newValue.reportMetadata) {
        localShowSummary.value = !!newValue.responseData?.length
        emit('update:totalData', newValue.responseData)
        /** 数据报表
         * 数据报表的接口 表头和数据都是后台定义的
         * 所以table中处理相关的columns和tableData
         *
         * displayType tabulation 分页  noPageTabulation 不分页
         *
         */
        localTotal.value = newValue.pageData?.total || 0
        opt.value.pageNum = newValue.pageData?.pageNum || 1
        opt.value.pageSize = newValue.pageData?.pageSize || 10
        const { list, columns, responseNodes } = formatterTable(props, false, proxy.$attrs)
        localResponseNodes = responseNodes
        if (columns) {
          localColumns.value = columns
          emit('update:columns', columns)
        }
        if (['roll', 'rollPagination'].includes(props.sidePagination)) {
          isNeedPage.value = false
          localTableData.value = list
          customerPage()
        } else {
          tableData.value = list
          isNeedPage.value = newValue.reportMetadata.displayType == 'tabulation'
        }
        if (newValue.reportMetadata.isMultipleChoice === true) localSelection.value = true
        // 兜底处理 如果当前页面没有数据 并且不是第一页  应该取值前一页码 同事注意prePage是否为0
        if (props.sidePagination === 'service' && !list?.length && opt.value.pageNum !== 1 && newValue.pageData.prePage !== 0) {
          nextTick(() => {
            handleCurrentChange(1)
          })
        }
      } else {
        /** 非报表分页 */
        localColumns.value = props.columns
        const { total, list, pageNum, pageSize, prePage } = props.rawData || {}
        if (!(isEmptyNULL(pageNum) || isEmptyNULL(pageSize))) return []
        localTotal.value = total || 0
        opt.value.pageNum = pageNum
        opt.value.pageSize = pageSize
        if (['rollPagination'].includes(props.sidePagination)) {
          localTableData.value = list || []
          customerPage()
        } else {
          tableData.value = list || []
        }
        isNeedPage.value = props.sidePagination === 'service'
        localSelection.value = props.isSelection
        // 兜底处理 如果当前页面没有数据 并且不是第一页  应该取值前一页码 同事注意prePage是否为0
        if (props.sidePagination === 'service' && !list?.length && pageNum !== 1 && prePage !== 0) {
          nextTick(() => {
            handleCurrentChange(1)
          })
        }
      }
    }
    nextTick(() => {
      if (['rollPagination', 'roll'].includes(props.sidePagination) && !observer) {
        const options = {
          root: null,
          rootMargin: '0px',
          threshold: 0.5
        }
        const callback = (entries, observer) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              // 目标元素进入视口
              opt.value.pageNum++
              props.sidePagination === 'rollPagination' ? customerPage() : handleCurrentChange(opt.value.pageNum)
            }
          })
        }
        targetDom = tableRef.value.$el.querySelector('.load-more-btn')
        if (targetDom) {
          observer = new IntersectionObserver(callback, options)
          observer.observe(targetDom)
        }
      }
    })
  }
  if (isShowSummary.value) {
    const rowSumHandle = (localResponseNodes || []).find(v => v.name === 'RowSumHandle' || v.name === 'rowSumHandle')
    const mergeTatol = (rowSumHandle?.metadataList || []).find(item => item.type === 'merge-total' || item.type === 'total')
    const item = mergeTatol?.metadataList?.find(v => v.code === 'end')
    timerMergeTable = setTimeout(() => {
      const tds = document.querySelectorAll(`${proxy.$attrs.class ? `.${proxy.$attrs.class}` : '.summary-table'} .el-table__footer-wrapper tr>td`)
      if (!tds?.length) return
      if (item) {
        const value = Number(item.value) + 1
        const num = value <= 2 ? 2 : value
        for (let i = 0; i < num; i++) {
          if (i === (localSelection.value ? 1 : 0)) {
            tds[i].colSpan = num
            tds[i].style.textAlign = 'center'
          } else {
            tds[i].style.display = 'none'
          }
        }

      } else if (tds && tds[1]) {
        tds[1].colSpan = 4
        tds[1].style.textAlign = 'center'
        tds[0].style.display = 'none'
      }
    }, 100)
  }
  flatMap(computedColumns.value)
}, {
  deep: true,
  immediate: true
})

const columnsChange = ({ prop, parentCode }, { checkedKeys, halfCheckedKeys }) => {
  const allCheckedKeys = [...checkedKeys, ...halfCheckedKeys]
  const columnNode = columnsNodeMap.get(prop)
  const flag = allCheckedKeys.includes(prop)
  columnNode.isHide = !flag
  columnNode.hidden = !flag
  if (parentCode) {
    const parentFlag = allCheckedKeys.includes(parentCode)
    const parentColumn = columnsNodeMap.get(parentCode)
    parentColumn.isHide = !parentFlag
    parentColumn.hidden = !parentFlag
  }
}
const getAllId = (data, list) => {
  checkList.value = []
  if (list && list.length) {
    for (let i = 0; i < list.length; i++) {
      if (list[i].isHide) continue
      data.push(list[i].prop)
      if (list[i].children) {
        getAllId(data, list[i].children)
      }
    }
  }
  return data
}

const cellClick = (row, cell, td, event) => {
  proxy.$attrs.onCellClick && proxy.$attrs.onCellClick(cell, row, event, td)
}
const getSummaries = param => {
  const { columns } = param
  const sums = []
  const totalData = props.rawData?.responseData?.length ? props.rawData?.responseData[0] : {}
  columns.forEach((column, index) => {
    const { property } = column
    if (property === 'settingIcon') return
    if (index === (localSelection.value ? 1 : 0)) {
      sums[index] = h('div', { class: proxy.$attrs.onCellClick ? 'cell-primary' : '', onClick: e => cellClick({ ...column, property: 'totalAll', label: '合计' }, '', '', e) }, [
        '总值'
      ])
      return
    }
    // let data = ''
    // if (property == 'totalCount') {
    //   data = totalData[property]
    // } else {
    //   data = Number.isNaN(Number(totalData[property])) ? totalData[property] : totalData[property].toFixed(2)
    // }
    const data = typeof totalData[property] == 'string'
      ? totalData[property]
      : Number.isNaN(Number(totalData[property]))
        ? totalData[property]
        : Number(totalData[property].toFixed(2))
    /**
       * elememt table 合计兰不支持toolTip
       */
    sums[index] = h(ShowTooltip, {
      key: `${index}_${data}`,
      effect: 'light',
      content: data,
      placement: 'top'
    })
  })

  return sums
}
/** 排序 */
const handlesortChange = column => {
  /**
     * asc 升序
     * desc 降序 从高往低
     */
  opt.value.orderBy = !column.order ? undefined : column.prop
  opt.value.orderType =
    !column.order
      ? undefined
      : column.order === 'ascending' ? 'asc' : 'desc'
  emit('handleChange', opt.value)
}
const initColumns = () => {
  columnsList.value = computedColumns.value.filter(item => item.type !== 'index' && item.prop !== 'settingIcon')
  checkList.value = getAllId([], columnsList.value)
}
watch(
  () => computedColumns.value,
  () => {
    timer && clearTimeout(timer)
    timer = setTimeout(() => {
      props.isNeedSetting && initColumns()
    }, 1000)
  },
  {
    deep: true,
    immediate: true
  }
)
defineExpose({ toggleSelection, getSelectionRows, clearSelection, toggleRowSelection })
onBeforeUnmount(() => {
  timer && clearTimeout(timer)
  timerMergeTable && clearTimeout(timerMergeTable)
  if (observer) {
    targetDom && observer.unobserve(targetDom)
    observer.disconnect()
  }
})
</script>
<style lang="scss" scoped>
.table-wrapper {
  width: 100%;
  height: v-bind("props.height");
  max-height: v-bind("props.maxHeight");
  overflow: auto;

  &::before,
  &::after {
    width: 0;
  }

  .el-pagination {
    margin-top: 10px;
  }

  .table-wrapper__content {
    width: 100%;

    &>div {
      margin: 0 !important;
    }
  }

  // 放开后 应用流量分析-应用详情-访问域名详情中的分页器会消失不见
  // .table-wrapper__content {
  //   height: calc(100% - 44px);
  // }
  &.no-pagination {
    .table-wrapper__content {
      height: 100%;
    }
  }

  &.no-border {
    :deep(.table-wrapper__content) {
      th.el-table__cell {
        border-right: none !important;
      }
    }
  }

  .table-title {
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    margin-bottom: 0;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--g-m-box-title-color);

    &::before {
      height: 15px;
    }

    :deep(.el-form-item) {
      margin: 0 0 0 32px;

      .el-form-item__content {
        line-height: 30px;

        .el-radio-button__inner {
          padding: 8px 15px;
          font-size: 12px;
        }

        .el-input__wrapper {
          padding: 0 11px;
        }
      }

      .el-radio-button__original-radio:checked+.el-radio-button__inner {
        background-color: white;
        color: var(--el-radio-button-checked-bg-color, var(--el-color-primary));
      }
    }
  }

  :deep(.is-scrolling-left) {
    z-index: 1;
  }

  :deep(.cell) {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;

    .el-button {
      padding: 0;
    }
  }

  :deep(.el-table--fit) {
    height: 100% !important;
  }

  :deep(.el-table__header-wrapper) {
    th {
      &:last-child {
        border-right: 1px solid #dcdcdc;
      }

      background-color: #fafafa !important;

      &.settingIcon {
        .el-icon {
          cursor: pointer;
          width: 100%;
        }
      }
    }

    th:last-child {
      border-bottom: 1px solid var(--el-table-border-color);
    }

    tr:first-child {
      th:last-child {
        border-right: 0 !important;
      }
    }

    tr:not(:first-child) {
      th {
        border-top: 1px solid var(--el-table-border-color);
      }
    }

    .before-setting-column {
      border-right: 0 !important;
    }
  }

  :deep(.el-table__body-wrapper) {

    // 如果设置auto 大模型那边会出现双滚动条
    // overflow: auto;
    .el-table__body {
      min-height: 1px;
      display: block;

      .cell-primary {
        cursor: pointer;
        padding: 0 6px 0 0;
        color: var(--el-color-primary) !important;

        .cell {
          cursor: pointer;
          color: var(--el-color-primary) !important;
        }
      }
    }

    .load-more-btn {
      height: 40px;
      text-align: center;

      .el-loading-spinner {
        top: 27px;
      }

      .circular {
        width: 24px;
        height: 24px;
      }
    }
  }

  .is-link {
    color: #474747;
  }

  .el-table__inner-wrapper {
    border-right: none;
  }

  &:not(.no-pagination) {

    :deep(.el-table__empty-block) {
      min-height: 300px;
      border-bottom: 1px solid var(--g-table-header-divide-line-color);
    }
  }

  :deep(.el-button) {
    padding: 10px 8px;
  }

  :deep(.el-empty__description) {
    p {
      line-height: 12px;
    }
  }

  :deep(.el-table tr) {
    height: 0;
    transition: all 5s;

    .superfluous {
      color: #afafaf;
      display: block;
      transition: all 0.2s;
      height: 23px;
    }

    &.expand-tr {
      .superfluous {
        height: 0;
      }
    }
  }

  :deep(.el-table__footer-wrapper) {
    .el-table__cell {
      border-right: none !important;

      .cell-primary {
        cursor: pointer;
        color: var(--el-color-primary) !important;

        .cell {
          cursor: pointer;
          color: var(--el-color-primary) !important;
        }
      }
    }
  }
}

.bordertable {
  border: solid 1px #dcdcdc;
  padding: 20px;
}

/* 应用旋转动画到元素上 */
.expand {
  .icon {
    transform: rotate(90deg);
    transition: all 0.2s;
  }
}

.changeExpand {
  cursor: pointer;
}

:deep(.el-table) {
  .el-scrollbar__view {
    height: calc(100% - 1px);

    .el-table__empty-text {
      height: 100%;

      .el-empty {
        height: 100%;
      }
    }
  }

  .tr-fixed {
    display: table-row;
    position: sticky;
    bottom: 0;
    width: 100%;

    td {
      border: 1px solid #f3f5fa;
      background: #f4f7fa;
      opacity: 1;
    }
  }

  .fixed-row {
    bottom: 0;
  }
}
</style>
