import os
import json
import shutil

def create_docs_structure():
    # 基础目录
    base_dir = "docs"
    
    # 删除现有目录
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    # 创建目录结构
    os.makedirs(os.path.join(base_dir, ".vitepress/theme"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "api"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "guide"), exist_ok=True)
    
    # package.json
    package_json = {
        "type": "module",  # 添加这行
        "scripts": {
            "docs:dev": "vitepress dev",
            "docs:build": "vitepress build",
            "docs:preview": "vitepress preview"
        },
        "dependencies": {
            "vue": "^3.3.4"
        },
        "devDependencies": {
            "vitepress": "1.0.0-rc.31"
        }
    }
    
    with open(os.path.join(base_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)
    
    # config.js
    config_js = """import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '许可证管理系统',
  description: 'API 文档',
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/getting-started' },
      { text: 'API', link: '/api/auth' }
    ],
    sidebar: {
      '/guide/': [
        {
          text: '指南',
          items: [
            { text: '快速开始', link: '/guide/getting-started' },
            { text: '安装', link: '/guide/installation' }
          ]
        }
      ],
      '/api/': [
        {
          text: 'API 参考',
          items: [
            { text: '认证', link: '/api/auth' },
            { text: '许可证管理', link: '/api/license' },
            { text: '许可证验证', link: '/api/verify' }
          ]
        }
      ]
    }
  }
})"""
    
    with open(os.path.join(base_dir, ".vitepress/config.js"), "w", encoding="utf-8") as f:
        f.write(config_js)
    
    # theme/index.js
    theme_js = """import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'

export default {
  ...DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout)
  }
}"""
    
    with open(os.path.join(base_dir, ".vitepress/theme/index.js"), "w", encoding="utf-8") as f:
        f.write(theme_js)
    
    # index.md
    index_md = """---
layout: home
hero:
  name: 许可证管理系统
  text: API 文档
  tagline: 简单、高效的许可证管理解决方案
  actions:
    - theme: brand
      text: 快速开始
      link: /guide/getting-started
    - theme: alt
      text: API 文档
      link: /api/auth

features:
  - title: 简单易用
    details: 提供直观的 RESTful API 接口
  - title: 安全可靠
    details: 使用 JWT 进行身份验证
  - title: 功能完善
    details: 支持许可证生成、验证、管理等完整功能
---"""
    
    with open(os.path.join(base_dir, "index.md"), "w", encoding="utf-8") as f:
        f.write(index_md)
    
    # 创建其他文档
    docs = {
        "guide/getting-started.md": "# 快速开始\n\n## 系统要求\n\n- Python 3.8+\n- Node.js 16+\n- MySQL 5.7+",
        "guide/installation.md": "# 安装指南\n\n## 数据库配置\n\n配置数据库连接信息...",
        "api/auth.md": "# 认证 API\n\n## 登录接口\n\n用于获取访问令牌...",
        "api/license.md": "# 许可证管理 API\n\n## 生成许可证\n\n创建新的许可证...",
        "api/verify.md": "# 许可证验证 API\n\n## 验证许可证\n\n验证许可证有效性..."
    }
    
    for path, content in docs.items():
        full_path = os.path.join(base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_docs_structure()
    print("文档结构创建完成！")
    print("\n请按顺序执行以下命令：")
    print("cd docs")
    print("npm install")
    print("npm run docs:dev")