import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
<<<<<<< HEAD
  // Turbopack (padrão no next dev do Next 15) — sem config extra necessária
  // webpack abaixo é usado apenas para `next build` (produção)
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      // RegExp único: Webpack 5 aceita string glob, RegExp único, ou array de strings glob
      ignored: /hiberfil\.sys|pagefile\.sys|swapfile\.sys|DumpStack\.log|node_modules[\\/]|\.git[\\/]|\.next[\\/]/,
=======
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored:
        /C:\\hiberfil\.sys|C:\\pagefile\.sys|C:\\swapfile\.sys|C:\\DumpStack\.log|node_modules[\\/]|\.git[\\/]|\.next[\\/]/,
>>>>>>> main
    };
    return config;
  },
};

export default nextConfig;

