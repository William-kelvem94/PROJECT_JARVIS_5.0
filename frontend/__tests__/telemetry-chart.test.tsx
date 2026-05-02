import { render, screen } from '@testing-library/react';
import { TelemetryChart } from '@/components/cockpit/telemetry-chart';

test('renders telemetry chart no history state', () => {
  render(<TelemetryChart history={[]} />);
  expect(screen.getByText('No telemetry history available.')).toBeInTheDocument();
});
