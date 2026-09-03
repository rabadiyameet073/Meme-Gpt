/**
 * MemeGPT Mobile — Meme Detail Screen /meme/[id]
 * Shows full meme with all formats, high-res preview, and actions.
 * Specification: 05_Mobile_App_Completion.md
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, router } from "expo-router";
import { Image } from "expo-image";
import { api } from "../../lib/api";
import { useMemeActions } from "../../hooks/useMemeActions";

export default function MemeDetailScreen() {
  const params = useLocalSearchParams<{
    id: string;
    name?: string;
    imageUrl?: string;
    gifUrl?: string;
    explanation?: string;
  }>();

  const { shareMeme, saveToCameraRoll, copyMemeLink } = useMemeActions();
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);

  const slug = typeof params.id === "string" ? params.id : "";
  const name = params.name || slug.replace(/-/g, " ");
  const imageUrl = params.gifUrl || params.imageUrl || `https://cdn.memegpt.com/images/${slug}.jpg`;
  const explanation = params.explanation || "";

  const handleVote = async (voteVal: 1 | -1) => {
    try {
      const memeId = parseInt(slug, 10) || Math.abs(hashString(slug));
      await api.vote(memeId, voteVal, "mobile_session");
      setFeedbackSent(voteVal === 1 ? "up" : "down");
      Alert.alert("Feedback recorded", voteVal === 1 ? "Glad you liked it! 👍" : "We'll improve recommendations! 👎");
    } catch {
      Alert.alert("Feedback", "Thank you for your rating!");
    }
  };

  const handleFeedback = async (type: string) => {
    try {
      const memeId = parseInt(slug, 10) || Math.abs(hashString(slug));
      await api.sendFeedback(memeId, type);
      Alert.alert("Feedback Sent", "Thanks for helping MemeGPT improve!");
    } catch {
      Alert.alert("Feedback", "Thanks for your feedback!");
    }
  };

  return (
    <SafeAreaView style={styles.safe} edges={["top", "bottom"]}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Back button */}
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>

        <Text style={styles.title}>{name}</Text>

        {/* High-res Image Preview */}
        <View style={styles.imageWrap}>
          <Image
            source={{ uri: imageUrl }}
            style={styles.image}
            contentFit="contain"
            transition={300}
          />
        </View>

        {explanation ? (
          <View style={styles.explanationBox}>
            <Text style={styles.explanationText}>{explanation}</Text>
          </View>
        ) : null}

        {/* Action buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.btn, styles.btnPurple]}
            onPress={() => saveToCameraRoll(imageUrl).then((ok) => Alert.alert(ok ? "Saved!" : "Could not save"))}
            accessibilityRole="button"
            accessibilityLabel="Save to Photos"
          >
            <Text style={styles.btnText}>⬇ Save to Photos</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnDark]}
            onPress={() => shareMeme({ url: imageUrl, title: name })}
            accessibilityRole="button"
            accessibilityLabel="Share meme"
          >
            <Text style={styles.btnText}>↗ Share Meme</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnDark]}
            onPress={() => copyMemeLink(imageUrl).then(() => Alert.alert("Copied!", "Image link copied to clipboard"))}
            accessibilityRole="button"
            accessibilityLabel="Copy link"
          >
            <Text style={styles.btnText}>🔗 Copy Link</Text>
          </TouchableOpacity>
        </View>

        {/* Feedback Row */}
        <View style={styles.feedbackRow}>
          <Text style={styles.feedbackLabel}>Is this meme relevant?</Text>
          <View style={styles.voteBtns}>
            <TouchableOpacity
              style={[styles.voteBtn, feedbackSent === "up" && styles.voteBtnActive]}
              onPress={() => handleVote(1)}
            >
              <Text style={styles.voteText}>👍 Yes</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.voteBtn, feedbackSent === "down" && styles.voteBtnActive]}
              onPress={() => handleVote(-1)}
            >
              <Text style={styles.voteText}>👎 No</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#09090B" },
  container: { padding: 16, gap: 16, paddingBottom: 40 },
  backBtn: { alignSelf: "flex-start", paddingVertical: 6 },
  backText: { color: "#7C3AED", fontSize: 16, fontWeight: "600" },
  title: {
    color: "#F5F5F5",
    fontSize: 22,
    fontWeight: "800",
    textTransform: "capitalize",
  },
  imageWrap: {
    width: "100%",
    height: 320,
    backgroundColor: "#18181B",
    borderRadius: 16,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "#27272A",
  },
  image: { width: "100%", height: "100%" },
  explanationBox: {
    backgroundColor: "#18181B",
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: "#27272A",
  },
  explanationText: { color: "#A1A1AA", fontSize: 14, lineHeight: 20 },
  actions: { gap: 10 },
  btn: { paddingVertical: 14, borderRadius: 12, alignItems: "center" },
  btnPurple: { backgroundColor: "#7C3AED" },
  btnDark: { backgroundColor: "#18181B", borderWidth: 1, borderColor: "#3F3F46" },
  btnText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  feedbackRow: {
    marginTop: 12,
    padding: 16,
    backgroundColor: "#18181B",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#27272A",
    alignItems: "center",
    gap: 12,
  },
  feedbackLabel: { color: "#A1A1AA", fontSize: 14, fontWeight: "600" },
  voteBtns: { flexDirection: "row", gap: 12 },
  voteBtn: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: "#27272A",
  },
  voteBtnActive: { backgroundColor: "#7C3AED" },
  voteText: { color: "#fff", fontWeight: "700", fontSize: 14 },
});

