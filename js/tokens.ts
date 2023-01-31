import { Token } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';

import * as _PACKAGE from '../package.json';

export const PACKAGE = _PACKAGE;

import * as B from './_boards';
import * as M from './_msgV0';

export const NS = PACKAGE.name;
export const VERSION = PACKAGE.version;
export const PLUGIN_ID = `${NS}:plugin`;

export const IRemoteCommandManager = new Token<IRemoteCommandManager>(
  `${NS}:IRemoteCommandManager`
);

export const IWindowProxyCommandSource = new Token<IWindowProxyCommandSource>(
  `${NS}:IWindowProxyCommandSource`
);

export const IBoardManager = new Token<IBoardManager>(`${NS}:IBoardManager`);

export interface IWindowProxyCommandSource {
  addSource(source: WindowProxy | Worker, origin: string): void;
  removeSource(source: WindowProxy | Worker): void;
}

export interface IRemoteCommandManager {
  addSource(id: string, options: IRemoteCommandSource): void;
  getAppInfo(): Promise<M.AppInfo>;
  run(commandId: string, args: any): Promise<any>;
}

export interface IBoardManager {
  openBoard(id: string): Promise<void>;
  boardsChanged: ISignal<IBoardManager, void>;
  boardIds: string[];
  getBoard(id: string): B.CommandBoard | null;
}

export interface IRemoteCommandSource {
  // nothing here yet
}

export const DEBUG = window.location.href.includes('JYG_DEBUG');

// TODO: make this configurable?
export const INFO_METHODS: (keyof M.CommandInfo)[] = [
  'caption',
  'className',
  'dataset',
  'icon',
  'iconClass',
  'iconLabel',
  'isEnabled',
  'isToggleable',
  'isToggled',
  'isVisible',
  'label',
  'mnemonic',
  'usage',
];

export const EMOJI = '📺';

export const CommandIds = {
  openBoard: 'jyg:open-board',
  closeAllBoards: 'jyg:close-all-boards',
};

export const CSS = {
  frame: 'jp-Jyg-Frame',
  switchArea: 'jp-Jyg-SwitchArea',
  // lab
  htmlSelect: 'jp-HTMLSelect',
  defaultStyle: 'jp-DefaultStyle',
};
