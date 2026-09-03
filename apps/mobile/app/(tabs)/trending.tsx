import React, { useEffect, useState } from "react";
import {
  View, Text, FlatList, StyleSheet, ActivityIndicator, SafeAreaView, RefreshControl,
} from "react-native";
import { Image } from "expo-image";
import { router } from "expo-router";
import { api, MemeResult } from "../../lib/api";

export default function TrendingScreen() {
  const [memes, setMemes] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const data = await api.getTrending(20);
      setMemes(data);
    } catch {
      /* silently fail */
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#7C3AED" />
      </View>
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
      <Text style={styles.title}>🔥 Trending Memes</Text>
      <FlatList
        data={memes}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        columnWrapperStyle={{ gap: 8, marginBottom: 8 }}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            activeOpacity={0.85}
            onPress={() => handleOpenDetail(item)}
          >
            <Image
              source={{ uri: item.thumb_url || item.image_url }}
              style={styles.image}
              contentFit="cover"
              transition={200}
            />
            <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
          </TouchableOpacity>
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  loading: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#09090B" },
  title: { color: "#fff", fontSize: 22, fontWeight: "800", padding: 20, paddingBottom: 12 },
  card: { flex: 1, backgroundColor: "#18181B", borderRadius: 12, overflow: "hidden" },
  image: { width: "100%", aspectRatio: 1 },
  name: { color: "#e4e4e7", fontSize: 11, padding: 8, fontWeight: "600" },
});
