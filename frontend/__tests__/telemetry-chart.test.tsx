import { render, screen } from '@testing-library/react';
import { TelemetryChart } from '@/components/cockpit/telemetry-chart';

test('renders telemetry chart no history state', () => {
  render(<TelemetryChart data={[]} />);
  expect(screen.getByText('NO_TELEMETRY_DATA // AWAITING_SIGNAL...')).toBeInTheDocument();
});
