export const JARVIS_API_URL = process.env.NEXT_PUBLIC_JARVIS_API_URL || '/jarvis-api';
export const TELEMETRY_URL = process.env.NEXT_PUBLIC_TELEMETRY_URL || '/jarvis-telemetry';

export function jarvisApi(path: string) {
  return `${JARVIS_API_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

export function telemetryApi(path: string) {
  return `${TELEMETRY_URL}${path.startsWith('/') ? path : `/${path}`}`;
}
