import { IFileResponse, useChatInteract } from "@chainlit/react-client";
import { Attachments } from "@chainlit/react-components";
import CheckIcon from "@mui/icons-material/Check";
import { Box, IconButton, Stack } from "@mui/material";
import { useCallback, useMemo } from "react";
import toast from "react-hot-toast";
import { useRecoilState, useSetRecoilState } from "recoil";
import { memoryAttachmentsState } from "state/agentMemory";
import { v4 as uuidv4 } from "uuid";
import MemoryInput from "./memoryInput";

const UpdateMemory = () => {
  const { updateMemory } = useChatInteract();
  const setMemoryAttachments = useSetRecoilState(memoryAttachmentsState);
  const [memoryFileElements, setMemoryFileElements] = useRecoilState(
    memoryAttachmentsState
  );
  const fileSpec = useMemo(() => ({ max_size_mb: 1000 }), []);

  const disabled = memoryFileElements.length > 0 ? true : false;

  const onFileUpload = useCallback((payloads: IFileResponse[]) => {
    const fileElements = payloads.map((file) => ({
      id: uuidv4(),
      type: "file" as const,
      display: "inline" as const,
      name: file.name,
      mime: file.type,
      content: file.content,
    }));
    setMemoryAttachments((prev) => prev.concat(fileElements));
    console.log("fileElements", fileElements);
  }, []);

  const onFileUploadError = useCallback(
    () => (error: string) => toast.error(error),
    []
  );
  const submit = useCallback(() => {
    updateMemory(memoryFileElements);
    setMemoryAttachments([]);
  }, [memoryFileElements, updateMemory, setMemoryAttachments]);
  return (
    <Stack
      sx={{
        // backgroundColor: "background.paper",
        borderRadius: 1,
        // border: (theme) => `1px solid ${theme.palette.divider}`,
        boxShadow: "box-shadow: 0px 2px 4px 0px #0000000D",
        textarea: {
          height: "34px",
          maxHeight: "30vh",
          overflowY: "auto !important",
          resize: "none",
          paddingBottom: "0.75rem",
          paddingTop: "0.75rem",
          color: "text.primary",
          lineHeight: "24px",
        },
      }}
    >
      {memoryFileElements.length > 0 ? (
        <Box
          sx={{
            mt: 2,
            mx: 2,
            padding: "2px",
          }}
        >
          <Attachments
            fileElements={memoryFileElements}
            setFileElements={setMemoryFileElements}
          />
          <IconButton color="inherit" onClick={() => submit()}>
            <CheckIcon />
          </IconButton>
        </Box>
      ) : null}
      <MemoryInput
        disabled={disabled}
        fileSpec={fileSpec}
        onFileUploadError={onFileUploadError}
        onFileUpload={onFileUpload}
      />
    </Stack>
  );
};
export default UpdateMemory;
