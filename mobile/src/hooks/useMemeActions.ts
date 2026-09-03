import { Share, Alert, Platform } from "react-native";
import * as Clipboard from "expo-clipboard";
import * as FileSystem from "expo-file-system";
import * as MediaLibrary from "expo-media-library";
import { MemeItem } from "./useOfflineCache";

let Haptics: any = null;
try {
  Haptics = require("expo-haptics");
} catch {}

let Sharing: any = null;
try {
  Sharing = require("expo-sharing");
} catch {}

export function useMemeActions() {
  const shareMeme = async (meme: MemeItem) => {
    try {
      if (Haptics?.selectionAsync) {
        await Haptics.selectionAsync();
      }

      const mediaUrl = meme.gif_url || meme.gifRef || meme.image_url || meme.imageRef;
      const shareUrl = `https://app.memegpt.com/meme/${meme.slug || meme.id}`;

      if (Sharing?.isAvailableAsync && mediaUrl) {
        const isAvailable = await Sharing.isAvailableAsync();
        if (isAvailable) {
          const ext = mediaUrl.endsWith(".gif") ? "gif" : "jpg";
          const filename = `${meme.slug || meme.id}.${ext}`;
          const localUri = `${FileSystem.cacheDirectory}${filename}`;
          await FileSystem.downloadAsync(mediaUrl, localUri);
          await Sharing.shareAsync(localUri, {
            mimeType: ext === "gif" ? "image/gif" : "image/jpeg",
            dialogTitle: `Share: ${meme.name}`,
          });
          return;
        }
      }

      await Share.share({
        message: `${meme.name} — ${meme.explanation || "Found on MemeGPT"}\n${shareUrl}`,
        url: shareUrl,
        title: meme.name,
      });
    } catch (e) {
      console.warn("Share failed", e);
    }
  };

  const copyMemeLink = async (meme: MemeItem) => {
    try {
      const shareUrl = `https://app.memegpt.com/meme/${meme.slug || meme.id}`;
      await Clipboard.setStringAsync(shareUrl);
      if (Haptics?.impactAsync) {
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle?.Light || "light");
      }
      Alert.alert("Copied!", "Meme link copied to clipboard.");
    } catch (e) {
      console.warn("Copy link failed", e);
    }
  };

  const saveToCameraRoll = async (meme: MemeItem) => {
    const mediaUrl = meme.image_url || meme.imageRef || meme.gif_url || meme.gifRef;
    if (!mediaUrl) {
      Alert.alert("Error", "No image URL available for this meme.");
      return;
    }

    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission needed", "Please grant photo library permission to save memes.");
        return;
      }

      const ext = mediaUrl.endsWith(".gif") ? "gif" : "jpg";
      const filename = `${FileSystem.documentDirectory}${meme.slug || meme.id}.${ext}`;

      const { uri } = await FileSystem.downloadAsync(mediaUrl, filename);
      await MediaLibrary.saveToLibraryAsync(uri);

      if (Haptics?.notificationAsync) {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType?.Success || "success");
      }
      Alert.alert("Saved!", "Meme saved to your Photos.");
    } catch (e) {
      console.error("Save to camera roll failed", e);
      if (Haptics?.notificationAsync) {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType?.Error || "error");
      }
      Alert.alert("Error", "Could not save meme to camera roll.");
    }
  };

  return { shareMeme, copyMemeLink, saveToCameraRoll };
}
