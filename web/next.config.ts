import type { NextConfig } from "next";

/**
 * For project sites (user.github.io/repo), set BASE_PATH=/repo when building.
 * User/org sites (user.github.io) leave BASE_PATH empty.
 */
const basePath = process.env.BASE_PATH || "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  ...(basePath
    ? {
        basePath,
        assetPrefix: basePath,
      }
    : {}),
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
};

export default nextConfig;
