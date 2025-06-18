import React, { useState } from "react";
import {
  View,
  TextInput,
  Text,
  Alert,
  StyleSheet,
  ScrollView,
  Button,
  TouchableOpacity
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import { createArticle } from "../api";

export default function GenerateArticle() {
  const [lexileTarget, setLexileTarget] = useState("800");
  const [targetWords, setTargetWords] = useState("");
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [usedWords, setUsedWords] = useState([]);

  const onGenerate = async () => {
    const words = targetWords
      .split(",")
      .map(w => w.trim())
      .filter(w => w.length > 0);

    if (!lexileTarget) {
      Alert.alert("錯誤", "請選擇難度");
      return;
    }

    setLoading(true);
    try {
      const data = await createArticle(parseInt(lexileTarget), words.length > 0 ? words : undefined);
      setArticle(data);
      setUsedWords(data.targetWords || []);
    } catch (err) {
      Alert.alert("產生失敗", err.response?.data?.error || "連線錯誤");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>智慧文章生成器</Text>
      <View style={styles.introBox}>
        <Text style={styles.introText}>
          歡迎使用智慧文章產生器！
          系統將根據你指定的閱讀難度與單字自動產生短篇文章。
          即使你不輸入任何單字，也會根據你的學習進度自動挑選。
        </Text>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.label}>選擇文章難度：</Text>
        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={lexileTarget}
            onValueChange={(value) => setLexileTarget(value)}
            style={styles.picker}
          >
            <Picker.Item label="非常簡單（約 300L）" value="300" />
            <Picker.Item label="簡單（約 500L）" value="500" />
            <Picker.Item label="中等（約 800L）" value="800" />
            <Picker.Item label="有挑戰（約 1000L）" value="1000" />
            <Picker.Item label="困難（約 1200L）" value="1200" />
          </Picker>
        </View>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.label}>想包含的單字（可留空）：</Text>
        <TextInput
          value={targetWords}
          onChangeText={setTargetWords}
          placeholder="例如：apple, happy, run"
          style={styles.input}
        />
        <Text style={styles.hint}>💡留空則會自動挑選你較陌生的單字。</Text>
      </View>

      <TouchableOpacity
        onPress={onGenerate}
        style={[styles.button, loading && { opacity: 0.6 }]}
        disabled={loading}
      >
        <Text style={styles.buttonText}>{loading ? "產生中..." : "產生文章"}</Text>
      </TouchableOpacity>

      {article && (
        <View style={styles.result}>
            <Text style={{color: "#64748b" }}>
              💡遇到不會的單字？{"\n"}可以直接點擊該單字，會自動翻譯並加入字典喔！{"\n\n"}
            </Text>
          
          <Text style={styles.label}>生成文章：</Text>
          <Text style={styles.article}>{article.article}</Text>
          {usedWords.length > 0 && (
            <Text style={styles.wordsUsed}>
              本次使用單字：{usedWords.join(", ")}
            </Text>
          )}
          <Text style={styles.meta}>
            實際 Lexile: {article.lexileActual}
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: "#f9fafb" },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 10 },
  introBox: {
    backgroundColor: '#eef2ff',
    padding: 14,
    borderRadius: 10,
    marginBottom: 20,
  },
  introText: {
    fontSize: 15,
    color: '#334155',
    lineHeight: 22,
  },
  sectionBox: {
    backgroundColor: "#ffffff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 6,
  },
  label: { fontSize: 16, fontWeight: "bold", marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: "#cbd5e1",
    padding: 10,
    borderRadius: 8,
    backgroundColor: "#f8fafc",
  },
  hint: {
    fontSize: 13,
    color: "#64748b",
    marginTop: 4,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    overflow: "hidden",
  },
  picker: {
  height: 56,
  width: '100%',
  justifyContent: 'center',
},
  button: {
    backgroundColor: "#6366f1",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  result: { marginTop: 32 },
  article: { marginTop: 8, fontSize: 16, lineHeight: 24 },
  wordsUsed: { marginTop: 12, fontSize: 15, color: "#334155", fontStyle: "italic" },
  meta: { marginTop: 12, color: "#888" },
});
