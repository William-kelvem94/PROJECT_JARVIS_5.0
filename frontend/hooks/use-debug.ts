import * as React from 'react';

export const useDebugMode = (options: { enabled?: boolean } = {}) => {
  React.useEffect(() => {
    // Debug mode logic is disabled for the native version
  }, []);
};
