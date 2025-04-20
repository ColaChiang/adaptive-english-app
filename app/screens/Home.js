import { useState } from "react";
import { View, TextInput, Button, Text, Alert } from "react-native";
import { api } from "../api";

export default function Home({ route }) {
  const { username } = route.params;
  const [word, setWord] = useState("");

  const addWord = async () => {
    try {
      const res = await api.post("/add_word", { word, level: "A1" });
      Alert.alert("成功", `${res.data.message}`);
      setWord("");
    } catch (err) {
      Alert.alert("錯誤", err.response?.data?.error || "連線失敗");
    }
  };

  return (
    <View style={{ flex: 1, padding: 24 }}>
      <Text style={{ fontSize: 18, marginBottom: 16 }}>
        Hi, {username}! 請輸入新單字
      </Text>
      <TextInput
        placeholder="e.g., apple"
        value={word}
        onChangeText={setWord}
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />
      <Button title="存到 Firestore" onPress={addWord} />
    </View>
  );
}