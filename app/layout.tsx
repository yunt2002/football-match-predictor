import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Football Match Predictor | KOR vs MEX",
  description: "Korea vs Mexico World Cup match prediction simulator",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
