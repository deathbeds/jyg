import { URLExt, PageConfig } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { PromiseDelegate } from '@lumino/coreutils';

import * as M from '../_msgV0';
import { EMOJI, IRemoteCommandManager, IRemoteCommandSource } from '../tokens';

import { BaseCommandSource } from './_base';

export const API_URL = URLExt.join(PageConfig.getBaseUrl(), 'jyg');
export const WS_URL = URLExt.join(API_URL, 'ws').replace(/^http/, 'ws');

export interface IOptions {
  serverSettings: ServerConnection.ISettings;
  remoteCommands: IRemoteCommandManager;
}

export class WebSocketCommandSource
  extends BaseCommandSource<WebSocket>
  implements IRemoteCommandSource
{
  protected _ready = new PromiseDelegate<void>();

  async initClient(options: IOptions): Promise<WebSocket> {
    const ws = new options.serverSettings.WebSocket(WS_URL);
    ws.onopen = () => this._ready.resolve();
    ws.onmessage = this.onMessage;
    ws.onclose = this.onClose;
    ws.onerror = this.onError;
    return ws;
  }

  protected onMessage = async (ev: MessageEvent<any>): Promise<void> => {
    this.onRequest(JSON.parse(ev.data), this._client!).catch(this.onError);
  };

  async sendResponse(response: M.AnyResponse): Promise<void> {
    this._client!.send(JSON.stringify(response));
  }

  async sendError(error: M.ErrorResponse): Promise<void> {
    this._client!.send(JSON.stringify(error));
  }

  /* istanbul ignore next */
  protected onClose = async (ev: Event) => {
    console.warn(EMOJI, 'websocket was closed', ev);
  };

  /* istanbul ignore next */
  protected onError = async (ev: Event) => {
    console.error(EMOJI, 'encountered a websocket error', ev);
  };
}
