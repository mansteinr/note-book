import { buildTree, arrToObj } from '@/util'
const flatMultipleHeader = (list, detection, data) => {
  if (detection[data.code]) return
  detection[data.code] = data.code
  list.push(data)
  if (data.parentMetadata) {
    data.parentCode = data.parentMetadata.code
    flatMultipleHeader(list, detection, data.parentMetadata)
  }
}
//  displayType tabulation 分页  noPageTabulation 不分页
// formatterTable 第二个参数 后台经常将下拉框查询数据用table形式传给前端
export const formatterTable = (data, isOnlyDataMap, $attrs) => {
  let returnList = []
  let localColumns = []
  const { rawData, widthMap = {}, isOperate, isNeedSetting, operateFixed, isNeedNumber, isVirturalTable, serialLabel = '编号' } = data || {}

  const {
    pageData = {},
    responseDataList = [],
    reportMetadata: { displayType, responseMetadataList = [], responseNodes, isMultipleHeader }
  } = rawData
  if (!isOnlyDataMap) {
  // 数据前置处理
    let perProcessList = []
    if (isMultipleHeader) {
      const detection = {}
      responseMetadataList.forEach(v => {
        flatMultipleHeader(perProcessList, detection, v)
      })
    // perProcessList = buildTree(list, 'parentCode', 'code')
    } else {
      perProcessList = responseMetadataList || []
    }
    const mapData = arrToObj(perProcessList, 'code', 'unit')
    /** 从后台接口数据中定义 columns*/
    const mapColumnList = perProcessList
      .filter(v => !v.hidden)
      .sort((a, b) => a.index - b.index)
      .map(v => ({
        ...v,
        prop: v.code,
        dataKey: v.code,
        sortable: v.sort ? 'custom' : false,
        extraCodeUnit: mapData[v.extraCode] || '',
        width: v.code === 'fromRegion' ? 100 : null,
        minWidth: v.code === 'fromRegion' ? null : (widthMap[v.code] || v.width || 120),
        description: v.description || ($attrs['header-tip'] ? $attrs['header-tip'][v.code] : ''),
        title: `${v.name.includes(',') ? v.name.replace(',', '/') : v.name}${v.unit ? `(${v.unit})` : ''}`,
        label: `${v.name.includes(',') ? v.name.replace(',', '_prefix_') : v.name}${v.unit ? `(${v.unit})` : ''}`
      }))

    isOperate && mapColumnList.push({
      label: '操作',
      noTooltip: true,
      prop: 'operateTool',
      fixed: operateFixed || 'right',
      width: widthMap.operateTool || widthMap.default || 100
    })
    if (isNeedSetting && !isVirturalTable && mapColumnList.length) {
      const lastColumn = mapColumnList[mapColumnList.length - 1]
      lastColumn.className = `${
        lastColumn.className || ''
      } before-setting-column`
      mapColumnList.push({
        label: '',
        width: 55,
        fixed: 'right',
        prop: 'settingIcon'
      })
    }
    localColumns = isNeedNumber
      ? [
        {
          width: 55,
          label: serialLabel,
          title: serialLabel,
          type: 'index',
          fixed: 'left',
          // 这是虚拟table 属性
          cellRenderer: ({ rowIndex }) => `${rowIndex + 1}`
        },
        ...mapColumnList
      ]
      : mapColumnList
  }
  if (displayType === 'tabulation') {
    // 返回tableData
    const list = pageData?.list || []
    list.forEach((item, index) => {
      const obj = { rowIndex: index }
      item.forEach(v => {
        if (v.style) {
          obj[`${v.code}Style`] = JSON.parse(v.style)
        }
        if (v.type) {
          obj[v.code] =  v.type === 'number' ? v.value.toFixed(2) : v.value
        } else {
          obj[v.code] = typeof v.value === 'number' ? v.value.toFixed(2) : v.value
        }
      })
      returnList.push(obj)
    })
  } else {
    const list = responseDataList || []
    list.forEach((item, index) => {
      const obj = { rowIndex: index }
      item.forEach(v => {
        if (isOnlyDataMap) {
          obj.value = v[isOnlyDataMap.value || 'value']
          obj.label = v[isOnlyDataMap.label || 'value']
        } else {
          if (v.style) {
            obj[`${v.code}Style`] = JSON.parse(v.style)
          }
          if (v.type) {
            obj[v.code] =  v.type === 'number' ? v.value.toFixed(2) : v.value
          } else {
            obj[v.code] = typeof v.value === 'number' ? v.value.toFixed(2) : v.value
          }
        }
      })
      returnList.push(obj)
    })
  }
  return {
    responseNodes,
    list: returnList,
    columns: isMultipleHeader ? buildTree(localColumns, 'parentCode', 'code') : localColumns
  }
}
// 展开
export const changeExpand = ({ $index, isExpand }) => {
  const tr = document.querySelectorAll('.el-scrollbar tr')[$index]
  const iconDom = tr.querySelector('td:first-child .cell div')
  if (isExpand == undefined) {
    tr.classList.toggle('expand-tr')
    iconDom.classList.toggle('expand')
  } else {
    if (!isExpand) {
      tr.classList.add('expand-tr')
      iconDom.classList.remove('expand')
    } else {
      tr.classList.remove('expand-tr')
      iconDom.classList.add('expand')
    }
  }

}
export const expandAll = () => {
  const tb = document.querySelectorAll('.el-table__body')[0]
  const domList = tb.querySelectorAll('tr')

  const tr = document.querySelectorAll('.el-table__header tr')[0]
  const iconDom = tr.querySelector('th:first-child .cell div')
  domList.forEach((v, index) => {
    changeExpand({ $index: index, isExpand: !iconDom.classList.contains('expand') })
  })
  iconDom.classList.toggle('expand')
}

