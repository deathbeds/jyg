import { JupyterFrontEnd } from '@jupyterlab/application';
import type { LabIcon } from '@jupyterlab/ui-components';
import { JSONExt } from '@lumino/coreutils';

const { emptyObject } = JSONExt;

const emptyString = Object.freeze('');

import * as M from './_msgV0';
import {
  IRemoteCommandManager,
  IRemoteCommandSource,
  INFO_METHODS,
  EMOJI,
} from './tokens';

export interface IOptions {
  app: JupyterFrontEnd;
}

export class RemoteCommandManager implements IRemoteCommandManager {
  protected _app: JupyterFrontEnd;
  protected _sources = new Map<string, IRemoteCommandSource>();
  protected _commandsInfo: M.CommandsInfo = {};
  protected _skipCommandMethod = new Map<[string, string], boolean>();

  constructor(options: IOptions) {
    this._app = options.app;
    this._initialize().catch(this.onInitFail);
  }

  /* istanbul ignore next */
  protected onInitFail = (error: any) => {
    console.error(EMOJI, `failed to initialize`, error);
  };

  protected async _initialize() {
    await this._app.started;
  }

  public addSource(id: string, source: IRemoteCommandSource) {
    /* istanbul ignore if */
    if (this._sources.has(id)) {
      throw new Error(`${id} source already registered`);
    }
    this._sources.set(id, source);
  }

  public getAppInfo = async (): Promise<M.AppInfo> => {
    const commands = await this.getCommandsInfo();
    const appInfo = {
      url: `${window.location.origin}${window.location.pathname}`,
      version: this._app.version,
      plugins: this._app.listPlugins(),
      name: this._app.name,
      title: document.title,
      commands,
    };
    return appInfo;
  };

  public run = async (commandId: string, args?: any): Promise<any> => {
    return await this._app.commands.execute(commandId, args);
  };

  public async getCommandsInfo(): Promise<M.CommandsInfo> {
    const { commands } = this._app;
    const commandsInfo: M.CommandsInfo = {};

    for (const id of commands.listCommands()) {
      const info: M.CommandInfo = (commandsInfo[id] = {});
      for (const method of INFO_METHODS) {
        if (this._skipCommandMethod.get([id, method])) {
          continue;
        }
        let value: any = null;
        try {
          value = commands[method](id, emptyObject) as any;
        } catch (error) {
          this._skipCommandMethod.set([id, method], true);
          continue;
        }

        switch (value) {
          case null:
          case undefined:
          case emptyObject:
          case emptyString:
            continue;
          default:
            break;
        }

        switch (method) {
          case 'isToggled':
          case 'isToggleable':
          case 'isVisible':
          case 'isEnabled':
            if (value == false) {
              continue;
            }
            break;
          case 'mnemonic':
            if (value == -1) {
              continue;
            }
            break;
          case 'dataset':
            if (!Object.keys(value).length) {
              continue;
            }
            break;
          case 'icon':
            if ((value as LabIcon).svgstr) {
              value = value.svgstr;
            }
            break;
          default:
            break;
        }

        info[method] = value;
      }
    }
    return commandsInfo;
  }
}
