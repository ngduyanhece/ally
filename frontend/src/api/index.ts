import toast from "react-hot-toast";

import { ChainlitAPI, ClientError } from "@chainlit/react-client";

const devServer = "http://52.74.55.75:5050";
// const devServer = "http://0.0.0.0:5050";
// const url = import.meta.env.DEV ? devServer : window.origin;
const url = devServer;
const serverUrl = new URL(url);

const httpEndpoint = `${serverUrl.protocol}//${serverUrl.host}`;
export const wsEndpoint = httpEndpoint;

const on401 = () => {
  if (window.location.pathname !== "/login") {
    // The credentials aren't correct, remove the token and redirect to login
    window.location.href = "/login";
  }
};

const onError = (error: ClientError) => {
  toast.error(error.toString());
};

export const apiClient = new ChainlitAPI(httpEndpoint, on401, onError);
