/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#725BFF',
          hover: '#5A47CC',
          light: '#9B8AFF',
          dark: '#4A3AA3',
        },
        success: {
          DEFAULT: '#1CD6B1',
          light: '#4FE3C4',
          dark: '#16B896',
        },
        danger: {
          DEFAULT: '#F87171',
          light: '#FCA5A5',
          dark: '#EF4444',
        },
        warning: {
          DEFAULT: '#FFB74A',
          light: '#FFD699',
          dark: '#FF9500',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
          tertiary: '#9CA3AF',
        },
        bg: {
          canvas: '#F9FAFB',
          card: '#FFFFFF',
          hover: '#F3F4F6',
        },
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'panel': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      },
      fontSize: {
        'micro': '0.625rem', // 10px
      },
      animation: {
        'in': 'fadeIn 0.2s ease-in-out',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in-from-right-4': 'slideInFromRight 0.3s ease-out',
        'zoom-in-95': 'zoomIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInFromRight: {
          '0%': { transform: 'translateX(1rem)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        zoomIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

