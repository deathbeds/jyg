import { LabIcon } from '@jupyterlab/ui-components';

import JYG from '../style/img/logo.svg';

export const logo = new LabIcon({ name: 'jyg:logo', svgstr: JYG });
export const danger = new LabIcon({
  name: 'jyg:danger',
  svgstr: JYG.replace('jp-icon3', 'jp-error-color1'),
});
