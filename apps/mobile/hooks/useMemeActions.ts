/**
 * MemeGPT Mobile — Meme Actions Hook
 * Handles saving to camera roll, system sharing, and clipboard copying.
 * Specification: 05_Mobile_App_Completion.md
 */

import { Alert } from "react-native";
import * as MediaLibrary from "expo-media-library";
import * as Sharing from "expo-sharing";
import * as Clipboard from "expo-clipboard";
import * as FileSystem from "expo-file-system";

export function useMemeActions() {
  const saveToCameraRoll = async (imageUrl: string): Promise<boolean> => {
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission needed", "Please allow photo library access to save memes.");
        return false;
      }
      const filename = (FileSystem.cacheDirectory || "") + "meme_" + Date.now() + ".jpg";
      await FileSystem.downloadAsync(imageUrl, filename);
      await MediaLibrary.saveToLibraryAsync(filename);
      return true;
    } catch {
      return false;
    }
  };

  const shareMeme = async ({ url, title }: { url: string; title?: string }): Promise<void> => {
    try {
      const filename = (FileSystem.cacheDirectory || "") + "meme_share_" + Date.now() + ".jpg";
      await FileSystem.downloadAsync(url, filename);
      await Sharing.shareAsync(filename, { dialogTitle: title || "Share Meme" });
    } catch {
      /* silently fail */
    }
  };

  const copyMemeLink = async (url: string): Promise<void> => {
    await Clipboard.setStringAsync(url);
  };

  return { saveToCameraRoll, shareMeme, copyMemeLink };
}
