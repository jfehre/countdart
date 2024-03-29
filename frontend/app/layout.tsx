import type { Metadata } from "next";
import { MantineProvider } from "@mantine/core";
import { Inter } from "next/font/google";
import { MainAppShell } from "./components/appshell";
import "@mantine/core/styles.css";
import React, { type ReactElement } from "react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Count Dart",
    description: "",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>): ReactElement {
    return (
        <html lang="en">
            <body className={inter.className}>
                <MantineProvider>
                    <MainAppShell>{children}</MainAppShell>
                </MantineProvider>
            </body>
        </html>
    );
}
