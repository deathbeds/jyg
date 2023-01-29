import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ISignal, Signal } from '@lumino/signaling';

import * as M from './_msgV0';
import {
  IBoard,
  IBoardManager,
  IRemoteCommandManager,
  IWindowProxyCommandSource,
} from './tokens';

export interface IBoardManagerOptions {
  windowProxy: IWindowProxyCommandSource;
  remoteCommands: IRemoteCommandManager;
}

export const BRIDGE = `
  ;(function(){
    window.proxyPostMessage = (sink, message) => {
      sink.postMessage(message);
    }

    window.addEventListener('message', (event) => {
      false && console.warn(event);
    });
  }).call(this);
`;

export class BoardManager implements IBoardManager {
  protected _windowProxy: IWindowProxyCommandSource;
  protected _settings: ISettingRegistry.ISettings | null = null;
  protected _boardsChanged = new Signal<IBoardManager, void>(this);
  protected _remoteCommands: IRemoteCommandManager;
  protected _boards = new Map<string, IBoard>();

  constructor(options: IBoardManagerOptions) {
    this._windowProxy = options.windowProxy;
    this._remoteCommands = options.remoteCommands;
  }

  get boardsChanged(): ISignal<IBoardManager, void> {
    return this._boardsChanged;
  }

  get boardIds(): string[] {
    return [...this._boards.keys()];
  }

  getBoard(id: string): IBoard | null {
    return this._boards.get(id) || null;
  }

  set settings(settings: ISettingRegistry.ISettings) {
    if (this._settings) {
      throw new Error('already has settings');
    }
    this._settings = settings;
    settings.changed.connect(this.onSettingsChanged);
    this.onSettingsChanged();
  }

  async openBoard(id: string): Promise<void> {
    let board = this._boards.get(id);

    if (!board) {
      throw new Error(`unknown board id ${id}`);
    }

    const { renderString } = await import('nunjucks');

    const app = await this._remoteCommands.getAppInfo();

    const rendered = renderString(board.template, { app });

    const newWindow = window.open('about:blank', `board-${id}`);

    if (!newWindow) {
      throw new Error(`couldn't open window`);
    }

    newWindow.document.body.innerHTML = rendered;
    newWindow.document.title = board.title;

    const bridge = newWindow.document.createElement('script');
    bridge.textContent = BRIDGE;
    newWindow.document.body.appendChild(bridge);

    this._windowProxy.addSource(newWindow);

    const onNodeClick = (evt: Event) => {
      const { currentTarget } = evt;
      if (!currentTarget) {
        return;
      }
      const { dataset } = currentTarget as HTMLElement;
      const request_id = 'msg-' + +new Date();
      const message = {
        request_id,
        request_type: 'run',
        content: {
          id: dataset.commandId,
          args: JSON.parse(dataset.commandArgs || '{}'),
        },
      } as M.RunRequest;

      (newWindow as any).proxyPostMessage(window, JSON.stringify(message));
    };

    const nodes = newWindow.document.querySelectorAll('[data-command-id]');

    for (const node of nodes) {
      node.addEventListener('click', onNodeClick);
    }
  }

  onSettingsChanged = () => {
    const newBoards: Record<string, IBoard> =
      (this._settings?.composite.boards as any) || {};
    const boardKeys = [...this._boards.keys()];
    for (const id of boardKeys) {
      if (!newBoards[id]) {
        this._boards.delete(id);
      }
    }
    for (const [id, board] of Object.entries(newBoards)) {
      this._boards.set(id, board as any as IBoard);
    }
    this._boardsChanged.emit(void 0);
  };
}
