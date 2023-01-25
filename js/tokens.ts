import { Token } from '@lumino/coreutils';

import * as _PACKAGE from '../package.json';

export const PACKAGE = _PACKAGE;

import * as M from './_msgV0';

export const NS = PACKAGE.name;
export const VERSION = PACKAGE.version;
export const PLUGIN_ID = `${NS}:plugin`;

export const IRemoteCommandManager = new Token<IRemoteCommandManager>(
  `${PLUGIN_ID}:IRemoteCommandManager`
);

export interface IRemoteCommandManager {
  addSource(id: string, options: IRemoteCommandSource): void;
  getAppInfo(): Promise<M.AppInfo>;
  run(commandId: string, args: any): Promise<any>;
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
