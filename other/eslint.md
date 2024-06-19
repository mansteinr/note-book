### 学习地址

[eslint]()

### 原理

>erewrer

### 安装
  ```
  npm install eslint --save-dev
  ```

  查看版本

  ```
  npx eslint --verison
  ```

### 自动生成配置文件

运行命令行

```
npm install @eslint/config
```

最后会自动安装<code>eslint-plugin-vue</code>

在根目录下生成<code>eslint.config.js</code>、<code>eslintrc.cjs</code>


### 初始文件配置

<code>eslintrc.cjs</code>文件中的初始配置如下：

```
/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting'
  ],
  overrides: [
    {
      files: [
        'cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}',
        'cypress/support/**/*.{js,ts,jsx,tsx}'
      ],
      'extends': [
        'plugin:cypress/recommended'
      ]
    }
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  }
}

```