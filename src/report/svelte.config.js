import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
	preprocess: vitePreprocess(),
	kit: { 
		adapter: adapter({
			// fallback: 'index.html'
		}),
		output: {
			bundleStrategy: 'inline'
		},
		router: {
			type: 'hash'
		}
	},
	vite: {
		build: {
			assetsInlineLimit: 100000000 // Effectively inline all assets
		}
	}
};

export default config;
