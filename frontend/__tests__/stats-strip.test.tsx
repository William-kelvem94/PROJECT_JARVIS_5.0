import { render, screen } from '@testing-library/react';
import { StatsStrip } from '@/components/cockpit/stats-strip';

test('renders stats strip with object names and task count', () => {
  render(<StatsStrip objects={['keyboard', 'monitor']} todos={3} />);

  expect(screen.getByText('keyboard, monitor')).toBeInTheDocument();
  expect(screen.getByText('3 tarefas')).toBeInTheDocument();
});
