/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // don't fail builds on lint errors; formatting can be fixed later
    ignoreDuringBuilds: true,
  },
  webpack: (config, { dev, isServer }) => {
    if (dev) {
      config.watchOptions = {
        ...config.watchOptions,
        ignored: /node_modules|DumpStack\.log\.tmp|hiberfil\.sys|pagefile\.sys|swapfile\.sys/,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
