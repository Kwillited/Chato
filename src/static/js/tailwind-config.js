tailwind.config = {
  // 配置深色模式策略为class模式
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        1:{
          primary:'#F8FAFC',  // 主底色/极浅灰色 (#F8FAFC)

          neutral: '#94A3B8', // 中灰色 (#94A3B8) - 中性文本或边框
          success: '#10B981', // 绿色 (#10B981) - 成功状态提示
          warning: '#F59E0B', // 橙色 (#F59E0B) - 警告或需要注意的元素

          primaryAccent: '#4F46E5', // 深紫色 (#4F46E5) - 按钮点缀
        },

        dark:{
          // 主色调：灰蓝系列（背景层级）
          'primary': '#1a2435',    // 主底色：深灰蓝
          'bg-secondary': '#253146',  // 次级背景：浅灰蓝
          'bg-tertiary': '#2d3b55',   // 三级背景：更浅灰蓝（卡片/输入框）

          // 文本色
          'text-primary': '#e0e6ed',  // 主文本：浅灰（保证可读性）
          'text-secondary': '#a0aec0',// 次级文本：浅灰蓝（弱化信息）

          // 交互色：蓝紫系列
          'accent': {
            primary: '#6373f5',       // 主交互色：浅蓝紫（按钮/选中态）
            secondary: '#826af9'      // 次交互色：深一点蓝紫（hover/高亮）
          },

          // 功能色
          'border': '#384764',        // 边框色：灰蓝
          'success': '#4ade80',       // 成功色：浅绿
          'warning': '#facc15',        // 警告色：浅黄
          
          // 自定义阴影（适合夜间模式的弱对比阴影）
          'boxShadow': {
            'b-soft': '0 2px 8px rgba(0, 0, 0, 0.15)',
            'b-hover': '0 4px 12px rgba(0, 0, 0, 0.2)'
          }

        },

        primary: '#4F46E5', // 深紫色 (#4F46E5) - 主色调，用于重要按钮、标题等关键元素
        secondary: '#6366F1', // 中蓝色 (#6366F1) - 辅助色，用于次要按钮、高亮等，备选#818CF8
        //dark: '#1E293B', // 深灰色 (#1E293B) - 深色背景或文本
        light: '#FFFFFF', // 白色 (#FFFFFF) - 浅色背景，用于卡片、输入框等
        neutral: '#94A3B8', // 中灰色 (#94A3B8) - 中性文本或边框
        success: '#10B981', // 绿色 (#10B981) - 成功状态提示
        warning: '#F59E0B', // 橙色 (#F59E0B) - 警告或需要注意的元素
        // 深色模式专用颜色变体
        'dark-800': '#1E293B', // 深灰色背景（主深色背景）
        'dark-700': '#475569', // 更浅的深灰色背景（嵌套深色背景），提供更好的层次感
        'dark-600': '#334155', // 中等深灰色背景
        'dark-500': '#64748b'  // 浅深灰色背景
        
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 12px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1)', // 卡片悬停阴影，增强立体感
        'card-hover': '0 10px 25px rgba(0, 0, 0, 0.07), 0 4px 10px rgba(0, 0, 0, 0.05)', // 卡片悬停时的增强阴影
        dropdown: '0 10px 25px rgba(0, 0, 0, 0.1), 0 6px 10px rgba(0, 0, 0, 0.05)', // 下拉菜单悬停时的增强阴影
        panel: '0 0 15px rgba(0, 0, 0, 0.05), 2px 0 10px rgba(0, 0, 0, 0.03)', // 面板组件的阴影效果，用于突出显示内容区域
        // 深色模式阴影变体
        'card-dark': '0 4px 12px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.25)',
        'dropdown-dark': '0 10px 25px rgba(0, 0, 0, 0.2), 0 6px 10px rgba(0, 0, 0, 0.15)',
        'panel-dark': '0 0 15px rgba(0, 0, 0, 0.2), 2px 0 10px rgba(0, 0, 0, 0.15)',
      },

      // 统一过渡动画配置
      transitionProperty: {
        'all': 'all',
        'colors': 'background-color, border-color, color, fill, stroke',
      },
      transitionDuration: {
        '300': '300ms',
      },
      transitionTimingFunction: {
        'ease': 'ease',
      },
    },
  },

  // 添加全局深色模式选择器，确保与现有的条件类名方案兼容
  variants: {
    extend: {
      backgroundColor: ['dark'],
      textColor: ['dark'],
      borderColor: ['dark'],
      boxShadow: ['dark'],
    },
  },
};
