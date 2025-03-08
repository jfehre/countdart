import React, {
    type ReactElement,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";
import { type CamDetectionSchema } from "../types/schemas";

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
            try {
                const rawMessage: string = event.data;
                const message: GameContextMessage = JSON.parse(rawMessage);
                if (message.message_type === "result") {
                    const payload: CamDetectionSchema = JSON.parse(
                        message.payload,
                    );
                    const cls = payload[0];
                    setCurrentCls(cls);
                    console.log(payload[1]);
                    if (cls === "dart" && payload[1] !== undefined) {
                        console.log("setting result");
                        setCurrentResult(payload[1].score);
                    }
                    console.log(currentResult);
                } else {
                    console.log("Unknown message type");
                }
            } catch (error: any) {
                console.error(error.message);
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
