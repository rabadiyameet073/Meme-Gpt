import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Brand colors from design spec
        brand: {
          purple:        '#7C3AED',
          'purple-light':'#A78BFA',
          amber:         '#F59E0B',
          'amber-light': '#FCD34D',
        },
        // Background scale
        bg: {
          base:    '#0A0A0A',
          surface: '#141414',
          elevated:'#1E1E1E',
          hover:   '#252525',
        },
        'bg-base':     '#0A0A0A',
        'bg-surface':  '#141414',
        'bg-elevated': '#1E1E1E',
        'bg-hover':    '#252525',
        // Border scale
        border: {
          subtle:  '#2A2A2A',
          default: '#3F3F3F',
          strong:  '#525252',
        },
        // Status
        success: '#22C55E',
      },
      fontFamily: {
        sans:    ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        display: ['var(--font-space-grotesk)', 'Space Grotesk', 'sans-serif'],
        mono:    ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      fontSize: {
        'xs':   ['0.75rem',  { lineHeight: '1rem' }],
        'sm':   ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem',     { lineHeight: '1.5rem' }],
        'lg':   ['1.125rem', { lineHeight: '1.75rem' }],
        'xl':   ['1.25rem',  { lineHeight: '1.75rem' }],
        '2xl':  ['1.5rem',   { lineHeight: '2rem' }],
        '3xl':  ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl':  ['2.25rem',  { lineHeight: '2.5rem' }],
        '5xl':  ['3rem',     { lineHeight: '1' }],
        '6xl':  ['3.75rem',  { lineHeight: '1' }],
        '7xl':  ['4.5rem',   { lineHeight: '1' }],
      },
      backgroundImage: {
        'gradient-brand':  'linear-gradient(135deg, #7C3AED 0%, #A78BFA 50%, #F59E0B 100%)',
        'gradient-purple': 'linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%)',
        'gradient-dark':   'linear-gradient(180deg, #0A0A0A 0%, #141414 100%)',
        'gradient-hero':   'radial-gradient(ellipse at top, #1a0533 0%, #0A0A0A 60%)',
      },
      animation: {
        'gradient-x':    'gradient-x 3s ease infinite',
        'gradient-rotate':'gradient-rotate 4s linear infinite',
        'shimmer':        'shimmer 1.5s infinite',
        'pulse-glow':     'pulse-glow 2s ease-in-out infinite',
        'float':          'float 3s ease-in-out infinite',
        'fade-in':        'fade-in 0.4s ease-out',
        'slide-up':       'slide-up 0.3s ease-out',
        'spin-slow':      'spin 3s linear infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':       { backgroundPosition: '100% 50%' },
        },
        'gradient-rotate': {
          '0%':   { backgroundPosition: '0% 50%' },
          '50%':  { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 12px rgba(124,58,237,0.3)' },
          '50%':       { boxShadow: '0 0 24px rgba(124,58,237,0.6)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-8px)' },
        },
        'fade-in': {
          '0%':   { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'slide-up': {
          '0%':   { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'glow-purple': '0 0 20px rgba(124,58,237,0.4)',
        'glow-amber':  '0 0 20px rgba(245,158,11,0.3)',
        'card':        '0 4px 24px rgba(0,0,0,0.4)',
        'card-hover':  '0 20px 40px rgba(124,58,237,0.15)',
      },
    },
  },
  plugins: [],
};

export default config;
