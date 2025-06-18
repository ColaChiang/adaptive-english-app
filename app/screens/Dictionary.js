// app/screens/Dictionary.js
import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, StyleSheet, ActivityIndicator, TouchableOpacity
} from 'react-native';
import { fetchAllWords } from '../api';

export default function Dictionary() {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    const loadWords = async () => {
      try {
        const res = await fetchAllWords();
        setWords(res.words || []);
      } catch (err) {
        console.error('無法取得單字', err);
      } finally {
        setLoading(false);
      }
    };
    loadWords();
  }, []);

  const toggleExpand = (wordId) => {
    setExpanded(expanded === wordId ? null : wordId);
  };

  const renderWord = ({ item }) => {
    const isExpanded = expanded === item.id;

    return (
      <TouchableOpacity onPress={() => toggleExpand(item.id)} style={styles.card}>
        <Text style={styles.word}>{item.id}</Text>
        {isExpanded && (
          <Text style={styles.meaning}>{item.full || '無解釋'}</Text>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>我的字典</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#3b82f6" />
      ) : (
        <FlatList
          data={words}
          keyExtractor={(item) => item.id}
          renderItem={renderWord}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8fafc',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#e2e8f0',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  word: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2563eb',
  },
  meaning: {
    fontSize: 15,
    color: '#1e293b',
    marginTop: 6,
  }
});
