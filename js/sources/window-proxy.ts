import { ISettingRegistry } from '@jupyterlab/settingregistry';

import * as M from '../_msgV0';
import { IWindowProxyCommandSource, IRemoteCommandSource, EMOJI } from '../tokens';

import { BaseCommandSource, IOptions as _IOptions } from './_base';

export interface IOptions extends _IOptions {
  appReady: Promise<void>;
}

export class WindowProxyCommandSource
  extends BaseCommandSource<WindowProxy | Worker>
  implements IRemoteCommandSource, IWindowProxyCommandSource
{
  protected _sources: (WindowProxy | Worker)[] = [];
  protected _listening = false;
  protected _settings: ISettingRegistry.ISettings | null = null;

  async initClient(options: IOptions): Promise<any> {
    await options.appReady;
    return null;
  }

  set settings(settings: ISettingRegistry.ISettings) {
    if (this._settings) {
      throw new Error('already has settings');
    }
    this._settings = settings;
    settings.changed.connect(this.onSettingsChanged, this);
    this.onSettingsChanged();
  }

  get enabled() {
    return !!this._settings?.composite.enabled;
  }

  onSettingsChanged(): void {
    if (this._settings?.composite.enabled && this._listening) {
      this.unlisten();
    }
  }

  listen() {
    if (this.enabled) {
      window.addEventListener('message', this.onSourceMessage);
      this._listening = true;
    }
  }

  unlisten() {
    window.removeEventListener('message', this.onSourceMessage);
    this._listening = false;
    this._sources = [];
  }

  addSource(source: WindowProxy | Worker): void {
    const allowedSource = this.isAllowedSource(source as any, true);

    if (allowedSource) {
      this._sources.push(allowedSource);

      if (!this._listening) {
        this.listen();
      }
    }
  }

  removeSource(source: WindowProxy | Worker): void {
    const i = this._sources.indexOf(source);
    if (i != -1) {
      this._sources = this._sources.splice(i, 1);
    }
    if (!this._sources.length) {
      this.unlisten();
    }
  }

  protected onSourceMessage = async (ev: MessageEvent<any>): Promise<void> => {
    if (!this.enabled) {
      this.unlisten();
      return;
    }

    const { source } = ev;
    const allowedSource = this.isAllowedSource(source);
    if (allowedSource) {
      this.onRequest(JSON.parse(ev.data), allowedSource).catch(this.onError);
    }
  };

  isAllowedSource(
    source: MessageEventSource | null,
    registering = false
  ): WindowProxy | null {
    if (this.enabled && source) {
      return source as WindowProxy;
    }

    return null;
  }

  async sendResponse(
    response: M.AnyResponse,
    source: WindowProxy | Worker
  ): Promise<void> {
    source.postMessage(JSON.stringify(response));
  }

  async sendError(error: M.ErrorResponse, source: WindowProxy | Worker): Promise<void> {
    source.postMessage(JSON.stringify(error));
  }

  async onError(error: any) {
    console.error(EMOJI, 'encountered an error', error);
  }
}
