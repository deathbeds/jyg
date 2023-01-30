import { JupyterFrontEnd, ILabShell } from '@jupyterlab/application';
import { IFrame, MainAreaWidget } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { LabIcon } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import type nunjucks from 'nunjucks';

import * as B from './_boards';
import * as M from './_msgV0';
import { ICONS } from './icons';
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

const DEFAULT_LAUNCH_AREA = 'right';

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

  constructor(options: IBoardManagerOptions) {
    this._windowProxy = options.windowProxy;
    this._remoteCommands = options.remoteCommands;
    this._shell = options.shell;
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

    const app = await this._remoteCommands.getAppInfo();

    const rendered = await this.renderTemplate(board.template, { app });

    const area = this.composite.launch_area || DEFAULT_LAUNCH_AREA;

    let newWindow: Window;
    if (area == 'popup') {
      newWindow = this.openPopup(id);
    } else {
      newWindow = this.openWidget(area, id, rendered, board);
    }

    this.updateWindow(newWindow, rendered, board);
  }

  openWidget(
    area: B.LaunchArea,
    id: string,
    rendered: string,
    board: B.CommandBoard
  ): Window {
    const content = new IFrame({ sandbox: ['allow-same-origin', 'allow-scripts'] });
    content.id = `jyg-board-${id}`;
    content.url = 'about:blank';

    const widget = new MainAreaWidget({ content });
    widget.addClass(CSS.frame);

    const switchArea = new SwitchArea({ area });

    switchArea.changed.connect(() => {
      const newArea = switchArea.area;
      let movedWindow: Window | null;
      if (newArea == 'popup') {
        movedWindow = this.openPopup(id);
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
    const newWindow = content.node.querySelector('iframe')?.contentWindow;
    if (!newWindow) {
      throw new Error('No window');
    }
    return newWindow;
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
    return icon || ICONS.logo;
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

  openPopup(id: string): Window {
    const newWindow = window.open('about:blank', `board-${id}`);
    if (!newWindow) {
      throw new Error(`Couldn't open window`);
    }
    return newWindow;
  }

  updateWindow(newWindow: Window, rendered: string, board: B.CommandBoard) {
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
