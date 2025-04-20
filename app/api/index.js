import axios from "axios";

export const api = axios.create({
  baseURL: "http://10.0.2.2:5000",   // Android 模擬器用 10.0.2.2 映射 localhost
  headers: { "Content-Type": "application/json" },
});