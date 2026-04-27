import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored:
        /C:\\hiberfil\.sys|C:\\pagefile\.sys|C:\\swapfile\.sys|C:\\DumpStack\.log|node_modules[\\/]|\.git[\\/]|\.next[\\/]/,
    };
    return config;
  },
};

export default nextConfig;
