import App from './App.svelte'
import axios from "axios";
import { messages } from "./lib/stores";

axios.defaults.withCredentials = true;
axios.interceptors.response.use((response) => {
  return response;
}, (error) => {
  try {
    messages.push(error.response.data.message, "error");
  } catch {}
  return Promise.reject(error);
})

const app = new App({
  target: document.getElementById('app')
})

export default app
