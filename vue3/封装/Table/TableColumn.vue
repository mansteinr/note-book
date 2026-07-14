<template>
  <!-- 如果有配置多级表头的数据，则递归该组件 -->
  <template v-if="column.children?.length && !column.isHide">
    <el-table-column
      v-bind="{ ...$attrs, ...column }"
      :show-overflow-tooltip="!column.noTooltip"
      :class-name="column.className || column.prop"
    >
      <TableColumn
        v-for="item in column.children"
        :key="item.prop"
        :column="{ ...$attrs, ...item }"
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
      <template #header>
        <slot :name="`${column.prop}Header`">
          {{ column.label }}
          <!--<ShowTooltip
            effect="light"
            :content="column.label"
          />-->
        </slot>
      </template>
    </el-table-column>
  </template>
  <template v-else>
    <el-table-column
      v-if="!column.isHide"
      :sortable="column.sortable"
      v-bind="{ ...$attrs, ...column }"
      :show-overflow-tooltip="!column.noTooltip"
      :class-name="column.className || column.prop"
    >
      <template #header>
        <div
          v-if="column.label?.includes('_prefix_')"
          class="header-col-wrapper"
        >
          <div
            v-for="(item, index) in column.label.split('_prefix_')"
            :key="item"
            :class="`header-col${index + 1}`"
          >
            {{ item }}
          </div>
          <div class="header-line" />
        </div>

        <template v-else-if="column.description && column.description != ''">
          {{ column.label }}
          <el-tooltip
            :content="column.description"
            placement="top"
            effect="dark"
          >
            <i class="iconfont icon-tishi" />
          </el-tooltip>
        </template>

        <slot
          v-else
          :name="`${column.prop}Header`"
        >
          {{ column.label }}
          <!--<ShowTooltip
            effect="light"
            :content="column.label"
          />-->
        </slot>
      </template>
      <template
        v-if="column.prop != 'settingIcon'"
        #default="scope"
      >
        <template v-if="column.buttons && column.buttons.length">
          <el-button
            v-for="button in column.buttons"
            :key="button.text"
            text
            v-bind="{ ...$attrs, ...column.button }"
            :type="button.type || 'primary'"
            @click="button.onClick(scope.row, $event)"
          >
            {{ button.text }}
          </el-button>
        </template>
        <span
          v-else
          :class="column.prop"
          :style="scope.row[`${column.prop}Style`]"
          @click="column.onClick && column.onClick(scope.row, $event)"
        >
          <slot
            v-if="column.special && column.slot"
            v-bind="scope"
          >
            <div v-if="Array.isArray(scope.row[column.prop])">
              <div>
                {{ typeof scope.row[column.prop][0] === 'number'
                  ? scope.row[column.prop][0].toFixed(2)
                  : scope.row[column.prop][0]
                }}
              </div>
              <div class="superfluous">
                {{ typeof scope.row[column.prop][1] === 'number'
                  ? scope.row[column.prop][1].toFixed(2)
                  : scope.row[column.prop][1]
                }}
              </div>
            </div>
            <div v-else>
              {{ column.formatter
                ? column.formatter(scope.row)
                : showLableFun(scope.row, column)
              }}
            </div>
          </slot>
          <slot
            v-else
            :name="column.prop"
            v-bind="scope"
          >
            {{ column.formatter
              ? column.formatter(scope.row)
              : showLableFun(scope.row, column)
            }}
          </slot>
        </span>
      </template>
    </el-table-column>
  </template>
</template>
<script setup name="TableColumn">
import { isEmpty, isEmptyNULL } from '@/util'
// import ShowTooltip from '@/components/ShowTooltip/index.vue'
defineProps({
  column: {
    type: Object,
    default: () => ({})
  }
})
const showLableFun = (row, column) => {
  if (column.extraCode) {
    return isEmpty(row[column.prop]) + (isEmptyNULL(row[column.extraCode]) ? `(${row[column.extraCode]}${column.extraCodeUnit || ''})` : '(--)')
  } else {
    return isEmpty(row[column.prop])
  }
}
</script>

<style lang="scss">
.header-col-wrapper {
  height: 30px;
  position: relative;

  .header-col1 {
    position: absolute;
    left: 10px;
    bottom: -4px;
  }

  .header-col2 {
    position: absolute;
    right: 1px;
    top: -3px;
  }

  .header-line {
    width: 1px;
    height: 100px;
    transform: rotate(-67deg);
    transform-origin: top;
    background-color: #dcdcdc;
  }
}
</style>
