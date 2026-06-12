import "./globals.css";

export const metadata = {
  title: "Agentic Property Operations",
  description: "Multi-agent property management dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

