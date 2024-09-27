/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
await import('./src/env.js')

/** @type {import("next").NextConfig} */
const config = {
    reactStrictMode: true,
    async rewrites() {
        return [
            {
                source: '/status',
                destination: 'http://127.0.0.1:8000/status',
            },
            {
                source: '/docs',
                destination: 'http://127.0.0.1:8000/docs',
            },
            {
                source: '/openapi.json',
                destination: 'http://127.0.0.1:8000/openapi.json',
            },
            {
                source: '/api/chat',
                destination: 'http://127.0.0.1:8000/chat',
            },
        ]
    },

    /**
     * If you are using `appDir` then you must comment the below `i18n` config out.
     *
     * @see https://github.com/vercel/next.js/issues/41980
     */
    i18n: {
        locales: ['en'],
        defaultLocale: 'en',
    },
    transpilePackages: ['geist'],
}

export default config
