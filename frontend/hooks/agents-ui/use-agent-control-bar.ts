import { useCallback } from 'react';

export interface PublishPermissions {
  camera: boolean;
  microphone: boolean;
  screenShare: boolean;
  data: boolean;
}

export function usePublishPermissions(): PublishPermissions {
  return {
    camera: false,
    microphone: false,
    screenShare: false,
    data: false,
  };
}

export interface UseInputControlsProps {
  saveUserChoices?: boolean;
  onDisconnect?: () => void;
  onDeviceError?: (error: { source: string; error: Error }) => void;
}

export interface UseInputControlsReturn {
  micTrackRef?: unknown;
  microphoneToggle: { enabled: boolean; toggle: (enabled?: boolean) => Promise<void> };
  cameraToggle: { enabled: boolean; toggle: (enabled?: boolean) => Promise<void> };
  screenShareToggle: { enabled: boolean; toggle: (enabled?: boolean) => Promise<void> };
  handleAudioDeviceChange: (deviceId: string) => void;
  handleVideoDeviceChange: (deviceId: string) => void;
  handleMicrophoneDeviceSelectError: (error: Error) => void;
  handleCameraDeviceSelectError: (error: Error) => void;
}

export function useInputControls({
  saveUserChoices = true,
  onDeviceError,
}: UseInputControlsProps = {}): UseInputControlsReturn {
  const toggle = async () => {};

  const handleAudioDeviceChange = useCallback((deviceId: string) => {
    // No local device persistence available in this build.
  }, []);

  const handleVideoDeviceChange = useCallback((deviceId: string) => {
    // No local device persistence available in this build.
  }, []);

  const handleMicrophoneDeviceSelectError = useCallback(
    (error: Error) => onDeviceError?.({ source: 'microphone', error }),
    [onDeviceError]
  );

  const handleCameraDeviceSelectError = useCallback(
    (error: Error) => onDeviceError?.({ source: 'camera', error }),
    [onDeviceError]
  );

  return {
    micTrackRef: undefined,
    microphoneToggle: { enabled: false, toggle },
    cameraToggle: { enabled: false, toggle },
    screenShareToggle: { enabled: false, toggle },
    handleAudioDeviceChange,
    handleVideoDeviceChange,
    handleMicrophoneDeviceSelectError,
    handleCameraDeviceSelectError,
  };
}
