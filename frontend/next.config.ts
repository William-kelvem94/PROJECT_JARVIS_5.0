import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored: /hiberfil\.sys|pagefile\.sys|swapfile\.sys|DumpStack\.log|node_modules[\\/]|\.git[\\/]|\.next[\\/]/,
    };
    return config;
  },
};

export default nextConfig;
