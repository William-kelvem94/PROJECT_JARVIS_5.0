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
  debug: async (...args: any[]) => {
    if (await isDebug()) console.debug(...args);
  },
  info: async (...args: any[]) => {
    if (await isDebug()) console.info(...args);
  },
  warn: async (...args: any[]) => {
    if (await isDebug()) console.warn(...args);
  },
  error: async (...args: any[]) => {
    if (await isDebug()) console.error(...args);
  },
};
