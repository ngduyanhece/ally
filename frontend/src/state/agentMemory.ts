import { atom } from "recoil";

import { IFileElement } from "@chainlit/react-client";

export const memoryAttachmentsState = atom<IFileElement[]>({
  key: "MemoryAttachments",
  default: [],
});
