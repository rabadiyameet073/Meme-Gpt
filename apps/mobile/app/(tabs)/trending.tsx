/**
 * Trending Tab — hourly-updated trending memes.
 * Filter by category chips.
 */
import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getTrending } from '../../lib/api';
import type { MemeResult } from '../../lib/api';
import { MemeCard } from '../../components/MemeCard';
import { BottomSheet } from '../../components/BottomSheet';
import { FormatPicker } from '../../components/FormatPicker';
import type { FormatPref } from '../../hooks/useMemeSearch';

const CATEGORIES = ['all', 'work', 'coding', 'gaming', 'exam', 'relationship', 'general'];

export default function TrendingTab() {
  const [category, setCategory] = useState('all');
  const [formatPref, setFormatPref] = useState<FormatPref>('gif');
  const [memes, setMemes] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<MemeResult | null>(null);

  useEffect(() => {
    setLoading(true);
    getTrending(category, 20)
      .then((data) => setMemes(Array.isArray(data) ? data : []))
      .catch(() => setMemes([]))
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <SafeAreaView style={styles.safe} edges={['bottom']}>
      <View style={styles.container}>
        {/* Category filter */}
        <FlatList
          data={CATEGORIES}
          horizontal
          showsHorizontalScrollIndicator={false}
          keyExtractor={(c) => c}
          style={styles.catList}
          contentContainerStyle={{ gap: 8, paddingHorizontal: 16 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => setCategory(item)}
              style={[styles.catChip, category === item && styles.catChipActive]}
              accessibilityRole="button"
              accessibilityState={{ selected: category === item }}
            >
              <Text style={[styles.catText, category === item && styles.catTextActive]}>
                {item}
              </Text>
            </TouchableOpacity>
          )}
        />

        {/* Format picker */}
        <View style={{ paddingHorizontal: 16 }}>
          <FormatPicker value={formatPref} onChange={setFormatPref} />
        </View>

        {/* Loading */}
        {loading && (
          <View style={styles.loadingWrap}>
            <ActivityIndicator color="#7C3AED" size="large" />
            <Text style={styles.loadingText}>Loading trending memes…</Text>
          </View>
        )}

        {/* Meme list */}
        {!loading && (
          <FlatList
            data={memes}
            keyExtractor={(m) => m.id}
            contentContainerStyle={{ padding: 16, gap: 12 }}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={styles.emptyIcon}>🦗</Text>
                <Text style={styles.emptyText}>No trending memes yet.</Text>
                <Text style={styles.emptyHint}>Run the data pipeline first.</Text>
              </View>
            }
            renderItem={({ item }) => (
              <TouchableOpacity onPress={() => setSelected(item)} activeOpacity={0.9}>
                <MemeCard meme={item} formatPref={formatPref} />
              </TouchableOpacity>
            )}
          />
        )}
      </View>

      <BottomSheet
        meme={selected}
        visible={selected !== null}
        onClose={() => setSelected(null)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A0A0A' },
  container: { flex: 1, gap: 12 },
  catList: { paddingTop: 12 },
  catChip: {
    backgroundColor: '#1e1e1e',
    borderWidth: 1,
    borderColor: '#3f3f3f',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20,
  },
  catChipActive: { backgroundColor: '#F59E0B', borderColor: '#F59E0B' },
  catText: { color: '#a3a3a3', fontSize: 12, fontWeight: '600', textTransform: 'capitalize' },
  catTextActive: { color: '#000' },
  loadingWrap: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  loadingText: { color: '#737373', fontSize: 13 },
  empty: { alignItems: 'center', paddingTop: 60, gap: 8 },
  emptyIcon: { fontSize: 40 },
  emptyText: { color: '#737373', fontSize: 15, fontWeight: '600' },
  emptyHint: { color: '#525252', fontSize: 12 },
});
