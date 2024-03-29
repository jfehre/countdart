"use client";

import { AppShell } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { SidebarNav } from "./Sidebar/sidebar";
import React, { type ReactElement } from "react";

export function MainAppShell({
    children,
}: {
    children: React.ReactNode;
}): ReactElement {
    const [opened] = useDisclosure();

    return (
        <AppShell
            navbar={{
                width: 200,
                breakpoint: "sm",
                collapsed: { mobile: !opened },
            }}
            footer={{ height: 20 }}
            padding="md"
        >
            <AppShell.Navbar>
                <SidebarNav
                    items={[{ href: "boardmanager", title: "Boardmanager" }]}
                ></SidebarNav>
            </AppShell.Navbar>
            <AppShell.Main>{children}</AppShell.Main>
            <AppShell.Footer></AppShell.Footer>
        </AppShell>
    );
}
