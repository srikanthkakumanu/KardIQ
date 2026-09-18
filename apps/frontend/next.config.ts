import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a minimal .next/standalone server so the runtime Docker image
  // doesn't need node_modules or the full build tree.
  output: "standalone",
};

export default nextConfig;
