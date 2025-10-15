import gulp from 'gulp';
import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join } from 'path';

// Configuration
const config = {
    src: 'src',
    dist: 'build',
    build: '../../out'
};

// Bundle into single HTML
export const bundle = () => {
    return new Promise((resolve) => {
        // Read all CSS files
        const cssFiles = readdirSync(join(config.dist, '_app/immutable/assets'))
            .filter(file => file.endsWith('.css'));
        const cssContent = cssFiles.map(file => 
            readFileSync(join(config.dist, '_app/immutable/assets', file), 'utf-8')
        ).join('\n');

        // Read all JS files and combine them
        const jsFiles = [
            ...readdirSync(join(config.dist, '_app/immutable/chunks'))
                .filter(file => file.endsWith('.js')),
            ...readdirSync(join(config.dist, '_app/immutable/entry'))
                .filter(file => file.endsWith('.js'))
        ];
        
        // Create a map of module names to their content
        const modules = {};
        jsFiles.forEach(file => {
            const content = readFileSync(join(config.dist, '_app/immutable', file.includes('entry') ? 'entry' : 'chunks', file), 'utf-8');
            const moduleName = file.replace('.js', '');
            modules[moduleName] = content;
        });

        // Create bundled HTML
        const bundledHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Simulation Evaluation Report</title>
    <style>${cssContent}</style>
</head>
<body data-sveltekit-preload-data="hover">
    <div>
        <script>
            // Create a module system
            const moduleCache = {};
            function require(moduleName) {
                if (moduleCache[moduleName]) return moduleCache[moduleName];
                const module = { exports: {} };
                const code = modules[moduleName];
                if (!code) throw new Error(\`Module \${moduleName} not found\`);
                const fn = new Function('module', 'exports', 'require', code);
                fn(module, module.exports, require);
                moduleCache[moduleName] = module.exports;
                return module.exports;
            }

            // Load all modules
            ${Object.entries(modules).map(([name, code]) => code).join('\n')}

            // Initialize the app
            const element = document.currentScript.parentElement;
            const kit = require('start.C80zu3jn');
            const app = require('app.B7a6G7mS');
            kit.start(app, element);
        </script>
    </div>
</body>
</html>`;

        // Write the bundled HTML file
        writeFileSync(join(config.build, 'report.html'), bundledHtml);
        resolve();
    });
};

// Build task
export const build = gulp.series(bundle);

// Default task
export default build; 