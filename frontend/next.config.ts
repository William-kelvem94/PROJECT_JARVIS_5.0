import type { NextConfig } from 'next';

const jarvisApiUrl = process.env.NEXT_PUBLIC_JARVIS_API_URL || 'http://localhost:8000';
const telemetryProxyUrl = process.env.JARVIS_TELEMETRY_URL || 'http://localhost:8001';
const standaloneOutput = process.env.NEXT_STANDALONE === '1';

const nextConfig: NextConfig = {
  ...(standaloneOutput ? { output: 'standalone' as const } : {}),
  async rewrites() {
    return [
      {
        source: '/jarvis-api/:path*',
        destination: `${jarvisApiUrl}/:path*`,
      },
      {
        source: '/jarvis-telemetry/:path*',
        destination: `${telemetryProxyUrl}/:path*`,
      },
    ];
  },
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored:
        /hiberfil\.sys|pagefile\.sys|swapfile\.sys|DumpStack\.log|node_modules[\\/]|\.git[\\/]|\.next[\\/]/,
    };
    return config;
  },
};

export default nextConfig;
