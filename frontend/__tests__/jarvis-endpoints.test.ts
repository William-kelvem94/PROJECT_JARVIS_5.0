import { jarvisApi, telemetryApi } from '@/lib/jarvis-endpoints';

describe('jarvis endpoint helpers', () => {
  test('uses the Next proxy defaults when no explicit base URL is provided', () => {
    expect(jarvisApi('/health')).toBe('/jarvis-api/health');
    expect(telemetryApi('/history')).toBe('/jarvis-api/telemetry/history');
  });

  test('normalizes slashes and keeps query strings intact', () => {
    expect(jarvisApi('screenshots/latest.png?t=1', '/jarvis-api/')).toBe(
      '/jarvis-api/screenshots/latest.png?t=1'
    );
    expect(telemetryApi('status', '/jarvis-telemetry/api/')).toBe('/jarvis-telemetry/api/status');
  });

  test('falls back to proxy defaults when environment-style overrides are empty', () => {
    expect(jarvisApi('/logs', '   ')).toBe('/jarvis-api/logs');
    expect(telemetryApi('/status', '')).toBe('/jarvis-api/telemetry/status');
  });

  test('maps the dedicated telemetry dashboard base to its /api endpoints', () => {
    expect(telemetryApi('/status', '/jarvis-telemetry')).toBe('/jarvis-telemetry/api/status');
    expect(telemetryApi('/status', 'http://localhost:8001')).toBe(
      'http://localhost:8001/api/status'
    );
  });
});
