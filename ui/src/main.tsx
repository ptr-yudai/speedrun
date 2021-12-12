import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import axios from "axios";
import { toast } from "react-toastify";

axios.defaults.withCredentials = true;
axios.interceptors.response.use((response) => {
  return response;
}, (error) => {
  try {
    toast.error(error.response.data.message);
  } catch {}
  return Promise.reject(error);
})

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)
