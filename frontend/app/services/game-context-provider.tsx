import React, {
    type ReactElement,
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from "react";
import { type AllMessage, type ResultMessage } from "../types/schemas";
import { notifications } from "@mantine/notifications";

/**
 * defines the type of the game context.
 */
export interface GameContextType {
    onNewResult: (callback: (result: ResultMessage) => void) => void;
}

/**
 * ReactContext to handle game messages.
 */
export const GameContext = createContext<GameContextType | undefined>(
    undefined,
);

/**
 * Properties for GameContextProvider
 */
export interface GameContextProviderProps {
    children: ReactElement;
}

/**
 * GameContextProvider to handle game messages.
 * @param children
 * @returns React component
 */
export function GameContextProvider({
    children,
}: GameContextProviderProps): ReactElement {
    // list of callbacks to call when new result is received
    const [resultCallbacks, setResultCallbacks] = useState<
        Array<(result: ResultMessage) => void>
    >([]);
    const resultCallbacksRef = useRef(resultCallbacks);

    // function to register new result callback
    const onNewResult = useCallback(
        (callback: (result: ResultMessage) => void) => {
            setResultCallbacks((prev) => {
                const newCallbacks = [...prev, callback];
                resultCallbacksRef.current = newCallbacks;
                return newCallbacks;
            });
        },
        [],
    );

    /**
     * useEffect to handle websocket messages.
     */
    useEffect(() => {
        const ws = new WebSocket("ws://localhost:7878/api/v1/game/ws");
        ws.onmessage = (event) => {
            const rawMessage: string = event.data;
            // parse message
            try {
                const message: AllMessage = JSON.parse(rawMessage);
                // check if result message was received
                if (message.type === "result") {
                    const resultMessage = message as ResultMessage;
                    // call all registered callbacks
                    resultCallbacksRef.current.forEach((callback) => {
                        callback(resultMessage);
                    });
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
        <GameContext.Provider value={{ onNewResult }}>
            {children}
        </GameContext.Provider>
    );
}

/**
 * Hook to use the game context.
 * @returns GameContextType
 */
export const useGameContext = (): GameContextType => {
    const context = useContext(GameContext);
    if (context === undefined) {
        throw new Error(
            "useGameContext must be used within a GameContextProvider",
        );
    }

    return context;
};
