/**
 * BottomSheet — React Native bottom sheet for meme detail/actions.
 * Used when user taps a meme card to see full options.
 */
import React, { useEffect, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Animated,
  Modal, Pressable, ScrollView, Image,
} from 'react-native';
import type { MemeResult } from '../lib/api';
import { useShare } from '../hooks/useShare';
import { submitFeedback } from '../lib/api';

interface BottomSheetProps {
  meme: MemeResult | null;
  visible: boolean;
  onClose: () => void;
  queryId?: string | null;
}

export function BottomSheet({ meme, visible, onClose, queryId }: BottomSheetProps) {
  const translateY = useRef(new Animated.Value(400)).current;
  const { share, downloadToGallery, shareState, downloadState } = useShare();

  useEffect(() => {
    Animated.spring(translateY, {
      toValue: visible ? 0 : 400,
      useNativeDriver: true,
      tension: 65,
      friction: 11,
    }).start();
  }, [visible]);

  if (!meme) return null;

  const imgSrc = meme.formats.gif || meme.formats.image || meme.preview_url || '';

  return (
    <Modal transparent visible={visible} onRequestClose={onClose} animationType="none">
      <Pressable style={styles.backdrop} onPress={onClose} accessible accessibilityLabel="Close">
        <Animated.View
          style={[styles.sheet, { transform: [{ translateY }] }]}
          // Stop backdrop press from propagating through the sheet
          onStartShouldSetResponder={() => true}
        >
          {/* Handle bar */}
          <View style={styles.handle} />

          <ScrollView showsVerticalScrollIndicator={false}>
            {/* Meme name */}
            <Text style={styles.title}>{meme.name}</Text>

            {/* Image preview */}
            <View style={styles.imageWrap}>
              {imgSrc ? (
                <Image source={{ uri: imgSrc }} style={styles.image} resizeMode="contain" />
              ) : (
                <View style={[styles.image, styles.placeholder]}>
                  <Text style={styles.placeholderText}>No preview available</Text>
                </View>
              )}
            </View>

            {/* Categories */}
            {meme.categories.length > 0 && (
              <View style={styles.tags}>
                {meme.categories.map((c) => (
                  <View key={c} style={styles.tag}>
                    <Text style={styles.tagText}>{c}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Action buttons */}
            <View style={styles.actions}>
              <TouchableOpacity
                style={[styles.actionBtn, styles.btnPurple]}
                onPress={() => {
                  downloadToGallery(meme.slug, 'gif', meme.id);
                  submitFeedback(meme.id, 'download', queryId ?? undefined);
                }}
                accessibilityRole="button"
                accessibilityLabel="Download GIF"
              >
                <Text style={styles.actionBtnText}>
                  {downloadState === 'loading' ? '⏳ Saving…' : downloadState === 'done' ? '✓ Saved to Gallery' : '⬇ Download GIF'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionBtn, styles.btnDark]}
                onPress={() => {
                  downloadToGallery(meme.slug, 'image', meme.id);
                  submitFeedback(meme.id, 'download', queryId ?? undefined);
                }}
                accessibilityRole="button"
                accessibilityLabel="Download Image"
              >
                <Text style={styles.actionBtnText}>⬇ Download Image</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionBtn, styles.btnDark]}
                onPress={() => {
                  share(meme.slug, meme.name, meme.id);
                  submitFeedback(meme.id, 'share', queryId ?? undefined);
                }}
                accessibilityRole="button"
                accessibilityLabel="Share meme"
              >
                <Text style={styles.actionBtnText}>
                  {shareState === 'loading' ? '🔗 Sharing…' : '🔗 Share'}
                </Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </Animated.View>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#141414',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 16,
    paddingBottom: 40,
    maxHeight: '85%',
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: '#3f3f3f',
    borderRadius: 2,
    alignSelf: 'center',
    marginVertical: 12,
  },
  title: {
    color: '#f5f5f5',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
  },
  imageWrap: {
    backgroundColor: '#0a0a0a',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 12,
  },
  image: { width: '100%', height: 280 },
  placeholder: { alignItems: 'center', justifyContent: 'center' },
  placeholderText: { color: '#525252', fontSize: 13 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 16 },
  tag: {
    backgroundColor: '#1e1e1e',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#2a2a2a',
  },
  tagText: { color: '#a3a3a3', fontSize: 11 },
  actions: { gap: 8 },
  actionBtn: {
    paddingVertical: 13,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnPurple: { backgroundColor: '#7C3AED' },
  btnDark: { backgroundColor: '#262626' },
  actionBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
});
