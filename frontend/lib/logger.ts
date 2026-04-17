import { getAppConfig } from './utils';

async function isDebug() {
  try {
    const config = await getAppConfig(new Headers());
    return config.debug === true;
  } catch {
    return false;
  }
}

export const log = {
  debug: async (...args: Parameters<typeof console.debug>) => {
    if (await isDebug()) console.debug(...args);
  },
  info: async (...args: Parameters<typeof console.info>) => {
    if (await isDebug()) console.info(...args);
  },
  warn: async (...args: Parameters<typeof console.warn>) => {
    if (await isDebug()) console.warn(...args);
  },
  error: async (...args: Parameters<typeof console.error>) => {
    if (await isDebug()) console.error(...args);
  },
};
