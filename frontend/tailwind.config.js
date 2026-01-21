/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // Backgrounds
                main: '#09090b',      // zinc-950
                sidebar: '#18181b',   // zinc-900
                panel: '#27272a',     // zinc-800
                hover: '#27272a',     // zinc-800 (Item Hover)
                active: 'rgba(30, 58, 138, 0.4)', // bg-blue-900/40

                // Text
                primary: '#f4f4f5',   // zinc-100
                secondary: '#a1a1aa', // zinc-400
                muted: '#52525b',     // zinc-600
                accent: '#60a5fa',    // blue-400
                'file-item': '#38bdf8', // sky-400

                // Borders
                'border-main': '#27272a', // zinc-800

                // Brand
                brand: '#2563eb',     // blue-600
                'brand-hover': '#1d4ed8', // blue-700
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ], // typography 플러그인 제거 (심플하게)
};
