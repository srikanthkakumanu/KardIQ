import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Knowledge Card Assistant",
  description: "Ask questions grounded in your knowledge cards and graph relationships.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
