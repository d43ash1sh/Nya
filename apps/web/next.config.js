/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL;
    if (backendUrl) {
      return [
        {
          source: "/api/v1/:path*",
          destination: `${backendUrl.replace(/\/$/, "")}/api/v1/:path*`,
        },
      ];
    }
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/v1/:path*",
          destination: "http://127.0.0.1:8000/api/v1/:path*",
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;
