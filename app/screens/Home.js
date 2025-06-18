import { useState } from "react";
import {
  View,
  TextInput,
  Text,
  Alert,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { addWord } from "../api";

export default function Home({ route }) {
  const { username } = route.params;
  const [word, setWord] = useState("");
  const navigation = useNavigation();

  const onSubmit = async () => {
    try {
      const res = await addWord(word, "A1");
      Alert.alert("成功", res.message);
      setWord("");
    } catch (err) {
      console.log("錯誤：", err);
      Alert.alert("錯誤", err.response?.data?.error || "連線失敗");
    }
  };

  const PrimaryButton = ({ title, subtitle, onPress }) => (
    <TouchableOpacity onPress={onPress} style={styles.featureCard}>
      <Text style={styles.featureTitle}>{title}</Text>
      {subtitle && <Text style={styles.featureSubtitle}>{subtitle}</Text>}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.inner}>
      {/* <Text style={styles.greeting}>Hi, {username}</Text> */}
      <Text style={styles.greeting}>Hi, Ke-Le</Text>
      <Text style={styles.intro}>歡迎來到智慧英語學習系統👋</Text>

      <View style={styles.introBox}>
        <Text style={styles.introText}>
          這是一個整合「AI文章生成 + 記憶曲線 + 單字管理」的學習平台。
        </Text>
        <Text style={styles.introText}>
          你可以：
          {"\n"}• 建立個人字典{"\n"}• 自動生成包含指定單字的文章{"\n"}• 透過小測驗與回饋，強化記憶
        </Text>
      </View>

      <View style={styles.sectionBox}>
        <Text style={styles.sectionTitle}>有自己想要背的單字？快速加入</Text>
        <TextInput
          placeholder="例如：apple"
          value={word}
          onChangeText={setWord}
          style={styles.input}
          placeholderTextColor="#999"
        />
        <TouchableOpacity onPress={onSubmit} style={styles.addButton}>
          <Text style={styles.addButtonText}>加入字典</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>你的學習工具</Text>

      <PrimaryButton
        title="生成練習文章"
        subtitle="輸入目標難度與單字，AI 幫你生成文章"
        onPress={() => navigation.navigate("GenerateArticle")}
      />

      <PrimaryButton
        title="查看文章列表"
        subtitle="瀏覽你過去產生的所有文章"
        onPress={() => navigation.navigate("ArticleList")}
      />

      <PrimaryButton
        title="我的單字字典"
        subtitle="查看你學過的單字、翻譯與解釋"
        onPress={() => navigation.navigate("Dictionary")}
      />

      <PrimaryButton
        title="隨機單字測驗"
        subtitle="10 題克漏字題測驗，加強記憶"
        onPress={() => navigation.navigate("Quiz")}
      />
      
      <PrimaryButton
        title="單字記憶評估"
        subtitle="使用記憶曲線評估你是否記住了單字"
        onPress={() => navigation.navigate("Review")}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9fafb",
  },
  inner: {
    padding: 24,
  },
  greeting: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1e293b",
  },
  intro: {
    fontSize: 16,
    color: "#64748b",
    marginBottom: 12,
  },
  introBox: {
    backgroundColor: "#f1f5f9",
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  introText: {
    fontSize: 15,
    color: "#334155",
    marginBottom: 8,
    lineHeight: 22,
  },
  sectionBox: {
    backgroundColor: "#ffffff",
    padding: 20,
    borderRadius: 16,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#1e293b",
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#f8fafc",
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 10,
    fontSize: 16,
    marginBottom: 12,
    color: "#0f172a",
  },
  addButton: {
    backgroundColor: "#6366f1",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
  },
  addButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  featureCard: {
    backgroundColor: "#e0e7ff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#1e40af",
  },
  featureSubtitle: {
    fontSize: 14,
    color: "#475569",
    marginTop: 4,
  },
});
