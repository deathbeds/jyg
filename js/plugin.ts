import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

import '../style/index.css';

import { RemoteCommandManager } from './manager';
import { IRemoteCommandManager, PLUGIN_ID, NS } from './tokens';

const corePlugin: JupyterFrontEndPlugin<IRemoteCommandManager> = {
  id: PLUGIN_ID,
  autoStart: true,
  provides: IRemoteCommandManager,
  activate: (app: JupyterFrontEnd): IRemoteCommandManager => {
    const remoteCommands = new RemoteCommandManager({ app });
    return remoteCommands;
  },
};

const serverPlugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:server`,
  autoStart: true,
  requires: [IRemoteCommandManager],
  activate: async (
    app: JupyterFrontEnd,
    remoteCommands: RemoteCommandManager
  ): Promise<void> => {
    const { ServerCommandSource } = await import('./sources/server');
    const { serverSettings } = app.serviceManager;
    const source = new ServerCommandSource({ serverSettings, remoteCommands });
    remoteCommands.addSource('server', source);
  },
};

const iframePlugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:iframe`,
  autoStart: true,
  requires: [IRemoteCommandManager],
  activate: async (
    app: JupyterFrontEnd,
    remoteCommands: IRemoteCommandManager
  ): Promise<void> => {
    const { IFrameCommandSource } = await import('./sources/iframe');
    const source = new IFrameCommandSource({ remoteCommands });
    remoteCommands.addSource('iframe', source);
  },
};

export default [corePlugin, serverPlugin, iframePlugin];
