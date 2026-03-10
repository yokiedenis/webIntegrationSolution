/**
 * Server utilities - helper functions for server operations
 */

import net from "net";

/**
 * Wait for a port to be available (server is listening)
 * @param {string} host - Hostname (e.g., 'localhost')
 * @param {number} port - Port number
 * @param {number} timeout - Max time to wait in milliseconds
 * @param {number} interval - Check interval in milliseconds
 * @returns {Promise<boolean>} - True if port is available within timeout
 */
export function waitForPort(host, port, timeout = 30000, interval = 500) {
  return new Promise((resolve) => {
    const startTime = Date.now();

    const checkPort = () => {
      const socket = net.createConnection(port, host);

      socket.on("connect", () => {
        socket.destroy();
        resolve(true);
      });

      socket.on("error", () => {
        socket.destroy();

        if (Date.now() - startTime < timeout) {
          setTimeout(checkPort, interval);
        } else {
          resolve(false);
        }
      });

      socket.on("timeout", () => {
        socket.destroy();
      });

      socket.setTimeout(1000);
    };

    checkPort();
  });
}

/**
 * Generate a unique customer ID
 */
export function generateCustomerId() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const len = 10;
  let result = "CUST-";
  for (let i = 0; i < len; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generate a unique session ID
 */
export function generateSessionId() {
  return `session-${Date.now()}`;
}

/**
 * Generate a unique ticket ID
 */
export function generateTicketId() {
  return `TICKET-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Retry a function multiple times with exponential backoff
 */
export async function retryWithBackoff(
  fn,
  maxAttempts = 3,
  initialDelay = 1000,
  maxDelay = 10000,
) {
  let lastError;
  let delay = initialDelay;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      console.warn(
        `Attempt ${attempt}/${maxAttempts} failed: ${error.message}`,
      );

      if (attempt < maxAttempts) {
        console.log(`Retrying in ${delay}ms...`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        delay = Math.min(delay * 2, maxDelay);
      }
    }
  }

  throw lastError;
}

/**
 * Format log message with timestamp and prefix
 */
export function logWithPrefix(prefix, message, data = null) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${prefix}] ${message}`;

  if (data) {
    console.log(logMessage, data);
  } else {
    console.log(logMessage);
  }
}

export default {
  waitForPort,
  generateCustomerId,
  generateSessionId,
  generateTicketId,
  retryWithBackoff,
  logWithPrefix,
};
