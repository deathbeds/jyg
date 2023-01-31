import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { IFrame, MainAreaWidget } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { LabIcon } from '@jupyterlab/ui-components';
import { PromiseDelegate } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import type nunjucks from 'nunjucks';

import * as BOARD_HTML from '../style/board.html';

import * as B from './_boards';
import * as M from './_msgV0';
import * as I from './icons';
import {
  IBoardManager,
  IRemoteCommandManager,
  IWindowProxyCommandSource,
  CSS,
} from './tokens';

export interface IBoardManagerOptions {
  windowProxy: IWindowProxyCommandSource;
  remoteCommands: IRemoteCommandManager;
  shell: JupyterFrontEnd.IShell;
}

const BOARD_URL = BOARD_HTML.default;
const DEFAULT_LAUNCH_AREA = 'right';

let _N: null | typeof nunjucks = null;

const AREAS: B.LaunchArea[] = ['main', 'left', 'right', 'popup'];

export class BoardManager implements IBoardManager {
  protected _windowProxy: IWindowProxyCommandSource;
  protected _settings: ISettingRegistry.ISettings | null = null;
  protected _boardsChanged = new Signal<IBoardManager, void>(this);
  protected _remoteCommands: IRemoteCommandManager;
  protected _boards = new Map<string, B.CommandBoard>();
  protected _shell: JupyterFrontEnd.IShell;
  protected _icons = new Map<string, LabIcon>();
  protected _nextIcon = 0;
  protected _realUrl = new PromiseDelegate<string>();
  protected _widgets: Widget[] = [];

  constructor(options: IBoardManagerOptions) {
    this._windowProxy = options.windowProxy;
    this._remoteCommands = options.remoteCommands;
    this._shell = options.shell;
    this.getRealUrl().catch(console.warn);
  }

  async getRealUrl() {
    const res = await fetch(BOARD_URL);
    const text = await res.text();

    const realName = text.match(/[^"]+\.html/);

    if (realName == null) {
      this._realUrl.reject(`Couldn't find real board URL.`);
      return;
    }

    const realUrl = BOARD_URL.replace(/([^/]+.html)/, realName[0]);

    this._realUrl.resolve(realUrl);
  }

  get realUrl(): Promise<string> {
    return this._realUrl.promise;
  }

  get boardsChanged(): ISignal<IBoardManager, void> {
    return this._boardsChanged;
  }

  get boardIds(): string[] {
    return [...this._boards.keys()];
  }

  get composite(): B.CommandBoards {
    return (this._settings?.composite || {}) as B.CommandBoards;
  }

  onSettingsChanged = () => {
    const newBoards: Record<string, B.CommandBoard> = this.composite.boards || {};
    const boardKeys = [...this._boards.keys()];
    for (const id of boardKeys) {
      if (!newBoards[id]) {
        this._boards.delete(id);
      }
    }
    for (const [id, board] of Object.entries(newBoards)) {
      this._boards.set(id, board as any as B.CommandBoard);
    }
    this._boardsChanged.emit(void 0);
  };

  set settings(settings: ISettingRegistry.ISettings) {
    if (this._settings) {
      throw new Error('already has settings');
    }
    this._settings = settings;
    settings.changed.connect(this.onSettingsChanged);
    this.onSettingsChanged();
  }

  getBoard(id: string): B.CommandBoard | null {
    return this._boards.get(id) || null;
  }

  private async renderTemplate(
    tmpl: string,
    context: Record<string, any>
  ): Promise<string> {
    if (!_N) {
      _N = await import('nunjucks');
      _N.installJinjaCompat();
    }
    return _N.renderString(tmpl, context);
  }

  async openBoard(id: string): Promise<void> {
    let board = this._boards.get(id);

    if (!board) {
      throw new Error(`unknown board id ${id}`);
    }

    const url = await this.realUrl;

    const app = await this._remoteCommands.getAppInfo();

    const rendered = await this.renderTemplate(board.template, { app });

    const area = this.composite.launch_area || DEFAULT_LAUNCH_AREA;

    let newWindow: Window;
    if (area == 'popup') {
      newWindow = this.openPopup(url, id);
    } else {
      newWindow = this.openWidget(url, area, id, rendered, board);
    }

    this.updateWindow(newWindow, rendered, board);
  }

  openPopup(url: string, id: string): Window {
    const newWindow = window.open(url, `board-${id}`);
    if (!newWindow) {
      throw new Error(`Couldn't open window`);
    }
    return newWindow;
  }

  openWidget(
    url: string,
    area: B.LaunchArea,
    id: string,
    rendered: string,
    board: B.CommandBoard
  ): Window {
    const content = new IFrame({ sandbox: ['allow-same-origin', 'allow-scripts'] });
    content.id = `jyg-board-${id}`;
    content.url = url;

    const widget = new MainAreaWidget({ content });
    widget.addClass(CSS.frame);

    const switchArea = new SwitchArea({ area });

    switchArea.changed.connect(() => {
      const newArea = switchArea.area;
      let movedWindow: Window | null;
      if (newArea == 'popup') {
        movedWindow = this.openPopup(url, id);
        widget.dispose();
      } else {
        this._shell.add(widget, newArea);
        movedWindow = content.node.querySelector('iframe')?.contentWindow || null;
        this.handleAreaChange(newArea, widget, board);
      }

      if (!movedWindow) {
        throw new Error('No window to move to');
      }
      this.updateWindow(movedWindow, rendered, board);
    });

    widget.toolbar.addItem('switch-area', switchArea);

    const addOptions: DocumentRegistry.IOpenOptions = {};
    content.title.icon = this.getBoardIcon(board);
    this.handleAreaChange(area, widget, board);
    this._shell.add(widget, area as string, addOptions);
    this._widgets.push(widget);
    const newWindow = content.node.querySelector('iframe')?.contentWindow;
    if (!newWindow) {
      throw new Error('No window');
    }
    return newWindow;
  }

  closeAllBoards(): void {
    for (const widget of this._widgets) {
      widget.dispose();
    }
  }

  getBoardIcon(board: B.CommandBoard | null): LabIcon {
    let icon: LabIcon | null = null;
    if (board?.icon) {
      if (!this._icons.has(board.icon)) {
        this._icons.set(
          board.icon,
          new LabIcon({
            name: `jyg:custom-icon-${this._nextIcon++}`,
            svgstr: board.icon,
          })
        );
      }
      icon = this._icons.get(board.icon) || null;
    }
    return icon || I.logo;
  }

  handleAreaChange(area: B.LaunchArea, main: MainAreaWidget, board: B.CommandBoard) {
    const labShell = this._shell as ILabShell;
    const { content } = main;
    if (area == 'main') {
      content.title.label = board.title;
      content.title.caption = board.description || 'A command board';
    } else {
      content.title.label = '';
      content.title.caption = board.title;
      if (area == 'left') {
        labShell.expandLeft();
      } else if (area == 'right') {
        labShell.expandRight();
      }
    }
    this._shell.activateById(main.id);
  }

  svgToDataURI(svgstr: string) {
    return `data:image/svg+xml;base64,${btoa(svgstr)}`;
  }

  updateWindow(newWindow: Window, rendered: string, board: B.CommandBoard) {
    newWindow.addEventListener('load', () => {
      newWindow.document.body.innerHTML = rendered;
      newWindow.document.title = board.title;

      const favicon = newWindow.document.createElement('link');
      favicon.rel = 'shortcut icon';
      favicon.type = 'image/svg+xml';
      favicon.href = this.svgToDataURI(board.icon || I.logo.svgstr);

      newWindow.document.head.appendChild(favicon);

      this._windowProxy.addSource(newWindow, window.location.origin);

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
    });
  }
}

export class SwitchArea extends Widget {
  private _area: B.LaunchArea;
  private _changed = new Signal<SwitchArea, void>(this);

  get changed() {
    return this._changed;
  }

  get area() {
    return this._area;
  }

  constructor(options: ISwitchAreaOptions) {
    super(options);
    this._area = options.area;
    this.addClass(CSS.htmlSelect);
    this.addClass(CSS.defaultStyle);
    this.addClass(CSS.switchArea);
    const label = document.createElement('label');
    label.textContent = 'Move To';
    const select = document.createElement('select');
    for (const area of AREAS) {
      let opt = document.createElement('option');
      opt.value = area;
      opt.textContent = area;
      opt.title = `Move to ${area}`;
      if (area === this._area) {
        opt.selected = true;
      }
      select.appendChild(opt);
    }
    select.addEventListener('change', this.onSelect);
    this.node.appendChild(label);
    this.node.appendChild(select);
  }

  onSelect = (evt: Event) => {
    const select = evt.currentTarget as HTMLSelectElement;
    this._area = AREAS[select.selectedIndex];
    this._changed.emit(void 0);
  };
}

export interface ISwitchAreaOptions extends Widget.IOptions {
  area: B.LaunchArea;
}
