import { useState } from "react";
import { View, TextInput, Button } from "react-native";
import { saveToken } from "../utils/secure";

export default function Login({ navigation }) {
  const [name, setName] = useState("");

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24 }}>
      <TextInput
        placeholder="Your name"
        value={name}
        onChangeText={setName}
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />
      <Button
        title="Enter"
        onPress={async () => {
          await saveToken("dummy");   // 先存假 token
          navigation.replace("Home", { username: name });
        }}
      />
    </View>
  );
}