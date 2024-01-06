import { FileSpec, IFileResponse } from "@chainlit/react-client";
import { useUpload } from "@chainlit/react-components";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { IconButton, Tooltip } from "@mui/material";

type Props = {
  disabled?: boolean;
  fileSpec: FileSpec;
  onFileUpload: (files: IFileResponse[]) => void;
  onFileUploadError: (error: string) => void;
};

const MemoryInput = ({
  disabled,
  fileSpec,
  onFileUpload,
  onFileUploadError,
}: Props) => {
  const upload = useUpload({
    spec: fileSpec,
    onResolved: (payloads: IFileResponse[]) => onFileUpload(payloads),
    onError: onFileUploadError,
    options: { noDrag: false },
  });
  if (!upload) return null;
  const { getRootProps, getInputProps, uploading } = upload;
  return (
    <Tooltip title="Upload to agent's memory">
      <span>
        <input id="memory-input" {...getInputProps()} />
        <IconButton
          id={uploading ? "memory-input-button-loading" : "memory-input-button"}
          disabled={uploading || disabled}
          {...getRootProps({ className: "dropzone" })}
        >
          <CloudUploadIcon />
        </IconButton>
      </span>
    </Tooltip>
  );
};
export default MemoryInput;
