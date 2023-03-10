/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type JygMsgV0Schema = AnyMessage;
export type AnyMessage = AnyRequest | AnyResponse;
export type AnyRequest = AppInfoRequest | RunRequest;
export type AnyContent =
  | {
      [k: string]: unknown;
    }
  | string
  | number
  | boolean
  | unknown[]
  | null;
export type MessageTypeAppInfo = 'app_info';
export type MessageTypeRun = 'run';
export type AnyResponse = AnyValidResponse | ErrorResponse;
export type AnyValidResponse = AppInfoResponse | RunResponse;
export type AnyMessageType = MessageTypeRun | MessageTypeAppInfo;

export interface AppInfoRequest {
  content?: AnyContent;
  request_id: string;
  request_type: MessageTypeAppInfo;
}
export interface RunRequest {
  content: RunRequestContent;
  request_id: string;
  request_type: MessageTypeRun;
}
export interface RunRequestContent {
  args: {
    [k: string]: unknown;
  };
  id: string;
}
export interface AppInfoResponse {
  content: AppInfo;
  request_id: string;
  request_type: MessageTypeAppInfo;
}
export interface AppInfo {
  commands: CommandsInfo;
  name: string;
  plugins: string[];
  title: string;
  url: string;
  version: string;
}
export interface CommandsInfo {
  [k: string]: CommandInfo;
}
export interface CommandInfo {
  caption?: string;
  className?: string;
  dataset?: {
    [k: string]: unknown;
  };
  icon?: string | null;
  iconClass?: string;
  iconLabel?: string;
  isEnabled?: boolean;
  isToggleable?: boolean;
  isToggled?: boolean;
  isVisible?: boolean;
  label?: string;
  mnemonic?: string | number;
  usage?: string;
}
export interface RunResponse {
  content: AnyContent;
  request_id: string;
  request_type: MessageTypeAppInfo;
}
export interface ErrorResponse {
  error: string;
  request_id: string;
  request_type: AnyMessageType;
}
