import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '许可证管理系统',
  description: 'API 文档',
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/getting-started' },
      { text: '使用说明', link: '/manual/usage' },
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
      '/manual/': [
        {
          text: '使用说明',
          items: [
            { text: '基本使用', link: '/manual/usage' },
            { text: '许可证管理', link: '/manual/license' },
            { text: '批量操作', link: '/manual/batch' },
            { text: '导出功能', link: '/manual/export' }
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
})