// app/api/index.js
import axios from "axios";
import * as SecureStore from "expo-secure-store";

const api = axios.create({
  baseURL: "http://10.0.2.2:5000",
  headers: { "Content-Type": "application/json" },
});

// 取得 token 工具
const getAuthHeader = async () => {
  const token = await SecureStore.getItemAsync("token");
  return { Authorization: `Bearer ${token}` };
};

// 登入
export const login = async (email, password) => {
  const res = await api.post("/auth/login", { email, password });
  return res.data;
};

// 註冊
export const signup = async (email, password) => {
  const res = await api.post("/auth/signup", { email, password });
  return res.data;
};

// 使用者資訊
export const fetchMe = async () => {
  const headers = await getAuthHeader();
  const res = await api.get("/auth/me", { headers });
  return res.data;
};

// 取出待複習單字
export const fetchWordsToReview = async (limit = 10) => {
  const headers = await getAuthHeader();
  const res = await api.get(`/pick_words?limit=${limit}`, { headers });
  return res.data;
};

// 新增單字（手動輸入）
export const addWord = async (word, level = "A1") => {
  const headers = await getAuthHeader();
  const res = await api.post("/words", { word, level }, { headers });
  return res.data;
};

// 點擊單字 → 新增並翻譯
export const createOrMarkWord = async (word) => {
  const headers = await getAuthHeader();
  const res = await api.post("/words", {
    word,
    level: "A1",
    markOnly: true  // 區分是標記用還是主動輸入
  }, { headers });
  return res.data;
};

// 回報複習品質（1~5）
export const sendReviewFeedback = async (wordId, quality) => {
  const headers = await getAuthHeader();
  const res = await api.post("/review/feedback", { wordId, quality }, { headers });
  return res.data;
};

// 建立文章
export const createArticle = async (lexileTarget, targetWords) => {
  const headers = await getAuthHeader();
  const res = await api.post("/articles", {
    lexileTarget,
    targetWords,
  }, { headers });
  return res.data;
};

// 取得所有文章
export const fetchArticles = async () => {
  const headers = await getAuthHeader();
  const res = await api.get("/articles", { headers });
  return res.data;
};

// 取得單篇文章
export const getArticle = async (articleId) => {
  const headers = await getAuthHeader();
  const res = await api.get(`/articles/${articleId}`, { headers });
  return res.data;
};

export async function fetchAllWords() {
  const res = await api.get('/words', { headers: await getAuthHeader() });
  return res.data;
}

export async function fetchImageForWord(word) {
  const res = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(word)}&format=json&no_redirect=1`);
  const data = await res.json();
  const imageUrl = data.Image || null;  // DuckDuckGo API
  return { imageUrl };
}
export const fetchQuizQuestions = async () => {
  const headers = await getAuthHeader();
  const res = await api.get("/words/quiz", { headers });
  return res.data;  
};