import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ActivityIndicator, ScrollView,
  Modal, TouchableOpacity
} from 'react-native';
import { getArticle, createOrMarkWord } from '../api';
import { useRoute } from '@react-navigation/native';

export default function ArticleDetail() {
  const route = useRoute();
  const { articleId } = route.params;
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [markedWords, setMarkedWords] = useState({});
  const [selectedWord, setSelectedWord] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getArticle(articleId);
        setArticle(res);
      } catch (err) {
        console.error("❌ 無法載入文章", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleWordPress = async (rawWord) => {
    const word = rawWord.toLowerCase().replace(/[^a-zA-Z']/g, '');
    if (!word) return;

    if (markedWords[word]) {
      setSelectedWord(word);
      return;
    }

    setMarkedWords((prev) => ({
      ...prev,
      [word]: { short: "查詢中...", full: "" }
    }));
    setSelectedWord(word);

    try {
      const res = await createOrMarkWord(word);
      setMarkedWords((prev) => ({
        ...prev,
        [word]: { short: res.short, full: res.full },
      }));
    } catch (err) {
      console.error("儲存或翻譯失敗", err);
      setMarkedWords((prev) => ({
        ...prev,
        [word]: { short: "翻譯失敗", full: "無法取得解釋。" }
      }));
    }
  };

  const closeModal = () => {
    setSelectedWord(null);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#60a5fa" />
      </View>
    );
  }

  if (!article) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>文章載入失敗</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>     
    <Text style={styles.tip}>
        💡遇到不會的單字？{'\n'}可直接點擊該單字進行翻譯與加入字典。
      </Text>
      <Text style={styles.title}>文章內容</Text>

 

      <Text style={styles.articleText}>
        {article.article.split(' ').map((word, idx) => {
          const cleanWord = word.toLowerCase().replace(/[^a-zA-Z']/g, '');
          const mark = markedWords[cleanWord];

          return (
            <Text
              key={idx}
              style={[styles.wordInline, mark && styles.marked]}
              onPress={() => handleWordPress(word)}
            >
              {word + ' '}
              {mark && selectedWord !== cleanWord && (
                <Text style={styles.meaning}>
                  ({mark.short === "查詢中..." ? "..." : mark.short}){" "}
                </Text>
              )}
            </Text>
          );
        })}
      </Text>

      <View style={styles.divider} />

      <View style={styles.footer}>
        <Text style={styles.section}>本文資訊</Text>
        <Text style={styles.score}>實際Lexile：{article.lexileActual}</Text>
        <Text style={styles.section}>關鍵單字：</Text>

          {Object.keys(article.wordCounts).map((word) => (
            <Text key={word} style={styles.word}>• {word}</Text>
        ))}
      </View>

      {/* 解釋彈窗 */}
      <Modal visible={!!selectedWord} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>{selectedWord}</Text>
            <Text style={styles.modalExplain}>{markedWords[selectedWord]?.full}</Text>
            <TouchableOpacity onPress={closeModal} style={styles.closeBtn}>
              <Text style={styles.closeText}>關閉</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#f9fafb' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 12 },
  section: { fontSize: 18, fontWeight: '600', marginTop: 16 },
  score: { fontSize: 16, marginTop: 6 },
  tip: {
    color: '#64748b',
    fontSize: 14,
    marginBottom: 12,
    lineHeight: 20
  },
  divider: {
    height: 1,
    backgroundColor: "#e2e8f0",
    marginVertical: 20,
  },
  footer: {
    marginBottom: 40,
  },
  word: { fontSize: 16, marginLeft: 8, marginTop: 4 },
  wordInline: { fontSize: 16, lineHeight: 26, color: '#1f2937' },
  marked: { backgroundColor: '#e0f2fe', borderRadius: 4, paddingHorizontal: 2 },
  meaning: { color: '#0284c7', fontSize: 14 },
  articleText: { marginTop: 8, flexWrap: 'wrap' },
  error: { fontSize: 18, color: 'red' },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalBox: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    width: '80%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  modalTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 12 },
  modalExplain: { fontSize: 16, marginBottom: 20 },
  closeBtn: {
    backgroundColor: '#3b82f6',
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center'
  },
  closeText: { color: 'white', fontWeight: '600' }
});
