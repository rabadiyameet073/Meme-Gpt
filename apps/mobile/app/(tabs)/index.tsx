/**
 * Home / Search Tab — main search interface.
 * Input → AI results → tap for BottomSheet detail.
 */
import React, { useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet, FlatList, TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SearchBar } from '../../components/SearchBar';
import { MemeCard } from '../../components/MemeCard';
import { FormatPicker } from '../../components/FormatPicker';
import { BottomSheet } from '../../components/BottomSheet';
import { useMemeSearch, FormatPref } from '../../hooks/useMemeSearch';
import type { MemeResult } from '../../lib/api';

const SUGGESTION_CHIPS = [
  '🤦 Monday vibe',
  '😤 When the bug is back',
  '🎉 Code worked first try',
  '😴 Friday afternoon',
  '😭 Exam szn',
  '📧 Boss emailed at midnight',
];

export default function SearchTab() {
  const [formatPref, setFormatPref] = useState<FormatPref>('gif');
  const [selectedMeme, setSelectedMeme] = useState<MemeResult | null>(null);
  const { results, loading, error, queryId, search, sendFeedback } = useMemeSearch(formatPref);

  return (
    <SafeAreaView style={styles.safe} edges={['bottom']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>
            <Text style={styles.logoAccent}>Meme</Text>GPT
          </Text>
          <Text style={styles.subtitle}>Type anything. Get the perfect meme.</Text>
        </View>

        {/* Search input */}
        <SearchBar
          onSearch={search}
          loading={loading}
          placeholder="What's happening? 🤔"
        />

        {/* Error */}
        {error && <Text style={styles.error}>⚠ {error}</Text>}

        {/* Suggestion chips (only when no results) */}
        {!results.length && !loading && (
          <View style={styles.chips}>
            {SUGGESTION_CHIPS.map((chip) => (
              <TouchableOpacity
                key={chip}
                onPress={() => search(chip)}
                style={styles.chip}
                accessibilityRole="button"
                accessibilityLabel={`Search: ${chip}`}
              >
                <Text style={styles.chipText}>{chip}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Format picker */}
        {(results.length > 0 || loading) && (
          <FormatPicker value={formatPref} onChange={setFormatPref} />
        )}

        {/* Loading skeletons */}
        {loading && (
          <View style={styles.skeletons}>
            {[1, 2, 3].map((i) => (
              <View key={i} style={styles.skeleton} />
            ))}
          </View>
        )}

        {/* Results */}
        {results.map((meme) => (
          <TouchableOpacity
            key={meme.id}
            onPress={() => {
              setSelectedMeme(meme);
              sendFeedback(meme.id, 'click');
            }}
            activeOpacity={0.9}
            accessibilityRole="button"
            accessibilityLabel={`Open ${meme.name}`}
          >
            <MemeCard meme={meme} formatPref={formatPref} queryId={queryId} />
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Bottom sheet for meme detail */}
      <BottomSheet
        meme={selectedMeme}
        visible={selectedMeme !== null}
        onClose={() => setSelectedMeme(null)}
        queryId={queryId}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A0A0A' },
  scroll: { flex: 1 },
  container: { padding: 16, gap: 16, paddingBottom: 40 },
  header: { gap: 4 },
  logo: { fontSize: 26, fontWeight: '900', color: '#F5F5F5' },
  logoAccent: { color: '#7C3AED' },
  subtitle: { fontSize: 13, color: '#737373' },
  error: { fontSize: 13, color: '#f87171' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    backgroundColor: '#1e1e1e',
    borderWidth: 1,
    borderColor: '#3f3f3f',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20,
  },
  chipText: { color: '#a3a3a3', fontSize: 12 },
  skeletons: { gap: 12 },
  skeleton: {
    height: 280,
    backgroundColor: '#1e1e1e',
    borderRadius: 16,
  },
});
