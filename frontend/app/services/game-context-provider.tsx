import React, {
    type ReactElement,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";
import { type AllMessage, type ResultMessage } from "../types/schemas";
import { notifications } from "@mantine/notifications";

export interface GameContextType {
    currentCls: string;
    currentResult: string;
}

export const GameContext = createContext<GameContextType | undefined>(
    undefined,
);

export interface GameContextProviderProps {
    children: ReactElement;
}

export interface GameContextMessage {
    message_type: string;
    payload: string;
}

export function GameContextProvider({
    children,
}: GameContextProviderProps): ReactElement {
    const [currentCls, setCurrentCls] = useState("none");
    const [currentResult, setCurrentResult] = useState("");

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:7878/api/v1/game/ws");
        ws.onmessage = (event) => {
            const rawMessage: string = event.data;
            try {
                const message: AllMessage = JSON.parse(rawMessage);
                // check if undefinded
                if (message.type === "result") {
                    const resultMessage = message as ResultMessage;
                    setCurrentCls(resultMessage.cls);
                    if (
                        resultMessage.cls === "dart" &&
                        resultMessage.content !== undefined
                    ) {
                        setCurrentResult(resultMessage.content.score);
                    }
                } else if (message.type === "error") {
                    notifications.show({
                        title: "Error",
                        message: message.content,
                        color: "red",
                    });
                } else {
                    notifications.show({
                        title: "Error",
                        message: "received unknown message: " + rawMessage,
                        color: "red",
                    });
                }
            } catch (error: any) {
                notifications.show({
                    title: "Error",
                    message: "Could not parse message: " + rawMessage,
                    color: "red",
                });
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <GameContext.Provider value={{ currentCls, currentResult }}>
            {children}
        </GameContext.Provider>
    );
}

export const useGameContext = (): GameContextType => {
    const context = useContext(GameContext);
    if (context === undefined) {
        throw new Error(
            "useGameContext must be used within a GameContextProvider",
        );
    }

    return context;
};
