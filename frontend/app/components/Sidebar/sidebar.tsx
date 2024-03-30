import {
    NavLink,
    Stack,
    ActionIcon,
    useMantineColorScheme,
    useComputedColorScheme,
    Image,
    Group,
} from "@mantine/core";
import { IconMoon, IconHome, IconTarget } from "@tabler/icons-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { type ReactElement, useState } from "react";

/**
 * Define Navbar items here
 */
const data = [
    { href: "/", title: "Home", icon: IconHome },
    { href: "/boardmanager", title: "Boardmanager", icon: IconTarget },
];

/**
 * Return the Navbar layout
 * @returns
 */
export function SidebarNav(): ReactElement {
    const { setColorScheme } = useMantineColorScheme({ keepTransitions: true });
    const computedColorScheme = useComputedColorScheme("light");
    const toggleColorScheme = (): void => {
        setColorScheme(computedColorScheme === "dark" ? "light" : "dark");
    };

    // active item specified by pathname
    const path = usePathname();
    const [active, setActive] = useState(path);

    return (
        <Stack h="100%" justify="space-between">
            <Stack h="75%">
                <Image
                    src="/images/logo.webp"
                    h={75}
                    w="auto"
                    fit="contain"
                    mt={30}
                    mb={30}
                />
                {data.map((item) => (
                    // add Link component to avoid rerendering
                    <NavLink
                        component={Link}
                        href={item.href}
                        key={item.href}
                        active={item.href === active}
                        label={item.title}
                        leftSection={<item.icon size="1rem" stroke={1.5} />}
                        onClick={() => {
                            setActive(item.href);
                        }}
                    />
                ))}
            </Stack>
            <Group m={20}>
                <ActionIcon
                    key="toggleTheme"
                    onClick={toggleColorScheme}
                    variant="default"
                    size="xl"
                    aria-label="Toggle color scheme"
                >
                    <IconMoon stroke={1.5} />
                </ActionIcon>
            </Group>
        </Stack>
    );
}
