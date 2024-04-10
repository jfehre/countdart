import Image from "next/image";
import React, { useEffect, type ReactElement, useState } from "react";

export interface WebSocketStreamProps {
    camId: string;
    height: number;
}

export function WebSocketStream({
    camId,
    height,
}: WebSocketStreamProps): ReactElement {
    // base64 image
    const [image, setImage] = useState("/images/no_image.webp");
    const url: string = `ws://localhost:7878/api/v1/cams/ws/${camId}/live`;

    useEffect(() => {
        const ws = new WebSocket(url);

        ws.onmessage = (e) => {
            const b64String: string = e.data;
            setImage("data: image:jpeg;base64, " + b64String);
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div
            style={{
                height,
                position: "relative",
                backgroundColor: "black",
            }}
        >
            <Image
                src={image}
                alt={"Live feed"}
                fill
                style={{ objectFit: "contain" }}
            ></Image>
        </div>
    );
}
