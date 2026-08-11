/**
 * Meme detail screen — /meme/[id]
 * Shows full meme with all formats and action buttons.
 */
import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { useShare } from '../../hooks/useShare';
import { submitFeedback } from '../../lib/api';

export default function MemeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { share, downloadToGallery, shareState, downloadState } = useShare();

  // In a real implementation, this would fetch from API
  // For now it receives meme data via navigation params or fetches by id
  const slug = typeof id === 'string' ? id : '';

  return (
    <SafeAreaView style={styles.safe} edges={['bottom']}>
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

        <Text style={styles.title}>{slug.replace(/-/g, ' ')}</Text>

        {/* Placeholder image area */}
        <View style={styles.imageWrap}>
          <Text style={styles.imageHint}>Meme preview would load here</Text>
        </View>

        {/* Action buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.btn, styles.btnPurple]}
            onPress={() => downloadToGallery(slug, 'gif')}
            accessibilityRole="button"
            accessibilityLabel="Download GIF"
          >
            <Text style={styles.btnText}>
              {downloadState === 'loading' ? '⏳ Saving…' : downloadState === 'done' ? '✓ Saved' : '⬇ Download GIF'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnDark]}
            onPress={() => share(slug, slug)}
            accessibilityRole="button"
            accessibilityLabel="Share meme"
          >
            <Text style={styles.btnText}>
              {shareState === 'loading' ? '🔗 Sharing…' : '🔗 Share'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnDark]}
            onPress={() => submitFeedback(slug, 'thumbs_up')}
            accessibilityRole="button"
            accessibilityLabel="Thumbs up"
          >
            <Text style={styles.btnText}>👍 More like this</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A0A0A' },
  container: { padding: 16, gap: 16, paddingBottom: 40 },
  backBtn: { alignSelf: 'flex-start' },
  backText: { color: '#7C3AED', fontSize: 15, fontWeight: '600' },
  title: {
    color: '#F5F5F5',
    fontSize: 20,
    fontWeight: '700',
    textTransform: 'capitalize',
  },
  imageWrap: {
    height: 280,
    backgroundColor: '#141414',
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#2a2a2a',
  },
  imageHint: { color: '#525252', fontSize: 13 },
  actions: { gap: 10 },
  btn: { paddingVertical: 13, borderRadius: 12, alignItems: 'center' },
  btnPurple: { backgroundColor: '#7C3AED' },
  btnDark: { backgroundColor: '#1e1e1e' },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
});
