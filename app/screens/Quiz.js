// app/screens/Quiz.js
import React, { useEffect, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, ScrollView, Alert
} from 'react-native';
import { fetchQuizQuestions } from '../api';

export default function Quiz() {
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchQuizQuestions();
        setQuestions(data.questions);
      } catch (err) {
        Alert.alert('錯誤', '無法載入題目');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSelect = (option) => {
    setSelected(option);
    if (option === questions[current].answer) {
      setScore(score + 1);
    }
    setTimeout(() => {
      if (current + 1 === questions.length) {
        setFinished(true);
      } else {
        setCurrent(current + 1);
        setSelected(null);
      }
    }, 800);
  };

  if (loading) {
    return (
      <View style={styles.center}><ActivityIndicator size="large" color="#3b82f6" /></View>
    );
  }

  if (finished) {
    return (
      <View style={styles.center}>
        <Text style={styles.title}>🎉 測驗完成</Text>
        <Text style={styles.score}>得分：{score} / {questions.length}</Text>
      </View>
    );
  }

  const q = questions[current];

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>第 {current + 1} 題</Text>
      <Text style={styles.question}>{q.question}</Text>
      {q.options.map((opt, idx) => (
        <TouchableOpacity
          key={idx}
          style={[styles.option, selected === opt && (opt === q.answer ? styles.correct : styles.wrong)]}
          onPress={() => handleSelect(opt)}
          disabled={selected !== null}
        >
          <Text style={styles.optionText}>{opt}</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 16 },
  question: { fontSize: 18, marginBottom: 20 },
  option: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#e2e8f0',
    marginBottom: 12,
  },
  optionText: { fontSize: 16 },
  correct: { backgroundColor: '#4ade80' },
  wrong: { backgroundColor: '#f87171' },
  score: { fontSize: 20, fontWeight: '600', marginTop: 10 }
});
