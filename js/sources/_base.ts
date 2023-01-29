import { PromiseDelegate } from '@lumino/coreutils';

import { DEBUG, EMOJI, IRemoteCommandManager } from '../tokens';
import * as M from '../_msgV0';

export interface IOptions {
  remoteCommands: IRemoteCommandManager;
}

export class BaseCommandSource<T extends any = any, U extends IOptions = any> {
  protected _remoteCommands: IRemoteCommandManager;
  protected _client: T | null = null;
  protected _ready = new PromiseDelegate<void>();

  constructor(options: U) {
    this._remoteCommands = options.remoteCommands;
  }

  async initialize(options: U): Promise<void> {
    this._client = await this.initClient(options);
  }

  /* istanbul ignore next */
  protected async initClient(options: U): Promise<T> {
    return null as any;
  }

  protected onRequest = async (request: M.AnyRequest, source: T): Promise<any> => {
    await this._ready;
    /* istanbul ignore next */
    DEBUG && console.warn(EMOJI, 'message received', request);
    let responseContent: any;
    let error: any = null;
    const { request_id, request_type } = request;
    const header = { request_id, request_type };

    switch (request_type) {
      case 'app_info':
        responseContent = await this._remoteCommands.getAppInfo();
        break;
      case 'run':
        try {
          responseContent = await this._remoteCommands.run(
            request.content.id,
            request.content.args || {}
          );
        } catch (err) {
          error = err;
        }
        break;
      /* istanbul ignore next */
      default:
        console.warn(EMOJI, 'unexpected request', request);
        return {};
    }

    try {
      if (error) {
        await this.sendError({ error: `${error}`, ...header }, source);
      } else {
        await this.sendResponse({ content: responseContent, ...header } as any, source);
      }
    } catch (err) {
      await this.sendError(
        { error: `multiple errors\n${err}\n${error}`, ...header },
        source
      );
    }
  };

  /* istanbul ignore next */
  protected async sendError(error: M.ErrorResponse, source: T): Promise<void> {
    // nothing here
  }

  /* istanbul ignore next */
  protected async sendResponse(response: M.AnyValidResponse, source: T): Promise<void> {
    // nothing here
  }
}
