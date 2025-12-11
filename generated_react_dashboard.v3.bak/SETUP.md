
# Setup Instructions

1. Create React app:
   ```bash
   npx create-react-app pipeline-dashboard --template typescript
   cd pipeline-dashboard
   ```

2. Install Tailwind CSS:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

3. Configure Tailwind (tailwind.config.js):
   ```js
   module.exports = {
     content: ["./src/**/*.{js,jsx,ts,tsx}"],
     theme: { extend: {} },
     plugins: [],
   }
   ```

4. Add Tailwind to src/index.css:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. Replace src/App.tsx with generated code

6. Add Material Symbols to public/index.html:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" rel="stylesheet">
   ```

7. Run:
   ```bash
   npm start
   ```
