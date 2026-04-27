import type { Metadata } from "next";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "JARVIS 5.0",
  description: "Just A Rather Very Intelligent System - Cockpit de Controle",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="bg-black text-white antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
