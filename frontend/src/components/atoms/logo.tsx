import { useRecoilValue } from "recoil";

import { settingsState } from "state/settings";

interface Props {
  width?: number;
  style?: React.CSSProperties;
}

export const Logo = ({ style }: Props) => {
  const { theme } = useRecoilValue(settingsState);

  return (
    <img
      src="https://myfirefly-ai.s3.amazonaws.com/logo/Vertical.png"
      alt="logo"
      style={style}
    />
  );
};
