import type { Metadata } from "next";
import { Fraunces, Source_Serif_4 } from "next/font/google";
import { SiteFooter, SiteHeader } from "@/components/SiteChrome";
import { SiteGate } from "@/components/SiteGate";
import { ScrollToTop } from "@/components/ScrollToTop";
import { SyriacPrefsProvider } from "@/components/SyriacPrefs";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-source-serif",
  display: "swap",
});

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

export const metadata: Metadata = {
  title: {
    default: "Hudra — ܚܘܼܕܪܵܐ",
    template: "%s · Hudra",
  },
  description:
    "Browse the Syriac prayers of the East Syriac Hudra, organized by liturgical season.",
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
    shortcut: "/favicon.svg",
    apple: "/mark.svg",
  },
};

/** Apply saved font/size before paint to avoid a flash of defaults. */
const syriacPrefsBoot = `(function(){try{var F={adiabene:"East Syriac Adiabene",ctesiphon:"East Syriac Ctesiphon",ramsina:"Ramsina",idiqlat:"Idiqlat","malankara-classical":"East Syriac Malankara Classical",malankara:"East Syriac Malankara"};var S={sm:"0.9",md:"1",lg:"1.15",xl:"1.3"};var f=localStorage.getItem("hudra.syriacFont");var s=localStorage.getItem("hudra.syriacSize");var fam=F[f]||F.adiabene;var sc=S[s]||"1";var r=document.documentElement;r.style.setProperty("--font-syriac",'"'+fam+'", serif');r.style.setProperty("--syr-scale",sc);if(f)r.dataset.syrFont=f;if(s)r.dataset.syrSize=s}catch(e){}})();`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${sourceSerif.variable}`}>
      <head>
        <link rel="stylesheet" href={`${basePath}/syriac-fonts.css`} />
        <link rel="icon" href={`${basePath}/favicon.svg`} type="image/svg+xml" />
        <script dangerouslySetInnerHTML={{ __html: syriacPrefsBoot }} />
      </head>
      <body className="flex min-h-screen flex-col antialiased">
        <SyriacPrefsProvider>
          <ScrollToTop />
          <SiteGate>
            <SiteHeader />
            <div className="flex-1">{children}</div>
            <SiteFooter />
          </SiteGate>
        </SyriacPrefsProvider>
      </body>
    </html>
  );
}
