import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';
import * as Haptics from 'expo-haptics';
import { Alert } from 'react-native';

export function useShareAndDownload() {
  const shareMeme = async (url: string, title: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      const isGif = url.toLowerCase().endsWith('.gif');
      const ext = isGif ? 'gif' : 'jpg';
      const filename = `memegpt_${Date.now()}.${ext}`;
      const fileUri = `${FileSystem.cacheDirectory}${filename}`;

      await FileSystem.downloadAsync(url, fileUri);
      await Sharing.shareAsync(fileUri, {
        mimeType: isGif ? 'image/gif' : 'image/jpeg',
        dialogTitle: `Share: ${title}`,
      });
    } catch (e) {
      Alert.alert('Share failed', String(e));
    }
  };

  const downloadMeme = async (url: string): Promise<boolean> => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

      // Request permissions
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Allow access to save memes to your library.');
        return false;
      }

      const isGif = url.toLowerCase().endsWith('.gif');
      const ext = isGif ? 'gif' : 'jpg';
      const filename = `memegpt_${Date.now()}.${ext}`;
      const fileUri = `${FileSystem.documentDirectory || FileSystem.cacheDirectory}${filename}`;

      const download = await FileSystem.downloadAsync(url, fileUri);

      if (download.status === 200) {
        await MediaLibrary.saveToLibraryAsync(download.uri);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        return true;
      }
      return false;
    } catch (e) {
      Alert.alert('Download failed', String(e));
      return false;
    }
  };

  return { shareMeme, downloadMeme };
}
