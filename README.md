# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
    "$schema": "./node_modules/oxlint/configuration_schema.json",
    "plugins": ["react", "typescript", "oxc"],
    "options": {
        "typeAware": true
    },
    "rules": {
        "react/rules-of-hooks": "error",
        "react/only-export-components": [
            "warn",
            { "allowConstantExport": true }
        ]
    }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.

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



You need to install node 

check `npm -v` 

then run `npm install . `
This installs locally

Then run `npm run dev`


