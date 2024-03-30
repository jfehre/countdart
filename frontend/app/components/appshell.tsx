"use client";

import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { SidebarNav } from "./Sidebar/sidebar";
import React, { type ReactElement } from "react";
import { Notifications } from "@mantine/notifications";

/**
 * This is the main app shell and renders the navbar, header and footer
 *
 * @param param0
 * @returns
 */
export function MainAppShell({
    children,
}: {
    children: React.ReactNode;
}): ReactElement {
    const [opened, { toggle: toggleNavbar }] = useDisclosure();

    return (
        <AppShell
            header={{
                height: { base: 40, xs: 0 },
            }}
            navbar={{
                width: 200,
                breakpoint: "xs",
                collapsed: { mobile: !opened },
            }}
            footer={{ height: 20 }}
            padding="md"
        >
            <AppShell.Header>
                <Burger
                    opened={opened}
                    onClick={toggleNavbar}
                    hiddenFrom="xs"
                    size="xs"
                />
            </AppShell.Header>
            <AppShell.Navbar>
                <SidebarNav />
            </AppShell.Navbar>
            <AppShell.Main>
                <Notifications />
                {children}
            </AppShell.Main>
            <AppShell.Footer></AppShell.Footer>
        </AppShell>
    );
}
