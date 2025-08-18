/**
 * Design System Tokens
 * Based on user's UI preferences - Modern dark theme with glass morphism
 */

export const designTokens = {
  // Color Palette - Dark theme with blue/purple accents
  colors: {
    // Primary colors - Blue gradient
    primary: {
      50: '#e6f1ff',
      100: '#b3d4ff',
      200: '#80b8ff',
      300: '#4d9bff',
      400: '#1a7eff',
      500: '#0066ff', // Main brand blue
      600: '#0052cc',
      700: '#003d99',
      800: '#002966',
      900: '#001433',
    },
    
    // Secondary colors - Purple/Violet
    secondary: {
      50: '#f3e5ff',
      100: '#dbb3ff',
      200: '#c280ff',
      300: '#aa4dff',
      400: '#921aff',
      500: '#7c3aed', // Purple accent
      600: '#6329cc',
      700: '#4a1999',
      800: '#310866',
      900: '#190033',
    },
    
    // Neutral colors - Gray scale for dark theme
    neutral: {
      50: '#fafafa',
      100: '#f4f4f5',
      200: '#e4e4e7',
      300: '#d4d4d8',
      400: '#a1a1aa',
      500: '#71717a',
      600: '#52525b',
      700: '#3f3f46',
      800: '#27272a',
      900: '#18181b',
      950: '#09090b', // Darkest background
    },
    
    // Semantic colors
    semantic: {
      success: '#10b981',
      successLight: '#34d399',
      warning: '#f59e0b',
      warningLight: '#fbbf24',
      error: '#ef4444',
      errorLight: '#f87171',
      info: '#3b82f6',
      infoLight: '#60a5fa',
    },
    
    // Special effects colors
    effects: {
      glassBg: 'rgba(255, 255, 255, 0.05)',
      glassCard: 'rgba(255, 255, 255, 0.08)',
      glassBorder: 'rgba(255, 255, 255, 0.1)',
      glassHover: 'rgba(255, 255, 255, 0.12)',
      gradient1: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      gradient2: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      gradient3: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      gradientBlue: 'linear-gradient(135deg, #0066ff 0%, #00d4ff 100%)',
      glow: '0 0 40px rgba(0, 102, 255, 0.4)',
    },
    
    // Chart colors (from your data viz screenshots)
    charts: {
      blue: '#0066ff',
      purple: '#7c3aed',
      cyan: '#06b6d4',
      emerald: '#10b981',
      amber: '#f59e0b',
      rose: '#f43f5e',
      indigo: '#6366f1',
      teal: '#14b8a6',
    }
  },
  
  // Typography System
  typography: {
    fonts: {
      sans: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', 'SF Mono', Monaco, Consolas, monospace",
      display: "'Inter', 'SF Pro Display', sans-serif",
    },
    
    sizes: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
      '6xl': '3.75rem',   // 60px
    },
    
    weights: {
      thin: 100,
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    
    lineHeights: {
      tight: 1.2,
      snug: 1.4,
      normal: 1.6,
      relaxed: 1.8,
      loose: 2,
    }
  },
  
  // Spacing System (8px base)
  spacing: {
    px: '1px',
    0: '0',
    0.5: '0.125rem',  // 2px
    1: '0.25rem',     // 4px
    2: '0.5rem',      // 8px
    3: '0.75rem',     // 12px
    4: '1rem',        // 16px
    5: '1.25rem',     // 20px
    6: '1.5rem',      // 24px
    8: '2rem',        // 32px
    10: '2.5rem',     // 40px
    12: '3rem',       // 48px
    16: '4rem',       // 64px
    20: '5rem',       // 80px
    24: '6rem',       // 96px
    32: '8rem',       // 128px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.25rem',    // 4px
    base: '0.5rem',   // 8px
    md: '0.75rem',    // 12px
    lg: '1rem',       // 16px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '2rem',    // 32px
    full: '9999px',
  },
  
  // Shadows (with glow effects for dark theme)
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    
    // Glow effects for dark theme
    glow: {
      sm: '0 0 10px rgba(0, 102, 255, 0.3)',
      md: '0 0 20px rgba(0, 102, 255, 0.4)',
      lg: '0 0 40px rgba(0, 102, 255, 0.5)',
      purple: '0 0 30px rgba(124, 58, 237, 0.4)',
      success: '0 0 20px rgba(16, 185, 129, 0.4)',
      error: '0 0 20px rgba(239, 68, 68, 0.4)',
    },
    
    // Glass morphism shadows
    glass: {
      sm: '0 2px 8px rgba(0, 0, 0, 0.1), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
      md: '0 8px 32px rgba(0, 0, 0, 0.12), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
      lg: '0 16px 64px rgba(0, 0, 0, 0.15), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
    }
  },
  
  // Animations
  animations: {
    durations: {
      fast: '150ms',
      base: '300ms',
      slow: '500ms',
      slower: '700ms',
    },
    
    easings: {
      linear: 'linear',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
    
    keyframes: {
      fadeIn: {
        '0%': { opacity: 0 },
        '100%': { opacity: 1 },
      },
      slideIn: {
        '0%': { transform: 'translateY(10px)', opacity: 0 },
        '100%': { transform: 'translateY(0)', opacity: 1 },
      },
      pulse: {
        '0%, 100%': { opacity: 1 },
        '50%': { opacity: 0.8 },
      },
      glow: {
        '0%, 100%': { boxShadow: '0 0 20px rgba(0, 102, 255, 0.4)' },
        '50%': { boxShadow: '0 0 40px rgba(0, 102, 255, 0.6)' },
      }
    }
  },
  
  // Blur effects for glass morphism
  blur: {
    none: '0',
    sm: '4px',
    base: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '40px',
  },
  
  // Z-index scale
  zIndex: {
    0: 0,
    10: 10,
    20: 20,
    30: 30,
    40: 40,
    50: 50,
    dropdown: 1000,
    sticky: 1020,
    modal: 1030,
    popover: 1040,
    tooltip: 1050,
    notification: 1060,
  }
};

export default designTokens;