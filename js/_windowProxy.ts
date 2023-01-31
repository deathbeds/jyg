/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

/**
 * JupyterLab Commands from other windows
 */
export interface RemoteCommandsWindow {
  /**
   * Allow other windows to list and execute commands.
   */
  enabled?: boolean;
  /**
   * Patterns for origins allowed to list and execute commands
   */
  allowed_origins?: string[];
  /**
   * Allow listing and executing commmands from this app's base URL
   */
  allow_same_origin?: boolean;
  [k: string]: unknown;
}
