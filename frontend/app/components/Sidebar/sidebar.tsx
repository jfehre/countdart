import { List } from "@mantine/core";
import Link from "next/link";
import React, { type ReactElement } from "react";

interface SidebarNavProps extends React.HTMLAttributes<HTMLElement> {
    items: Array<{
        href: string;
        title: string;
    }>;
}

export function SidebarNav({ items }: SidebarNavProps): ReactElement {
    return (
        <List>
            {items.map((item, index) => (
                <Link key={index} href={item.href}>
                    {item.title}
                </Link>
            ))}
        </List>
    );
}
