import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import '../style/index.css';

import { BoardManager } from './boards';
import { ICONS } from './icons';
import { RemoteCommandManager } from './manager';
import {
  IRemoteCommandManager,
  PLUGIN_ID,
  NS,
  CommandIds,
  IWindowProxyCommandSource,
  IBoardManager,
  IBoard,
} from './tokens';

const corePlugin: JupyterFrontEndPlugin<IRemoteCommandManager> = {
  id: PLUGIN_ID,
  autoStart: true,
  provides: IRemoteCommandManager,
  activate: (app: JupyterFrontEnd): IRemoteCommandManager => {
    const remoteCommands = new RemoteCommandManager({ app });
    return remoteCommands;
  },
};

const webSocketPlugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:websocket`,
  autoStart: true,
  requires: [IRemoteCommandManager],
  activate: async (
    app: JupyterFrontEnd,
    remoteCommands: RemoteCommandManager
  ): Promise<void> => {
    const { WebSocketCommandSource } = await import('./sources/websocket');
    const { serverSettings } = app.serviceManager;
    const options = { serverSettings, remoteCommands };
    const source = new WebSocketCommandSource(options);
    remoteCommands.addSource('websocket', source);
    source.initialize(options).catch(console.warn);
  },
};

const windowProxyPlugin: JupyterFrontEndPlugin<IWindowProxyCommandSource> = {
  id: `${NS}:window-proxy`,
  autoStart: true,
  requires: [IRemoteCommandManager, ISettingRegistry],
  optional: [ILauncher],
  provides: IWindowProxyCommandSource,
  activate: async (
    app: JupyterFrontEnd,
    remoteCommands: IRemoteCommandManager,
    settings: ISettingRegistry,
    launcher?: ILauncher
  ): Promise<IWindowProxyCommandSource> => {
    const { WindowProxyCommandSource } = await import('./sources/window-proxy');
    const options = { remoteCommands, appReady: app.started };
    const source = new WindowProxyCommandSource(options);
    remoteCommands.addSource('window-proxy', source);
    settings
      .load(windowProxyPlugin.id)
      .then((settings) => {
        source.settings = settings;
        source.initialize(options).catch(console.warn);
      })
      .catch(console.warn);
    return source;
  },
};

const boardPlugin: JupyterFrontEndPlugin<IBoardManager> = {
  id: `${NS}:boards`,
  autoStart: true,
  requires: [ISettingRegistry, IRemoteCommandManager, IWindowProxyCommandSource],
  optional: [ILauncher],
  provides: IBoardManager,
  activate: async (
    app: JupyterFrontEnd,
    settings: ISettingRegistry,
    remoteCommands: IRemoteCommandManager,
    windowProxy: IWindowProxyCommandSource,
    launcher?: ILauncher
  ) => {
    const boards = new BoardManager({ windowProxy, remoteCommands });

    const { commands } = app;

    commands.addCommand(CommandIds.openBoard, {
      icon: ICONS.logo,
      label: (args?: any): string => {
        const { id } = args;
        if (id) {
          return `Open Command Board ${boards.getBoard(id)?.title || id}`;
        }
        return 'Unknown Command Board';
      },
      execute: (args?: any) => boards.openBoard(args.id),
    });

    settings
      .load(boardPlugin.id)
      .then((settings) => {
        boards.settings = settings;
        const hasLauncher: string[] = [];

        function makeLauncherItem(boardId: string, board: IBoard) {
          launcher?.add({
            command: CommandIds.openBoard,
            metadata: board as any,
            args: { id: boardId },
            category: board.category || 'Other',
            rank: board.rank == null ? 100 : board.rank,
          });
          hasLauncher.push(boardId);
        }

        function updateLauncher() {
          for (const boardId of boards.boardIds) {
            if (hasLauncher.includes(boardId)) {
              continue;
            }
            const board = boards.getBoard(boardId);
            if (board) {
              makeLauncherItem(boardId, board);
            }
          }
        }

        boards.boardsChanged.connect(updateLauncher);

        updateLauncher();
      })
      .catch(console.warn);

    return boards;
  },
};

export default [corePlugin, webSocketPlugin, windowProxyPlugin, boardPlugin];
