import * as React from 'react';
// import { LogLevel, setLogLevel } from 'livekit-client';
// import { useRoomContext } from '@livekit/components-react';

export const useDebugMode = (options: { enabled?: boolean } = {}) => {
  // const room = useRoomContext();
  // Neutralizado para Jarvis Native
  React.useEffect(() => {
    // console.log("Debug mode logic disabled for native version");
  }, []);
};
