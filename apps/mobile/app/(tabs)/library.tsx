/**
 * Library Tab — saved memes, offline cached, organized by collection.
 * Uses AsyncStorage for persistence (MMKV upgrade path in Phase 2).
 */
import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity, Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { MemeResult } from '../../lib/api';
import { BottomSheet } from '../../components/BottomSheet';

const STORAGE_KEY = 'memegpt_saved_memes';

async function loadSaved(): Promise<MemeResult[]> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export default function LibraryTab() {
  const [saved, setSaved] = useState<MemeResult[]>([]);
  const [selected, setSelected] = useState<MemeResult | null>(null);

  useEffect(() => {
    loadSaved().then(setSaved);
  }, []);

  const remove = async (id: string) => {
    const updated = saved.filter((m) => m.id !== id);
    setSaved(updated);
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  return (
    <SafeAreaView style={styles.safe} edges={['bottom']}>
      <View style={styles.header}>
        <Text style={styles.title}>📚 Library</Text>
        <Text style={styles.subtitle}>{saved.length} saved meme{saved.length !== 1 ? 's' : ''}</Text>
      </View>

      {saved.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>📭</Text>
          <Text style={styles.emptyTitle}>No saved memes yet</Text>
          <Text style={styles.emptyHint}>
            Tap ⬇ on any meme to save it to your library.
          </Text>
        </View>
      ) : (
        <FlatList
          data={saved}
          keyExtractor={(m) => m.id}
          numColumns={2}
          contentContainerStyle={styles.grid}
          columnWrapperStyle={{ gap: 10 }}
          renderItem={({ item }) => {
            const img = item.formats.gif || item.formats.image || item.preview_url || '';
            return (
              <TouchableOpacity
                style={styles.card}
                onPress={() => setSelected(item)}
                activeOpacity={0.85}
                accessibilityRole="button"
                accessibilityLabel={`Open ${item.name}`}
              >
                <Image source={{ uri: img }} style={styles.cardImg} resizeMode="contain" />
                <View style={styles.cardBody}>
                  <Text style={styles.cardName} numberOfLines={1}>{item.name}</Text>
                  <TouchableOpacity
                    onPress={() => remove(item.id)}
                    accessibilityRole="button"
                    accessibilityLabel={`Remove ${item.name}`}
                    hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}
                  >
                    <Text style={styles.removeBtn}>✕</Text>
                  </TouchableOpacity>
                </View>
              </TouchableOpacity>
            );
          }}
        />
      )}

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
  header: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  title: { color: '#F5F5F5', fontSize: 22, fontWeight: '800' },
  subtitle: { color: '#737373', fontSize: 13, marginTop: 2 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 10 },
  emptyIcon: { fontSize: 48 },
  emptyTitle: { color: '#a3a3a3', fontSize: 17, fontWeight: '700' },
  emptyHint: { color: '#525252', fontSize: 13, textAlign: 'center', maxWidth: 260 },
  grid: { padding: 16, gap: 10, paddingBottom: 40 },
  card: {
    flex: 1,
    backgroundColor: '#141414',
    borderWidth: 1,
    borderColor: '#2a2a2a',
    borderRadius: 14,
    overflow: 'hidden',
  },
  cardImg: { width: '100%', height: 130 },
  cardBody: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 8,
  },
  cardName: { color: '#d4d4d4', fontSize: 11, fontWeight: '600', flex: 1 },
  removeBtn: { color: '#525252', fontSize: 12, paddingLeft: 6 },
});
