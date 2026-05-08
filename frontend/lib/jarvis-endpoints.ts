export const JARVIS_API_URL = process.env.NEXT_PUBLIC_JARVIS_API_URL || '/jarvis-api';
export const TELEMETRY_URL = process.env.NEXT_PUBLIC_TELEMETRY_URL || '/jarvis-api/telemetry';

function apiUrl(baseUrl: string, path: string) {
  const base = baseUrl.replace(/\/+$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}

export function jarvisApi(path: string, baseUrl?: string) {
  return apiUrl(baseUrl?.trim() || JARVIS_API_URL, path);
}

export function telemetryApi(path: string, baseUrl?: string) {
  const base = baseUrl?.trim() || TELEMETRY_URL;
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const usesTelemetryDashboard =
    base.replace(/\/+$/, '').endsWith('/jarvis-telemetry') || /:8001\/?$/.test(base);

  return apiUrl(
    base,
    usesTelemetryDashboard && !normalizedPath.startsWith('/api/')
      ? `/api${normalizedPath}`
      : normalizedPath
  );
}
