import React, {
    type ReactElement,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

const ws = new WebSocket(
    "ws://localhost:7878/api/v1/cams/ws/67c747899ec039fb291e8b15/live",
);

export interface GameContextType {
    isReady: boolean;
}

export const GameContext = createContext<GameContextType | undefined>(
    undefined,
);

export interface GameContextProviderProps {
    children: ReactElement;
}

export function GameContextProvider({
    children,
}: GameContextProviderProps): ReactElement {
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        ws.onmessage = (event) => {
            const message: string = event.data;
            if (message === "undefined") {
                console.log("undef");
            } else if (message.startsWith("[")) {
                setIsReady(true);
                console.log(message);
            } else if (message.startsWith("/")) {
                console.log("image ");
            } else {
                console.log("else " + message);
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <GameContext.Provider value={{ isReady }}>
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
