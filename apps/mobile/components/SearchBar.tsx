/**
 * SearchBar — React Native search input.
 * Shows placeholder, handles submission via keyboard return.
 */
import React, { useState } from 'react';
import {
  View, TextInput, TouchableOpacity, Text, StyleSheet, ActivityIndicator,
} from 'react-native';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}

export function SearchBar({ onSearch, loading = false, placeholder = "What's happening? 🤔" }: SearchBarProps) {
  const [value, setValue] = useState('');

  const handleSubmit = () => {
    const q = value.trim();
    if (!q || loading) return;
    onSearch(q);
  };

  return (
    <View style={styles.container}>
      <TextInput
        value={value}
        onChangeText={setValue}
        onSubmitEditing={handleSubmit}
        placeholder={placeholder}
        placeholderTextColor="#525252"
        maxLength={2000}
        multiline
        style={styles.input}
        returnKeyType="search"
        accessibilityLabel="Search for a meme"
        accessibilityHint="Type a feeling or situation then press search"
      />
      <TouchableOpacity
        onPress={handleSubmit}
        disabled={!value.trim() || loading}
        style={[styles.button, (!value.trim() || loading) && styles.buttonDisabled]}
        accessibilityRole="button"
        accessibilityLabel="Search"
      >
        {loading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Text style={styles.buttonText}>Search</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#141414',
    borderWidth: 1.5,
    borderColor: '#3f3f3f',
    borderRadius: 14,
    padding: 12,
    gap: 8,
  },
  input: {
    color: '#f5f5f5',
    fontSize: 15,
    lineHeight: 22,
    minHeight: 60,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: '#7C3AED',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: '#fff', fontWeight: '700', fontSize: 14 },
});
