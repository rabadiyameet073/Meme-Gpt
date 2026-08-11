/**
 * MemeCard — React Native meme result card.
 * Features: lazy image, format badges, copy, download, share, vote.
 */
import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Image, Pressable,
} from 'react-native';
import type { MemeResult } from '../lib/api';
import { useShare } from '../hooks/useShare';
import { submitFeedback } from '../lib/api';
import type { FormatPref } from '../hooks/useMemeSearch';

interface MemeCardProps {
  meme: MemeResult;
  formatPref: FormatPref;
  queryId?: string | null;
}

export function MemeCard({ meme, formatPref, queryId }: MemeCardProps) {
  const { share, downloadToGallery, shareState, downloadState } = useShare();
  const [voted, setVoted] = useState<'up' | 'down' | null>(null);

  const imageUri =
    (formatPref === 'gif' && meme.formats.gif) ||
    (formatPref === 'image' && meme.formats.image) ||
    meme.formats.webp ||
    meme.formats.image ||
    meme.preview_url ||
    '';

  const score = Math.round(meme.relevance_score * 100);

  const handleVote = (dir: 'up' | 'down') => {
    setVoted(dir);
    submitFeedback(meme.id, dir === 'up' ? 'thumbs_up' : 'thumbs_down', queryId ?? undefined);
  };

  return (
    <View style={styles.card} accessible={true} accessibilityLabel={`Meme: ${meme.name}`}>
      {/* Image */}
      <View style={styles.imageContainer}>
        {imageUri ? (
          <Image
            source={{ uri: imageUri }}
            style={styles.image}
            resizeMode="contain"
            accessibilityLabel={meme.name}
          />
        ) : (
          <View style={[styles.image, styles.placeholder]}>
            <Text style={styles.placeholderText}>No preview</Text>
          </View>
        )}
        {score > 0 && (
          <View style={styles.scoreBadge}>
            <Text style={styles.scoreText}>🎯 {score}%</Text>
          </View>
        )}
      </View>

      {/* Body */}
      <View style={styles.body}>
        <Text style={styles.title} numberOfLines={1}>{meme.name}</Text>

        {/* Emotions */}
        {meme.emotions.length > 0 && (
          <Text style={styles.emotions}>{meme.emotions.slice(0, 3).join(' · ')}</Text>
        )}

        {/* Action buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.btn, styles.btnPrimary]}
            onPress={() => {
              const fmt = formatPref === 'image' ? 'image' : 'gif';
              downloadToGallery(meme.slug, fmt, meme.id);
              submitFeedback(meme.id, 'download', queryId ?? undefined);
            }}
            accessibilityLabel="Download meme"
            accessibilityRole="button"
          >
            <Text style={styles.btnTextLight}>
              {downloadState === 'loading' ? '…' : downloadState === 'done' ? '✓ Saved' : '⬇ Save'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnSecondary]}
            onPress={() => {
              share(meme.slug, meme.name, meme.id);
              submitFeedback(meme.id, 'share', queryId ?? undefined);
            }}
            accessibilityLabel="Share meme"
            accessibilityRole="button"
          >
            <Text style={styles.btnTextDim}>
              {shareState === 'loading' ? '…' : '🔗 Share'}
            </Text>
          </TouchableOpacity>

          <Pressable
            onPress={() => handleVote('up')}
            accessibilityLabel="Thumbs up"
            accessibilityRole="button"
            style={[styles.voteBtn, voted === 'up' && styles.votedUp]}
          >
            <Text>👍</Text>
          </Pressable>
          <Pressable
            onPress={() => handleVote('down')}
            accessibilityLabel="Thumbs down"
            accessibilityRole="button"
            style={[styles.voteBtn, voted === 'down' && styles.votedDown]}
          >
            <Text>👎</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#141414',
    borderWidth: 1,
    borderColor: '#2a2a2a',
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
  },
  imageContainer: { position: 'relative', backgroundColor: '#0a0a0a' },
  image: { width: '100%', height: 220 },
  placeholder: { alignItems: 'center', justifyContent: 'center' },
  placeholderText: { color: '#525252', fontSize: 12 },
  scoreBadge: {
    position: 'absolute', top: 8, left: 8,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 20,
  },
  scoreText: { color: '#c4b5fd', fontSize: 11, fontWeight: '600' },
  body: { padding: 12, gap: 6 },
  title: { color: '#e5e5e5', fontWeight: '600', fontSize: 14 },
  emotions: { color: '#737373', fontSize: 11 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 4, alignItems: 'center' },
  btn: { flex: 1, paddingVertical: 8, borderRadius: 10, alignItems: 'center' },
  btnPrimary: { backgroundColor: '#7C3AED' },
  btnSecondary: { backgroundColor: '#262626' },
  btnTextLight: { color: '#fff', fontWeight: '600', fontSize: 12 },
  btnTextDim: { color: '#a3a3a3', fontWeight: '600', fontSize: 12 },
  voteBtn: { padding: 8, borderRadius: 8, backgroundColor: '#1e1e1e' },
  votedUp: { backgroundColor: '#166534' },
  votedDown: { backgroundColor: '#7f1d1d' },
});
