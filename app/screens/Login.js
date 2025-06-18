import { useState } from "react";
import { Image } from "react-native";

import {
  View,
  TextInput,
  Text,
  Alert,
  Keyboard,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { saveToken } from "../utils/secure";
import { login } from "../api";

export default function Login({ navigation }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onLogin = async () => {
    if (!email || !password) {
      return Alert.alert("請輸入 Email 和密碼");
    }

    setLoading(true);
    Keyboard.dismiss();

    try {
      const res = await login(email, password);
      const token = res?.token;

      if (!token) throw new Error("未收到 token");

      await saveToken(token);
      Alert.alert("登入成功");
      setEmail("");
      setPassword("");
      navigation.replace("Home", { username: email });
    } catch (err) {
      console.log("登入失敗：", err);
      Alert.alert("登入失敗", err.response?.data?.error || err.message || "未知錯誤");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header / Logo / Title */}
        <View style={styles.header}>
          <Image
            source={require("../assets/logo.png")}
            style={styles.logo}
          />

          <Text style={styles.title}>Adaptive English System</Text>
          <Text style={styles.subtitle}>
            AI × 記憶曲線 × 單字管理的智慧學習平台
          </Text>
        </View>

        {/* Login Form */}
        <View style={styles.card}>
          <TextInput
            placeholder="Email"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            placeholderTextColor="#64748b"
            style={styles.input}
          />
          <TextInput
            placeholder="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholderTextColor="#64748b"
            style={styles.input}
          />

          {loading ? (
            <ActivityIndicator size="large" color="#2563eb" style={{ marginTop: 16 }} />
          ) : (
            <TouchableOpacity onPress={onLogin} style={styles.loginBtn}>
              <Text style={styles.loginText}>登入</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Motivational Quote */}
        <Text style={styles.quote}>
          讓每一次複習都恰到好處，讓學習不再靠毅力，而是靠科學
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1e293b",
  },
  scrollContent: {
    padding: 24,
    justifyContent: "center",
    flexGrow: 1,
  },
  header: {
    alignItems: "center",
    marginBottom: 24,
  },
  logo: {
    width: 128,
    height: 128,
    marginBottom: 12,
    resizeMode: "contain",
  },

  title: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#f8fafc",
    textAlign: "center",
  },
  subtitle: {
    fontSize: 14,
    color: "#cbd5e1",
    textAlign: "center",
    marginTop: 4,
  },
  card: {
    backgroundColor: "#ffffff",
    padding: 24,
    borderRadius: 16,
    shadowColor: "#000",
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 12,
    elevation: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#f1f5f9",
    color: "#0f172a",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 14,
  },
  loginBtn: {
    backgroundColor: "#2563eb",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 4,
  },
  loginText: {
    fontSize: 16,
    color: "#ffffff",
    fontWeight: "bold",
  },
  quote: {
    marginTop: 24,
    textAlign: "center",
    color: "#94a3b8",
    fontSize: 13,
    fontStyle: "italic",
  },
});
