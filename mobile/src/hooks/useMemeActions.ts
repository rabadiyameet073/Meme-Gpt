import { Share, Alert, Platform } from "react-native";
import * as Clipboard from "expo-clipboard";
import * as FileSystem from "expo-file-system";
import * as MediaLibrary from "expo-media-library";
import { MemeItem } from "./useOfflineCache";

export function useMemeActions() {
  const shareMeme = async (meme: MemeItem) => {
    try {
      const shareUrl = `https://app.memegpt.com/meme/${meme.slug || meme.id}`;
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
      Alert.alert("Saved!", "Meme saved to your Photos.");
    } catch (e) {
      console.error("Save to camera roll failed", e);
      Alert.alert("Error", "Could not save meme to camera roll.");
    }
  };

  return { shareMeme, copyMemeLink, saveToCameraRoll };
}
