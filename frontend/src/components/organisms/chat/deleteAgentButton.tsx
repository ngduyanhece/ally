import { useChatInteract } from "@chainlit/react-client";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import { IconButton, Tooltip } from "@mui/material";
export default function DeleteAgentButton() {
  const { deleteAgent } = useChatInteract();
  const handleClick = () => {
    deleteAgent();
  };
  return (
    <Tooltip title="Delete this agent">
      <span>
        <IconButton id="delete-agent-button" onClick={handleClick}>
          <DeleteForeverIcon />
        </IconButton>
      </span>
    </Tooltip>
  );
}
