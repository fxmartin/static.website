import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "m4rt1n.eu",
  description: "Professional writing and communication",
  keywords: "writing, communication, professional",
  openGraph: {
    title: "m4rt1n.eu",
    description: "Professional writing and communication",
    url: "https://m4rt1n.eu",
    siteName: "m4rt1n.eu",
    type: "website",
  },
  metadataBase: new URL("https://m4rt1n.eu"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-secondary">
        {children}
      </body>
    </html>
  );
}
