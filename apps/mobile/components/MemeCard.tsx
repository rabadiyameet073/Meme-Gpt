import React, { useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Pressable,
  Alert,
} from "react-native";
import { Image } from "expo-image";
import * as Clipboard from "expo-clipboard";
import { CachedMeme } from "../hooks/useOfflineCache";
import { useShareAndDownload } from "../hooks/useShareAndDownload";

let Haptics: any = null;
try {
  Haptics = require("expo-haptics");
} catch {}

interface MemeCardProps {
  meme: CachedMeme | any;
  onPress?: () => void;
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
}

export function MemeCard({
  meme,
  onPress,
  onFavorite,
  isFavorited = false,
}: MemeCardProps) {
  const { shareMeme, downloadMeme } = useShareAndDownload();
  const [favorited, setFavorited] = useState(isFavorited);
  const heartScale = useRef(new Animated.Value(1)).current;
  const lastTap = useRef<number>(0);

  // Double-tap to favorite
  const handleDoubleTap = () => {
    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300;

    if (now - lastTap.current < DOUBLE_TAP_DELAY) {
      if (Haptics?.impactAsync) {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle?.Medium || "medium");
      }
      setFavorited(true);
      onFavorite?.(String(meme.id));

      Animated.sequence([
        Animated.spring(heartScale, { toValue: 1.5, useNativeDriver: true }),
        Animated.spring(heartScale, { toValue: 1.0, useNativeDriver: true }),
      ]).start();
    } else {
      onPress?.();
    }
    lastTap.current = now;
  };

  const mediaUrl = meme.gif_url || meme.image_url || meme.thumb_url || "";

  return (
    <Pressable onPress={handleDoubleTap} style={styles.card}>
      {mediaUrl ? (
        <Image
          source={{ uri: mediaUrl }}
          style={styles.image}
          contentFit="cover"
          transition={200}
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
            onPress={() => shareMeme(mediaUrl, meme.name)}
            accessibilityLabel={`Share ${meme.name}`}
          >
            <Text style={styles.actionIcon}>📤</Text>
            <Text style={styles.actionText}>Share</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionBtn}
            onPress={async () => {
              if (Haptics?.impactAsync) {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle?.Light || "light");
              }
              const link = `https://app.memegpt.com/meme/${meme.slug || meme.id}`;
              await Clipboard.setStringAsync(link);
              Alert.alert("Copied!", "Link copied to clipboard.");
            }}
            accessibilityLabel={`Copy link for ${meme.name}`}
          >
            <Text style={styles.actionIcon}>🔗</Text>
            <Text style={styles.actionText}>Copy</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionBtn, styles.saveBtn]}
            onPress={async () => {
              const ok = await downloadMeme(mediaUrl);
              if (ok) {
                Alert.alert("Saved!", "Meme saved to your photo library.");
              }
            }}
            accessibilityLabel={`Save ${meme.name} to camera roll`}
          >
            <Text style={styles.actionIcon}>💾</Text>
            <Text style={[styles.actionText, styles.saveText]}>Save</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.favBtn}
            onPress={() => {
              if (Haptics?.selectionAsync) {
                Haptics.selectionAsync();
              }
              const next = !favorited;
              setFavorited(next);
              onFavorite?.(String(meme.id));
            }}
            accessibilityLabel={favorited ? "Unfavorite" : "Favorite"}
          >
            <Animated.Text
              style={[styles.favIcon, { transform: [{ scale: heartScale }] }]}
            >
              {favorited ? "❤️" : "🤍"}
            </Animated.Text>
          </TouchableOpacity>
        </View>
      </View>
    </Pressable>
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
    alignItems: "center",
  },
  actionBtn: {
    flex: 1,
    flexDirection: "row",
    backgroundColor: "#27272A",
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
  },
  actionIcon: {
    fontSize: 13,
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
  favBtn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: "rgba(255, 255, 255, 0.07)",
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
  },
  favIcon: {
    fontSize: 16,
  },
});
