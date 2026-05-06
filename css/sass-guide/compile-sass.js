#!/usr/bin/env node

/**
 * Sass 编译演示脚本
 * 展示如何使用 Node.js 编译 Sass 文件
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 检查是否安装了 sass
async function checkSassInstallation() {
    try {
        const { stdout } = await execAsync('sass --version');
        console.log(`✅ Sass 已安装，版本: ${stdout.trim()}`);
        return true;
    } catch (error) {
        console.log('❌ Sass 未安装，请先安装: npm install -g sass');
        return false;
    }
}

// 编译 Sass 文件
async function compileSass(inputFile, outputFile, options = {}) {
    const style = options.style || 'expanded';
    const sourceMap = options.sourceMap ? '--source-map' : '';
    
    const command = `sass ${inputFile} ${outputFile} --style ${style} ${sourceMap}`;
    
    console.log(`📦 编译: ${path.basename(inputFile)} -> ${path.basename(outputFile)}`);
    console.log(`  命令: ${command}`);
    
    try {
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            console.log(`⚠️  警告: ${stderr}`);
        }
        
        const stats = fs.statSync(outputFile);
        console.log(`✅ 编译成功！文件大小: ${(stats.size / 1024).toFixed(2)} KB`);
        
        // 显示编译前后的对比
        if (options.showComparison) {
            await showComparison(inputFile, outputFile);
        }
        
        return true;
    } catch (error) {
        console.error(`❌ 编译失败: ${error.message}`);
        return false;
    }
}

// 显示编译前后对比
async function showComparison(scssFile, cssFile) {
    try {
        const scssContent = fs.readFileSync(scssFile, 'utf8');
        const cssContent = fs.readFileSync(cssFile, 'utf8');
        
        const scssLines = scssContent.split('\n').length;
        const cssLines = cssContent.split('\n').length;
        
        console.log('\n📊 编译统计:');
        console.log(`   SCSS 行数: ${scssLines}`);
        console.log(`   CSS 行数: ${cssLines}`);
        console.log(`   压缩率: ${((1 - cssLines / scssLines) * 100).toFixed(1)}%`);
        
        // 显示一些关键特性
        const features = analyzeSassFeatures(scssContent);
        console.log('\n🔍 Sass 特性使用情况:');
        features.forEach(feature => {
            console.log(`   ${feature.name}: ${feature.count} 处`);
        });
        
    } catch (error) {
        console.log('无法显示对比信息:', error.message);
    }
}

// 分析 Sass 特性使用情况
function analyzeSassFeatures(content) {
    const features = [
        { name: '变量定义 ($)', pattern: /\$[a-zA-Z][\w-]*\s*:/g },
        { name: '嵌套规则', pattern: /\s*\{[^}]*\{/g },
        { name: '混合定义 (@mixin)', pattern: /@mixin\s+\w+/g },
        { name: '混合使用 (@include)', pattern: /@include\s+\w+/g },
        { name: '继承 (@extend)', pattern: /@extend\s+[.%]/g },
        { name: '函数定义 (@function)', pattern: /@function\s+\w+/g },
        { name: '控制指令 (@if, @for等)', pattern: /@(if|for|each|while)\b/g },
        { name: '导入文件 (@import)', pattern: /@import\s+['"]/g },
        { name: '模块系统 (@use)', pattern: /@use\s+['"]/g },
    ];
    
    return features.map(feature => {
        const matches = content.match(feature.pattern) || [];
        return {
            name: feature.name,
            count: matches.length
        };
    }).filter(feature => feature.count > 0);
}

// 创建示例项目结构
function createExampleProject() {
    const projectStructure = {
        'src/scss': [
            '_variables.scss',
            '_mixins.scss',
            '_functions.scss',
            'components/_buttons.scss',
            'components/_cards.scss',
            'layout/_grid.scss',
            'main.scss'
        ],
        'dist/css': []
    };
    
    console.log('\n📁 示例项目结构:');
    Object.entries(projectStructure).forEach(([dir, files]) => {
        console.log(`  ${dir}/`);
        files.forEach(file => {
            console.log(`    ${file}`);
        });
    });
}

// 显示帮助信息
function showHelp() {
    console.log(`
🎨 Sass 编译工具

用法:
  node compile-sass.js [命令]

命令:
  compile    编译 example.scss 文件
  watch      监听文件变化并自动编译
  minify     编译并压缩 CSS
  info       显示 Sass 信息和项目结构
  help       显示此帮助信息

示例:
  node compile-sass.js compile
  node compile-sass.js watch
  node compile-sass.js minify
    `);
}

// 主函数
async function main() {
    const command = process.argv[2] || 'help';
    
    switch (command) {
        case 'compile':
            await checkSassInstallation();
            await compileSass('example.scss', 'example.css', {
                style: 'expanded',
                showComparison: true
            });
            break;
            
        case 'watch':
            await checkSassInstallation();
            console.log('👀 开始监听文件变化...');
            console.log('  按 Ctrl+C 停止监听');
            exec('sass --watch example.scss:example.css', (error, stdout, stderr) => {
                if (error) {
                    console.error(`错误: ${error.message}`);
                    return;
                }
                if (stderr) {
                    console.error(`Sass 错误: ${stderr}`);
                    return;
                }
                console.log(stdout);
            });
            break;
            
        case 'minify':
            await checkSassInstallation();
            await compileSass('example.scss', 'example.min.css', {
                style: 'compressed',
                showComparison: true
            });
            break;
            
        case 'info':
            await checkSassInstallation();
            createExampleProject();
            
            // 显示当前目录的 Sass 文件
            console.log('\n📄 当前目录的 Sass 文件:');
            const files = fs.readdirSync('.');
            files.filter(file => file.endsWith('.scss') || file.endsWith('.sass'))
                .forEach(file => {
                    const stats = fs.statSync(file);
                    console.log(`  ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
                });
            break;
            
        case 'help':
        default:
            showHelp();
            break;
    }
}

// 运行主函数
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    checkSassInstallation,
    compileSass,
    analyzeSassFeatures
};