import { IRemoteCommandManager, IRemoteCommandSource } from '../tokens';

export interface IOptions {
  remoteCommands: IRemoteCommandManager;
}

export class IFrameCommandSource implements IRemoteCommandSource {
  constructor(options: IOptions) {
    // nothing here yet.
  }
}
