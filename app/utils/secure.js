// app/utils/secure.js
import * as SecureStore from "expo-secure-store";

export const saveToken = (token) => SecureStore.setItemAsync("token", token);
export const getToken = () => SecureStore.getItemAsync("token");

export async function getAuthHeader() {
  const token = await getToken();
  return { Authorization: `Bearer ${token}` };
}
