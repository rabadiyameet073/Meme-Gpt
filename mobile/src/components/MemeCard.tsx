import React from "react";
import { View, Text, Image, StyleSheet, TouchableOpacity } from "react-native";
import { MemeItem } from "../hooks/useOfflineCache";
import { useMemeActions } from "../hooks/useMemeActions";

interface MemeCardProps {
  meme: MemeItem;
  onPress?: () => void;
}

export function MemeCard({ meme, onPress }: MemeCardProps) {
  const { shareMeme, copyMemeLink, saveToCameraRoll } = useMemeActions();
  const imageUrl = meme.thumb_url || meme.image_url || meme.imageRef || meme.gif_url || meme.gifRef;

  return (
    <TouchableOpacity activeOpacity={0.85} onPress={onPress} style={styles.card}>
      {imageUrl ? (
        <Image
          source={{ uri: imageUrl }}
          style={styles.image}
          resizeMode="cover"
        />
      ) : (
        <View style={[styles.image, styles.placeholder]}>
          <Text style={styles.placeholderText}>🎭</Text>
        </View>
      )}

      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>
          {meme.name}
        </Text>
        {meme.explanation ? (
          <Text style={styles.explanation} numberOfLines={2}>
            {meme.explanation}
          </Text>
        ) : null}

        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => shareMeme(meme)}
          >
            <Text style={styles.actionText}>Share</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => copyMemeLink(meme)}
          >
            <Text style={styles.actionText}>Copy Link</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionBtn, styles.saveBtn]}
            onPress={() => saveToCameraRoll(meme)}
          >
            <Text style={[styles.actionText, styles.saveText]}>Save</Text>
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#18181B",
    borderRadius: 16,
    overflow: "hidden",
    marginVertical: 8,
    marginHorizontal: 16,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.08)",
  },
  image: {
    width: "100%",
    height: 220,
    backgroundColor: "#27272A",
  },
  placeholder: {
    justifyContent: "center",
    alignItems: "center",
  },
  placeholderText: {
    fontSize: 48,
  },
  content: {
    padding: 14,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: "#FAFAFA",
    marginBottom: 4,
  },
  explanation: {
    fontSize: 13,
    color: "#A1A1AA",
    lineHeight: 18,
    marginBottom: 12,
  },
  actions: {
    flexDirection: "row",
    gap: 8,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: "#27272A",
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: "center",
  },
  actionText: {
    color: "#FAFAFA",
    fontSize: 12,
    fontWeight: "600",
  },
  saveBtn: {
    backgroundColor: "#7C3AED",
  },
  saveText: {
    color: "#FFFFFF",
  },
});
