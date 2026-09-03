import React, { useState, useCallback } from "react";
import {
  View, Text, FlatList, StyleSheet, SafeAreaView, TouchableOpacity,
} from "react-native";
import { Image } from "expo-image";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect, router } from "expo-router";
import { MemeResult } from "../../lib/api";

const FAV_KEY = "memegpt_favorites_v1";

export default function LibraryScreen() {
  const [favorites, setFavorites] = useState<MemeResult[]>([]);

  const loadFavorites = useCallback(async () => {
    const raw = await AsyncStorage.getItem(FAV_KEY);
    if (raw) {
      try {
        setFavorites(JSON.parse(raw));
      } catch {
        setFavorites([]);
      }
    }
  }, []);

  useFocusEffect(() => {
    loadFavorites();
  });

  const removeFavorite = async (id: number) => {
    const updated = favorites.filter((f) => f.id !== id);
    setFavorites(updated);
    await AsyncStorage.setItem(FAV_KEY, JSON.stringify(updated));
  };

  if (favorites.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>❤️ Saved Memes</Text>
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>📂</Text>
          <Text style={styles.emptyText}>No saved memes yet!</Text>
          <Text style={styles.emptySubtext}>Search and save memes to see them here</Text>
        </View>
      </SafeAreaView>
    );
  }

  const handleOpenDetail = (item: MemeResult) => {
    router.push({
      pathname: "/meme/[id]",
      params: {
        id: item.slug || String(item.id),
        name: item.name,
        imageUrl: item.image_url,
        gifUrl: item.gif_url,
        explanation: item.explanation || "",
      },
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>❤️ Saved Memes ({favorites.length})</Text>
      <FlatList
        data={favorites}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        columnWrapperStyle={{ gap: 8, marginBottom: 8 }}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <TouchableOpacity activeOpacity={0.85} onPress={() => handleOpenDetail(item)}>
              <Image
                source={{ uri: item.thumb_url || item.image_url }}
                style={styles.image}
                contentFit="cover"
                transition={200}
              />
            </TouchableOpacity>
            <View style={styles.cardBottom}>
              <TouchableOpacity style={{ flex: 1 }} onPress={() => handleOpenDetail(item)}>
                <Text style={styles.name} numberOfLines={1}>{item.name}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => removeFavorite(item.id)}>
                <Text style={styles.remove}>✕</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  title: { color: "#fff", fontSize: 22, fontWeight: "800", padding: 20, paddingBottom: 12 },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", gap: 12 },
  emptyIcon: { fontSize: 64 },
  emptyText: { color: "#fff", fontSize: 18, fontWeight: "700" },
  emptySubtext: { color: "#71717a", fontSize: 14, textAlign: "center" },
  card: { flex: 1, backgroundColor: "#18181B", borderRadius: 12, overflow: "hidden" },
  image: { width: "100%", aspectRatio: 1 },
  cardBottom: { flexDirection: "row", justifyContent: "space-between", padding: 8, alignItems: "center" },
  name: { flex: 1, color: "#e4e4e7", fontSize: 11, fontWeight: "600" },
  remove: { color: "#71717a", fontSize: 16, paddingLeft: 4 },
});
