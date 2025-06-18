import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator
} from 'react-native';
import { fetchArticles } from '../api';
import { useNavigation } from '@react-navigation/native';

export default function ArticleList() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigation = useNavigation();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetchArticles();
        setArticles(res.articles || []);
      } catch (e) {
        console.error("取得文章失敗", e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // 抓包含 targetWords 的第一句，或 fallback
  const getSmartPreview = (article, targetWords) => {
    if (!article) return "(無內文)";
    const sentences = article.split(/(?<=[.?!])\s+/);
    const matched = sentences.find((s) =>
      targetWords?.some((word) => s.toLowerCase().includes(word.toLowerCase()))
    );
    return (matched || sentences[0] || "").slice(0, 80);
  };

  // 時間格式處理
  const formatDateTime = (createdAt) => {
    if (!createdAt) return "(未知時間)";
    let dateObj = null;

    if (typeof createdAt === 'object' && '_seconds' in createdAt) {
      dateObj = new Date(createdAt._seconds * 1000);
    } else {
      dateObj = new Date(createdAt);
    }

    return dateObj.toLocaleString('zh-TW', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderItem = ({ item }) => {
    const preview = getSmartPreview(item.article, item.targetWords);
    const dateStr = formatDateTime(item.createdAt);
    const targetWordsStr = item.targetWords?.join(", ") || "（無單字）";

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate("ArticleDetail", { articleId: item.id })}
      >
        <Text style={styles.title}>{preview}...</Text>
        <Text style={styles.info}>📚 單字：{targetWordsStr}</Text>
        <Text style={styles.date}>🕒 {dateStr}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>我的文章</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#60a5fa" />
      ) : (
        <FlatList
          data={articles}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          ListEmptyComponent={<Text style={styles.empty}>尚未建立任何文章</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#0f172a" },
  header: { fontSize: 22, fontWeight: "bold", color: "white", marginBottom: 12 },
  card: {
    backgroundColor: "#1e293b",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  title: { color: "#f8fafc", fontSize: 16, marginBottom: 4 },
  info: { color: "#cbd5e1", fontSize: 14 },
  date: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 40, color: "#64748b" },
});
