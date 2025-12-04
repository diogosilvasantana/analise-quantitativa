type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const LOG_LEVELS: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
};

const CURRENT_LOG_LEVEL = (process.env.NEXT_PUBLIC_LOG_LEVEL as LogLevel) || 'info';

const styles = {
    debug: 'color: #808080; font-weight: bold;',
    info: 'color: #00bfff; font-weight: bold;',
    warn: 'color: #ffa500; font-weight: bold;',
    error: 'color: #ff4500; font-weight: bold;',
};

class Logger {
    private shouldLog(level: LogLevel): boolean {
        return LOG_LEVELS[level] >= LOG_LEVELS[CURRENT_LOG_LEVEL];
    }

    debug(message: string, ...args: any[]) {
        if (this.shouldLog('debug')) {
            console.debug(`%c[DEBUG] ${message}`, styles.debug, ...args);
        }
    }

    info(message: string, ...args: any[]) {
        if (this.shouldLog('info')) {
            console.info(`%c[INFO] ${message}`, styles.info, ...args);
        }
    }

    warn(message: string, ...args: any[]) {
        if (this.shouldLog('warn')) {
            console.warn(`%c[WARN] ${message}`, styles.warn, ...args);
        }
    }

    error(message: string, ...args: any[]) {
        if (this.shouldLog('error')) {
            console.error(`%c[ERROR] ${message}`, styles.error, ...args);
        }
    }
}

export const logger = new Logger();
