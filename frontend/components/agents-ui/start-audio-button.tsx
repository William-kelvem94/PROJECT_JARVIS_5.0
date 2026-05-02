import { type ComponentProps } from 'react';
import { Button } from '@/components/ui/button';

/**
 * Props for the StartAudioButton component.
 */
export interface StartAudioButtonProps extends ComponentProps<'button'> {
  /**
   * The size of the button.
   * @defaultValue 'default'
   */
  size?: 'default' | 'sm' | 'lg' | 'icon' | 'icon-sm' | 'icon-lg';
  /**
   * The variant of the button.
   * @defaultValue 'default'
   */
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  /**
   * The label text to display on the button.
   */
  label: string;
}

/**
 * A button that allows users to start audio playback.
 */
export function StartAudioButton({
  size = 'default',
  variant = 'default',
  label,
  ...props
}: StartAudioButtonProps) {
  return (
    <Button size={size} variant={variant} {...props}>
      {label}
    </Button>
  );
}
