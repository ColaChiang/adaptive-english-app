// App.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// 匯入頁面
import Login from './screens/Login';
import Home from './screens/Home';
import Review from './screens/Review';
import GenerateArticle from "./screens/GenerateArticle";
import ArticleList from "./screens/ArticleList";
import ArticleDetail from './screens/ArticleDetail';
import Dictionary from './screens/Dictionary';
import Quiz from './screens/Quiz';



const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen name="Login" component={Login} />
        <Stack.Screen name="Home" component={Home} />
        <Stack.Screen name="Review" component={Review} /> 
        <Stack.Screen name="GenerateArticle" component={GenerateArticle} options={{ title: "AI生成文章" }} />
        <Stack.Screen name="ArticleList" component={ArticleList} options={{ title: "我的文章列表" }} />
        <Stack.Screen name="ArticleDetail" component={ArticleDetail} options={{ title: "文章詳情" }} />
        <Stack.Screen name="Dictionary" component={Dictionary} options={{ title: "我的字典" }} />
        <Stack.Screen name="Quiz" component={Quiz} options={{ title: "隨機測驗" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
