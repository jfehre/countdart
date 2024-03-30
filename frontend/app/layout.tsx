import type { Metadata } from "next";
import { createTheme, MantineProvider } from "@mantine/core";
import { Inter } from "next/font/google";
import { MainAppShell } from "./components/appshell";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import React, { type ReactElement } from "react";

const inter = Inter({ subsets: ["latin"] });

/**
 * Metadata
 */
export const metadata: Metadata = {
    title: "Count Dart",
    description: "",
};

/**
 * Mantine theme
 */
const theme = createTheme({
    primaryColor: "yellow",
});

/**
 * Root Layout for all pages.
 * Adds Mantine and AppShell (Navbar, Header, Footer) to each page.
 * Can also be used to add services later on
 *
 * @param children
 * @returns
 */
export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>): ReactElement {
    return (
        <html lang="en">
            <body className={inter.className}>
                <MantineProvider theme={theme}>
                    <MainAppShell>{children}</MainAppShell>
                </MantineProvider>
            </body>
        </html>
    );
}
