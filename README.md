# Executing the code

You need to install node

check `npm -v`

then run `npm install . `
This installs locally

Then run `npm run dev`

# Explanation

puzzle_tree/
├── public/ ← static files served as-is (favicon etc)
├── src/
│ ├── App.tsx ← the root React component (we'll gut this)
│ ├── main.tsx ← entry point, mounts App into the HTML
│ └── index.css ← global styles
├── index.html ← the single HTML page (just a shell, loads main.tsx)
├── package.json ← project config + dependency list
├── tsconfig.json ← TypeScript config
└── vite.config.ts ← Vite config
