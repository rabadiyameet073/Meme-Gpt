import React, { useState, useRef, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, SafeAreaView,
  ScrollView,
} from "react-native";
import { Image } from "expo-image";
import { router } from "expo-router";
import { api, MemeResult } from "../../lib/api";
import { useMemeActions } from "../../hooks/useMemeActions";

const FORMATS = [
  { label: "All", value: "any" },
  { label: "GIF", value: "gif" },
  { label: "Image", value: "image" },
  { label: "Video", value: "video" },
];

const SUGGESTIONS = [
  "when monday hits", "code works first try", "friday feeling",
  "boss vs employee", "me procrastinating", "when budget cuts",
  "meeting that couldve been email", "waiting for deploy",
];

function SuggestionChips({ onPress }: { onPress: (s: string) => void }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipsScroll}>
      {SUGGESTIONS.map((s) => (
        <TouchableOpacity key={s} style={styles.chip} onPress={() => onPress(s)}>
          <Text style={styles.chipText}>{s}</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

function MemeCard({ item, onAction }: { item: MemeResult; onAction: (msg: string) => void }) {
  const { shareMeme, saveToCameraRoll } = useMemeActions();
  const imageUrl = item.gif_url || item.image_url || item.thumb_url || "";

  const handleOpenDetail = () => {
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
    <View style={styles.card}>
      <TouchableOpacity activeOpacity={0.85} onPress={handleOpenDetail}>
        <Image
          source={{ uri: imageUrl }}
          style={styles.cardImage}
          contentFit="cover"
          transition={300}
        />
      </TouchableOpacity>
      <View style={styles.cardFooter}>
        <TouchableOpacity style={{ flex: 1 }} onPress={handleOpenDetail}>
          <Text style={styles.cardName} numberOfLines={2}>{item.name}</Text>
        </TouchableOpacity>
        <View style={styles.cardActions}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => shareMeme({ url: imageUrl, title: item.name }).then(() => onAction("Shared!"))}
          >
            <Text style={styles.actionIcon}>↗</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => saveToCameraRoll(imageUrl).then((ok) => onAction(ok ? "Saved!" : "Permission required"))}
          >
            <Text style={styles.actionIcon}>⬇</Text>
          </TouchableOpacity>
        </View>
      </View>
      {item.confidence != null && (
        <View style={styles.confidenceBadge}>
          <Text style={styles.confidenceText}>{Math.round(item.confidence * 100)}% match</Text>
        </View>
      )}
    </View>
  );
}

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const [format, setFormat] = useState("gif");
  const [results, setResults] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const inputRef = useRef<TextInput>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2500);
  }, []);

  const handleSearch = useCallback(async (q?: string) => {
    const searchQuery = q ?? query;
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError("");
    try {
      const data = await api.search(searchQuery, format, 10);
      setResults(data.matches || []);
      if ((data.matches || []).length === 0) {
        setError("No memes found. Try a different query!");
      }
    } catch (err) {
      setError("Search failed. Check your connection.");
    } finally {
      setLoading(false);
    }
  }, [query, format]);

  const handleSuggestion = useCallback((s: string) => {
    setQuery(s);
    handleSearch(s);
  }, [handleSearch]);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🎭 MemeGPT</Text>
          <Text style={styles.headerSub}>Say anything. Get the perfect meme.</Text>
        </View>

        {/* Search Bar */}
        <View style={styles.searchBar}>
          <TextInput
            ref={inputRef}
            style={styles.searchInput}
            placeholder="Describe your situation..."
            placeholderTextColor="#71717a"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={() => handleSearch()}
            returnKeyType="search"
            multiline={false}
          />
          <TouchableOpacity
            style={[styles.searchBtn, loading && styles.searchBtnDisabled]}
            onPress={() => handleSearch()}
            disabled={loading}
          >
            <Text style={styles.searchBtnText}>{loading ? "..." : "🔍"}</Text>
          </TouchableOpacity>
        </View>

        {/* Format Filter */}
        <View style={styles.formatRow}>
          {FORMATS.map((f) => (
            <TouchableOpacity
              key={f.value}
              style={[styles.formatChip, format === f.value && styles.formatChipActive]}
              onPress={() => setFormat(f.value)}
            >
              <Text style={[styles.formatText, format === f.value && styles.formatTextActive]}>
                {f.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Suggestions (when no results) */}
        {results.length === 0 && !loading && (
          <SuggestionChips onPress={handleSuggestion} />
        )}

        {/* Results */}
        {loading ? (
          <View style={styles.loadingView}>
            <ActivityIndicator size="large" color="#7C3AED" />
            <Text style={styles.loadingText}>Finding the perfect meme...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorView}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : (
          <FlatList
            data={results}
            keyExtractor={(item) => String(item.id)}
            numColumns={2}
            columnWrapperStyle={styles.columnWrapper}
            renderItem={({ item }) => (
              <MemeCard item={item} onAction={showToast} />
            )}
            contentContainerStyle={styles.list}
            showsVerticalScrollIndicator={false}
          />
        )}

        {/* Toast */}
        {toast ? (
          <View style={styles.toast}>
            <Text style={styles.toastText}>{toast}</Text>
          </View>
        ) : null}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  header: { padding: 20, paddingBottom: 12 },
  headerTitle: { color: "#fff", fontSize: 26, fontWeight: "800" },
  headerSub: { color: "#71717a", fontSize: 13, marginTop: 2 },
  searchBar: { flexDirection: "row", marginHorizontal: 16, marginBottom: 10, gap: 8 },
  searchInput: {
    flex: 1, backgroundColor: "#18181B", color: "#fff", borderRadius: 12,
    paddingHorizontal: 16, paddingVertical: 12, fontSize: 15,
    borderWidth: 1, borderColor: "#3F3F46",
  },
  searchBtn: {
    backgroundColor: "#7C3AED", borderRadius: 12, paddingHorizontal: 16,
    justifyContent: "center", alignItems: "center",
  },
  searchBtnDisabled: { backgroundColor: "#4C1D95" },
  searchBtnText: { fontSize: 20 },
  formatRow: { flexDirection: "row", paddingHorizontal: 16, gap: 8, marginBottom: 12 },
  formatChip: {
    paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20,
    backgroundColor: "#18181B", borderWidth: 1, borderColor: "#3F3F46",
  },
  formatChipActive: { backgroundColor: "#7C3AED", borderColor: "#7C3AED" },
  formatText: { color: "#71717a", fontSize: 13, fontWeight: "600" },
  formatTextActive: { color: "#fff" },
  chipsScroll: { paddingHorizontal: 16, marginBottom: 12 },
  chip: {
    backgroundColor: "#18181B", borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6,
    marginRight: 8, borderWidth: 1, borderColor: "#3F3F46",
  },
  chipText: { color: "#a1a1aa", fontSize: 12 },
  loadingView: { flex: 1, justifyContent: "center", alignItems: "center", gap: 16 },
  loadingText: { color: "#71717a", fontSize: 15 },
  errorView: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24 },
  errorText: { color: "#ef4444", textAlign: "center", fontSize: 15 },
  list: { paddingHorizontal: 12, paddingBottom: 24 },
  columnWrapper: { gap: 8, marginBottom: 8 },
  card: {
    flex: 1, backgroundColor: "#18181B", borderRadius: 16,
    overflow: "hidden", borderWidth: 1, borderColor: "#27272A",
  },
  cardImage: { width: "100%", aspectRatio: 1 },
  cardFooter: { padding: 8, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" },
  cardName: { flex: 1, color: "#e4e4e7", fontSize: 11, fontWeight: "600", marginRight: 4 },
  cardActions: { flexDirection: "row", gap: 4 },
  actionBtn: { width: 28, height: 28, borderRadius: 8, backgroundColor: "#27272A", justifyContent: "center", alignItems: "center" },
  actionIcon: { fontSize: 12, color: "#a1a1aa" },
  confidenceBadge: {
    position: "absolute", top: 8, right: 8,
    backgroundColor: "rgba(124,58,237,0.85)", borderRadius: 6, paddingHorizontal: 6, paddingVertical: 2,
  },
  confidenceText: { color: "#fff", fontSize: 10, fontWeight: "700" },
  toast: {
    position: "absolute", bottom: 20, left: 32, right: 32,
    backgroundColor: "#7C3AED", borderRadius: 12, padding: 14, alignItems: "center",
  },
  toastText: { color: "#fff", fontWeight: "600", fontSize: 14 },
});
