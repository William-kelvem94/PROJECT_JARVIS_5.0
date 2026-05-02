import { render, screen } from '@testing-library/react';
import { ConsolePanel } from '@/components/cockpit/console-panel';

test('renders empty console text when no logs', () => {
  render(<ConsolePanel logs={[]} emptyText="No logs yet." />);
  expect(screen.getByText('No logs yet.')).toBeInTheDocument();
});
