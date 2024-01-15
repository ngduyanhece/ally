import { useChatInteract } from "@chainlit/react-client";
import ConstructionIcon from "@mui/icons-material/Construction";
import { IconButton, Tooltip } from "@mui/material";
export default function UpdateToolButton() {
  const { updateTool } = useChatInteract();
  const handleClick = () => {
    updateTool();
  };
  return (
    <Tooltip title="Update the latest available tools for agent">
      <span>
        <IconButton id="update-tool-button" onClick={handleClick}>
          <ConstructionIcon />
        </IconButton>
      </span>
    </Tooltip>
  );
}
