<template>
  <div
    class="el-form-wrap"
    :class="layoutType"
  >
    <div
      v-if="exportPosition == 'left'"
      class="btn-group"
      :class="{
        'layoyt-left': exportPosition == 'left'
      }"
      style="margin-right: 20px;"
    >
      <slot name="btnGroup">
        <!-- 一般导出 -->
        <slot
          v-if="exportUrl"
          name="output"
        >
          <Download
            :export-url="exportUrl"
            :export-text="exportText"
            :params="params || formData"
            :download-verification-form-ref="downloadVerificationFormRef"
            @ouput="ouput"
          />
        </slot>
        <slot />
        <slot name="btnLeft" />
      </slot>
    </div>
    <el-form
      ref="formRef"
      :rules="rules"
      :model="formData"
      :inline="formLayout"
      :label-width="labelWidth"
      :class="`${exportPosition == 'left' ? 'outputLeft' : ''}`"
      @submit.prevent
    >
      <el-form-item
        v-for="(item, index) in formList"
        :key="item.prop"
        :prop="item.prop"
        :label="item.label"
        v-bind="item"
        :rules="item.rules ? item.rules.map(v => ({ index, ...item, ...v })) : null"
        :class="{
          'has-tip': !!item.tip,
          [item.prop]: item.prop,
          'has-label-tip': !!item.labelTip,
          'el-form-item-range': item.children?.length
        }"
      >
        <template
          v-if="item.label"
          #label
        >
          <slot
            :name="`${item.prop}LabelPre`"
            v-bind="item"
          ></slot>
          {{
            item.label
          }}
          <slot
            :name="`${item.prop}Label`"
            v-bind="item"
          >
            <el-popover
              effect="dark"
              :content="item.labelTip"
              :placement="item.placement || 'top'"
              :width="item.labelTipWidth || 'auto'"
              :popper-style="{ fontSize: '12px' }"
            >
              <template #reference>
                <el-icon v-if="item.labelTip">
                  <Warning />
                </el-icon>
              </template>
            </el-popover>
          </slot>
          <!--  -->
        </template>
        <slot
          :name="item.prop"
          v-bind="item"
        >
          <!-- 组合input框 -->
          <template v-if="item.children">
            <template
              v-for="(child, childIndex) in item.children"
              :key="child.prop"
            >
              <el-form-item
                :prop="child.prop"
                :label="child.label"
                class="combination-form-item"
                :label-width="child.label.length >= 4 ? child.label : '68px'"
                :rules="child.rules ? child.rules.map(v => ({ index, ...child, ...v })) : null"
              >
                <el-input
                  v-if="child.itemType === 'input'"
                  v-bind="child"
                  :model-value="getNestedValue(formData, child.prop)"
                  @update:model-value="setNestedValue(formData, child.prop, $event)"
                  clearable
                  :placeholder="`请输入${child.placeholder || child.label}`"
                  @change="item.onChange || (isSubmitForm ? '' : submitForm())"
                />
                <el-date-picker
                  v-else-if="child.itemType === 'datePicker'"
                  :model-value="getNestedValue(formData, child.prop)"
                  @update:model-value="setNestedValue(formData, child.prop, $event)"
                  :clearable="!!child.clearable"
                  value-format="YYYY-MM-DD"
                  format="YYYY-MM-DD"
                  range-separator="至"
                  start-placeholder="开始日期"
                  popper-class="date_form"
                  end-placeholder="结束日期"
                  :placeholder="`请选择${child.placeholder || child.label}`"
                  :shortcuts="child.isShortcuts ? shortcuts : []"
                  v-bind="{ disabledDate: disabledDateFun, ...child }"
                  @change="item.onChange || (isSubmitForm ? '' : submitForm())"
                />
              </el-form-item>
              <span
                v-if="childIndex === 0 && item.separator"
                class="separator"
              >{{ item.separator }}</span>
            </template>
          </template>
          <!-- 输入框 -->
          <el-input
            v-else-if="item.itemType === 'input'"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            v-bind="item"
            clearable
            :style="`width:${item.width || '220px'}`"
            :placeholder="`${item.placeholder ? item.placeholder : `请输入${item.label}`}`"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
          >
            <template
              v-if="item.append"
              #append
            >
              {{ item.append }}
            </template>
            <template
              v-if="item.prefix"
              #prefix
            >
              <el-icon>
                <svg-icon :name="item.prefix" />
              </el-icon>
            </template>
          </el-input>
          <!-- 文本域 -->
          <el-input
            v-else-if="item.itemType === 'textarea'"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            v-bind="item"
            clearable
            type="textarea"
            :style="`width:${item.width || '220px'}`"
            :placeholder="`${item.placeholder ? item.placeholder : `请输入${item.label}`}`"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
          />
          <!-- 选择框V2 -->
          <el-select-v2
            v-else-if="item.itemType === 'selectV2'"
            v-bind="item"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            filterable
            :options="item.options"
            :style="`width:${item.width || '220px'}`"
            :clearable="item.clearable ? true : false"
            :placeholder="`${item.placeholder ? item.placeholder : `请选择${item.label}`}`"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
          />
          <!-- 选择框 -->
          <el-select
            v-else-if="item.itemType === 'select'"
            v-bind="item"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            filterable
            collapse-tags
            collapse-tags-tooltip
            :multiple="item.multiple"
            :style="`width:${item.width || '220px'}`"
            :clearable="item.clearable ? true : false"
            :placeholder="`${item.placeholder ? item.placeholder : `请选择${item.label}`}`"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
            @focus="item.onFocus"
          >
            <template
              v-if="item.isCheckAll"
              #header
            >
              <el-checkbox
                v-model="item.checkAll"
                :indeterminate="item.indeterminate"
                @change="item.onAllChange"
              >
                全部
              </el-checkbox>
            </template>
            <template v-if="Array.isArray(item.options)">
              <el-option
                v-for="item_ in item.options || []"
                :key="item_[item.selectValue || 'value']"
                :label="item_[item.selectLabel || 'label'] || '--'"
                :value="item_[item.selectValue || 'value']"
                :disabled="item_.disabled"
              />
            </template>
            <template v-else>
              <el-option
                v-for="(value, key) in item.options"
                :key="key"
                :label="value || '--'"
                :value="key"
              />
            </template>
          </el-select>
          <el-date-picker
            v-else-if="item.itemType === 'datePicker'"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            :clearable="!!item.clearable"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            popper-class="date_form"
            end-placeholder="结束日期"
            :placeholder="`请选择${item.placeholder || item.label}`"
            :shortcuts="item.isShortcuts ? shortcuts : []"
            v-bind="{ disabledDate: disabledDateFun, ...item }"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
          />
          <!-- 单选框 -->
          <el-radio-group
            v-else-if="item.itemType === 'radio'"
            :model-value="getNestedValue(formData, item.prop)"
            @update:model-value="setNestedValue(formData, item.prop, $event)"
            @change="item.onChange || (isSubmitForm ? '' : submitForm())"
          >
            <template v-if="Array.isArray(item.options)">
              <el-radio-button
                v-for="item_ in item.options || []"
                :key="item_[item.selectValue || 'value']"
                :value="item_[item.selectValue || 'value']"
              >
                {{ item_[item.selectLabel || 'label'] }}
              </el-radio-button>
            </template>
            <template v-else>
              <el-radio-button
                v-for="(value, key) in item.options || {}"
                :key="key"
                :value="key"
              >
                {{ value }}
              </el-radio-button>
            </template>
          </el-radio-group>
          <template v-else>
            {{ item.value }}
          </template>
        </slot>
      </el-form-item>
    </el-form>
    <div
      v-if="isNeedBtnGroup"
      class="btn-group"
    >
      <slot name="btnGroup">
        <slot
          v-if="notConfirm"
          name="confirm"
        >
          <el-button
            type="primary"
            :disabled="loading"
            @click="submitForm"
          >
            {{ confirmText }}
          </el-button>
        </slot>
        <slot
          v-if="needCancel"
          name="cancel"
        >
          <el-button
            :disabled="loading"
            @click="cancel"
          >
            {{ cancelText }}
          </el-button>
        </slot>
        <!-- 一般导出 -->
        <slot
          v-if="exportUrl && exportPosition != 'left'"
          name="output"
        >
          <Download
            :export-url="exportUrl"
            :export-text="exportText"
            :params="params || formData"
            :download-verification-form-ref="downloadVerificationFormRef"
            @ouput="ouput"
          />
        </slot>
        <!-- 多条件导出 -->
        <slot
          v-if="conditionExportOptions && conditionExportOptions.length"
          name="conditionExport"
        >
          <Download
            type="multiple"
            :export-url="exportUrl"
            :condition-export-options="conditionExportOptions"
            :download-verification-form-ref="downloadVerificationFormRef"
            :params="params || formData"
            @ouput="ouput"
          />
        </slot>
        <slot />
      </slot>
    </div>
  </div>
</template>
<script setup name="Form">
import { ref } from 'vue'
import moment from 'moment'
import { disabledDateFun } from '@/util/index'
import { Warning } from '@element-plus/icons-vue'
import Download from '@/components/Download/index.vue'
moment.suppressDeprecationWarnings = true

let formHeight = 0
const isShowMore = ref(true)
const emit = defineEmits([
  'update:modelValue',
  'confirm',
  'reset',
  'cancel',
  'output'
])
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => { }
  },
  formItemList: {
    type: Array,
    default: () => []
  },
  labelWidth: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: '统计'
  },
  exportUrl: {
    type: String,
    default: ''
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  resetText: {
    type: String,
    default: '重置'
  },
  formLayout: {
    type: Boolean,
    default: true
  },
  isNeedBtnGroup: {
    type: Boolean,
    default: true
  },
  notConfirm: {
    type: Boolean,
    default: true
  },
  needCancel: {
    type: Boolean,
    default: false
  },
  notconditionExport: {
    type: Boolean,
    default: false
  },
  isNeedExpand: {
    type: Boolean,
    default: true
  },
  isDialogForm: {
    type: Boolean,
    default: false
  },
  conditionExportOptions: {
    type: Array,
    default: () => []
  },
  exportPosition: {
    type: String,
    default: ''
  },
  params: {
    type: Object,
    default: () => null
  },
  rules: {
    type: Object,
    default: () => { }
  },
  isDisableToday: {
    type: Boolean,
    default: true
  },
  layoutType: {
    type: String,
    default: 'space-between'
  },
  downloadVerificationFormRef: {
    type: Object,
    default: null
  },
  exportText: {
    type: String,
    default: '导出'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const end = new Date()
if (props.isDisableToday) {
  end.setTime(end.getTime() - 3600 * 1000 * 24 * 1)
}

const getStart = day => {
  const start = new Date()
  const days = props.isDisableToday ? day : day - 1
  return start.setTime(start.getTime() - 3600 * 1000 * 24 * days)
}
const shortcuts = [
  {
    text: '近7天',
    value: () => {
      return [getStart(7), end]
    }
  },
  {
    text: '近15天',
    value: () => {
      return [getStart(15), end]
    }
  },
  {
    text: '近30天',
    value: () => {
      return [getStart(30), end]
    }
  }
]
const formRef = ref(null)
const formData = computed(() => props.modelValue)

const getNestedValue = (obj, path) => {
  if (!path) return obj
  const keys = path.split('.')
  let result = obj
  for (const key of keys) {
    if (result == null) return undefined
    result = result[key]
  }
  return result
}

const setNestedValue = (obj, path, value) => {
  if (!path) return
  const keys = path.split('.')
  const lastKey = keys.pop()
  let target = obj
  for (const key of keys) {
    if (target[key] == null) {
      target[key] = {}
    }
    target = target[key]
  }
  target[lastKey] = value
  if (target.pageSize) {
    target.pageNum = 1;
    target.pageSize = 10;
  }
  emit('update:modelValue', props.modelValue)
}
const formList = computed(() => props.formItemList.filter(v => !v.isHide))

const resetForm = () => {
  formRef.value.resetFields()
}
const cancel = () => {
  return new Promise(resolve => {
    resetForm()
    emit('cancel')
    resolve('cancel')
  })
}
const ouput = () => {
  emit('output')
}
const isSubmitForm = computed(() => props.isDialogForm
  ? true
  : props.isNeedBtnGroup ? !!props.notConfirm : false)

const submitForm = () => {
  formRef.value.validate(valid => {
    valid && emit('confirm')
  })
}
const validateForm = () => {
  return new Promise((resolve, reject) => {
    formRef.value.validate(valid => {
      valid ? resolve(true) : reject(false)
    })
  })
}

const addClassFun = () => {
  if (!formRef.value) return
  formHeight = formRef.value.$el.offsetHeight
  isShowMore.value = formHeight > 50
  formRef.value.$el.style.maxHeight = '500px'
}
onMounted(() => {
  addClassFun()
})
defineExpose({
  cancel,
  resetForm,
  submitForm,
  validateForm
})
</script>

<style lang="scss" scoped>
.el-form-wrap {
  display: flex;
  justify-content: v-bind("props.layoutType");
  margin-left: auto;
  overflow: hidden;

  &.lable-value-parallel {
    .el-form-item {
      display: block;
      margin-bottom: 10px;

      &.el-form-item-range {
        margin-bottom: 0;

        &> :deep(.el-form-item__content) {
          justify-content: space-between;
        }
      }

      &:deep(.el-form-item__label) {
        width: 100%;
        justify-content: flex-start;
      }

      :deep(.el-form-item__content) {
        .el-select {
          width: 100% !important;
        }
      }
    }
  }

  &.flex-end {
    .el-form {
      .el-form-item {
        &:last-child {
          margin-right: 10px;
        }
      }
    }
  }

  .el-form {
    max-height: 50px;
    will-change: max-height;
    transition: max-height 0.3s ease-in;

    .el-form-item {
      margin-right: 10px;

      &:last-child {
        margin-right: 0;
      }

      :deep(.el-form-item__content) {
        .el-button {
          padding: 10px 8px;
        }
      }

      &.statistical-cycle {
        :deep(.el-select) {
          width: 180px;
        }
      }

      .combination-form-item {
        margin-right: 0;

        .el-input {
          width: 160px;
        }
      }

      .separator {
        margin: 0 10px;
      }

      &.border-radio {
        :deep(.el-form-item__content) {
          .el-radio-button__original-radio:checked+.el-radio-button__inner {
            background-color: white;
            color: var(--el-radio-button-checked-bg-color, var(--el-color-primary));
          }
        }
      }

      &.has-label-tip {
        :deep(.el-form-item__label) {
          align-items: center;

          .el-icon {
            margin-left: 2px;
            cursor: pointer;
          }
        }
      }
    }
  }

  &.expand {
    .btn-group {
      :deep(.el-icon--down) {
        transform: rotate(180deg);
      }
    }
  }

  .btn-group {
    display: flex;
    margin-left: 10px;

    &.layoyt-left {
      margin-left: 0;
    }

    &>.el-dropdown,
    &>.el-button {
      margin-left: 8px;

      &:first-child {
        margin-left: 0;
      }
    }

    &>.el-dropdown {
      :deep(.el-button) {
        padding: 10px 8px;
      }
    }

    :deep(.el-icon--right) {
      will-change: transform;
      transition: transform 0.3s ease-in;
    }
  }

  .outputLeft {
    margin-left: auto;
  }
}
</style>
