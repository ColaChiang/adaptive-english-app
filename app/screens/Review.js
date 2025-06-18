// app/screens/Review.js
import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, StyleSheet, ActivityIndicator, Animated,
  TouchableOpacity, Alert, RefreshControl
} from 'react-native';
import { fetchWordsToReview, sendReviewFeedback } from '../api';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

export default function Review() {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedWord, setExpandedWord] = useState(null);

  const loadWords = async () => {
    try {
      const data = await fetchWordsToReview();
      setWords(data);
    } catch (err) {
      console.error('無法取得複習單字', err);
      Alert.alert('錯誤', '無法取得單字資料');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadWords();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadWords();
  };

  const getCardGradient = (easiness) => {
    if (easiness >= 2.5) return ['#0f2027', '#203a43', '#2c5364'];
    if (easiness >= 1.7) return ['#42275a', '#734b6d'];
    return ['#3a1c71', '#d76d77', '#ffaf7b'];
  };

  const handleFeedback = async (wordId, quality) => {
    try {
      await sendReviewFeedback(wordId, quality);
      setWords((prev) => prev.filter((w) => w.id !== wordId));
      if (expandedWord === wordId) setExpandedWord(null);
    } catch (err) {
      Alert.alert('錯誤', '無法送出回饋');
    }
  };

  const toggleExplanation = (wordId) => {
    setExpandedWord(expandedWord === wordId ? null : wordId);
  };

  const feedbackOptions = [
    { label: '不熟', value: 1 },
    { label: '一般', value: 3 },
    { label: '熟悉', value: 5 },
  ];

  const renderWordCard = ({ item, index }) => {
    const date = item.next_review
      ? new Date(item.next_review).toLocaleDateString()
      : '無資料';
    const isExpanded = expandedWord === item.id;

    return (
      <Animated.View style={styles.animated}>
        <LinearGradient
          colors={getCardGradient(item.easiness)}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.card}
        >
          <TouchableOpacity onPress={() => toggleExplanation(item.id)}>
            <Text style={styles.word}>{item.word || `單字${index}`}</Text>
            {isExpanded && (
              <Text style={styles.fullExplain}>{item.full ?? '無解釋'}</Text>
            )}
          </TouchableOpacity>

          {isExpanded && (
            <>
              <Text style={styles.info}>間隔天數：{item.interval ?? '?'}</Text>
              <Text style={styles.info}>
                熟悉度：{typeof item.easiness === 'number' ? item.easiness.toFixed(2) : '無'}
              </Text>
              <Text style={styles.info}>下次複習：{date}</Text>
            </>
          )}

          <View style={styles.feedbackRow}>
            {feedbackOptions.map((opt) => (
              <TouchableOpacity
                key={opt.value}
                style={styles.smallBtn}
                onPress={() => handleFeedback(item.id, opt.value)}
                activeOpacity={0.7}
              >

                <Text style={styles.smallText}>{opt.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </LinearGradient>
      </Animated.View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>單字記憶評估</Text>
      <Text style={styles.guide}>
        評分你對此單字的熟悉程度！(輕觸單字可展開解釋)
      </Text>
      
      <TouchableOpacity onPress={onRefresh} style={styles.reloadBtn}>
        <Ionicons name="refresh" size={22} color="#f1f5f9" />
        <Text style={styles.reloadText}>重新整理</Text>
      </TouchableOpacity>

      {loading ? (
        <ActivityIndicator size="large" color="#38bdf8" />
      ) : (
        <FlatList
          data={words}
          keyExtractor={(item, index) => item.word + index}
          renderItem={renderWordCard}
          ListEmptyComponent={
            <Text style={styles.empty}>沒有需要複習的單字</Text>
          }
          contentContainerStyle={{ paddingBottom: 20 }}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#1e293b',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#f1f5f9',
    textAlign: 'center',
    marginBottom: 4,
  },
  guide: {
    fontSize: 15,
    color: '#94a3b8',
    textAlign: 'center',
    marginBottom: 12,
  },
  reloadBtn: {
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  reloadText: {
    marginLeft: 6,
    color: '#f1f5f9',
    fontSize: 15,
  },
  card: {
    padding: 18,
    borderRadius: 18,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.4,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 8,
    elevation: 6,
  },
  word: {
    fontSize: 26,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 6,
  },
  fullExplain: {
    fontSize: 16,
    color: '#fde68a',
    marginBottom: 6,
  },
  info: {
    color: '#e0e7ff',
    fontSize: 15,
    marginTop: 2,
  },
  empty: {
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: 16,
    marginTop: 40,
  },
  feedbackRow: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    alignItems: 'center',
    marginTop: 14,
    paddingHorizontal: 12,
  },

  smallBtn: {
    backgroundColor: '#facc15',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 10,
    minWidth: 70,
    alignItems: 'center',
  },

  smallText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
  },
  animated: {
    transform: [{ scale: 1 }],
  },
});
