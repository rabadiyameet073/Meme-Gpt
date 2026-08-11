/**
 * FormatPicker — React Native format selector: GIF | Image | Video
 * Persists selection using MMKV (falls back to AsyncStorage).
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import type { FormatPref } from '../hooks/useMemeSearch';

const FORMATS: { value: FormatPref; label: string; emoji: string }[] = [
  { value: 'gif', label: 'GIF', emoji: '🎞' },
  { value: 'image', label: 'Image', emoji: '🖼' },
  { value: 'video', label: 'Video', emoji: '🎬' },
];

interface FormatPickerProps {
  value: FormatPref;
  onChange: (fmt: FormatPref) => void;
}

export function FormatPicker({ value, onChange }: FormatPickerProps) {
  return (
    <View style={styles.container} accessibilityRole="radiogroup" accessibilityLabel="Select meme format">
      <Text style={styles.label}>Format:</Text>
      <View style={styles.buttons}>
        {FORMATS.map((fmt) => (
          <TouchableOpacity
            key={fmt.value}
            onPress={() => onChange(fmt.value)}
            style={[styles.btn, value === fmt.value && styles.btnActive]}
            accessibilityRole="radio"
            accessibilityState={{ checked: value === fmt.value }}
            accessibilityLabel={`${fmt.label} format`}
          >
            <Text style={styles.emoji} aria-hidden>{fmt.emoji}</Text>
            <Text style={[styles.btnText, value === fmt.value && styles.btnTextActive]}>
              {fmt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#141414',
    borderWidth: 1,
    borderColor: '#2a2a2a',
    borderRadius: 12,
    padding: 6,
    gap: 6,
  },
  label: { color: '#525252', fontSize: 11, marginLeft: 4 },
  buttons: { flexDirection: 'row', gap: 4, flex: 1 },
  btn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingVertical: 7,
    borderRadius: 8,
    backgroundColor: 'transparent',
  },
  btnActive: { backgroundColor: '#7C3AED' },
  emoji: { fontSize: 12 },
  btnText: { color: '#737373', fontWeight: '600', fontSize: 12 },
  btnTextActive: { color: '#fff' },
});
