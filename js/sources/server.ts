import { URLExt, PageConfig } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { PromiseDelegate } from '@lumino/coreutils';

import * as M from '../_msgV0';
import { DEBUG, EMOJI, IRemoteCommandManager, IRemoteCommandSource } from '../tokens';

export const API_URL = URLExt.join(PageConfig.getBaseUrl(), 'jyg');
export const WS_URL = URLExt.join(API_URL, 'ws').replace(/^http/, 'ws');

export interface IOptions {
  serverSettings: ServerConnection.ISettings;
  remoteCommands: IRemoteCommandManager;
}

export class ServerCommandSource implements IRemoteCommandSource {
  protected _remoteCommands: IRemoteCommandManager;
  protected _serverSettings: ServerConnection.ISettings;
  protected _ws: WebSocket;
  protected _ready = new PromiseDelegate<void>();

  constructor(options: IOptions) {
    this._remoteCommands = options.remoteCommands;
    this._serverSettings = options.serverSettings;
    this._ws = this._initWebSocket();
  }

  protected _initWebSocket(): WebSocket {
    const ws = new this._serverSettings.WebSocket(WS_URL);
    ws.onopen = () => this._ready.resolve();
    ws.onmessage = this.onMessage;
    ws.onclose = this.onClose;
    ws.onerror = this.onError;
    return ws;
  }

  protected onMessage = async (ev: MessageEvent) => {
    /* istanbul ignore next */
    DEBUG && console.warn(EMOJI, 'message received', ev);

    const request: M.AnyRequest = JSON.parse(ev.data);
    let responseContent: any;
    const { request_id, request_type } = request;

    switch (request_type) {
      case 'app_info':
        responseContent = await this._remoteCommands.getAppInfo();
        break;
      case 'run':
        responseContent = await this._remoteCommands.run(
          request.content.id,
          request.content.args || {}
        );
        break;
      default:
        console.warn(EMOJI, 'unexpected request', request);
        return;
    }

    let response: null | string = null;
    try {
      response = JSON.stringify({
        request_id,
        request_type,
        content: responseContent == null ? null : responseContent,
      } as M.AnyValidResponse);
    } catch (error) {
      response = JSON.stringify({
        request_id,
        request_type,
        error: `${error}`,
      } as M.ErrorResponse);
    }
    this._ws.send(response);
  };

  protected onClose = async (ev: Event) => {
    console.warn(EMOJI, 'websocket was closed', ev);
  };

  /* istanbul ignore next */
  protected onError = async (ev: Event) => {
    console.error(EMOJI, 'encountered a websocket error', ev);
  };
}
