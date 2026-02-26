/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // don't fail builds on lint errors; formatting can be fixed later
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
