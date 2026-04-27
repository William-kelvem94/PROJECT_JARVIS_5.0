import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  webpack: (config) => {
    // watchOptions.ignored aceita: string glob, RegExp único, ou array de strings glob.
    // Usamos RegExp único combinado para cobrir arquivos de sistema do Windows
    // sem disparar o erro de schema do Webpack 5.
    config.watchOptions = {
      ...config.watchOptions,
      ignored: /hiberfil\.sys|pagefile\.sys|swapfile\.sys|DumpStack\.log|Config\.Msdos|node_modules[/\\]|\.git[/\\]|\.next[/\\]/,
    };
    return config;
  },
};

export default nextConfig;

