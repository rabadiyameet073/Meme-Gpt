import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, Stack, router } from 'expo-router';
import { Image } from 'expo-image';
import { api } from '../../lib/api';
import { useShareAndDownload } from '../../hooks/useShareAndDownload';

const { width } = Dimensions.get('window');

export default function MemeDetailScreen() {
  const params = useLocalSearchParams<{
    id: string;
    name?: string;
    imageUrl?: string;
    gifUrl?: string;
    explanation?: string;
  }>();

  const id = typeof params.id === 'string' ? params.id : '';
  const [meme, setMeme] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);
  const { shareMeme, downloadMeme } = useShareAndDownload();

  useEffect(() => {
    let isMounted = true;
    if (id) {
      api
        .getMeme(id)
        .then((data) => {
          if (isMounted) setMeme(data);
        })
        .catch(() => {
          // Fall back to params if offline or error
          if (isMounted) {
            setMeme({
              id,
              name: params.name || id.replace(/-/g, ' '),
              image_url: params.imageUrl || '',
              gif_url: params.gifUrl || '',
              explanation: params.explanation || '',
              categories: [],
              emotions: [],
            });
          }
        })
        .finally(() => {
          if (isMounted) setLoading(false);
        });
    } else {
      setLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [id, params.name, params.imageUrl, params.gifUrl, params.explanation]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#7C3AED" />
      </View>
    );
  }

  if (!meme) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>Meme not found</Text>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtnInline}>
          <Text style={styles.backText}>← Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const mediaUrl = meme.gif_url || meme.image_url || params.gifUrl || params.imageUrl || '';
  const emotionsList = meme.emotions || (meme.emotion ? [meme.emotion] : []);
  const categoriesList = meme.categories || (meme.category ? [meme.category] : []);

  const handleVote = async (type: 'thumbs_up' | 'thumbs_down') => {
    try {
      await api.submitFeedback(meme.id || id, type);
      setFeedbackSent(type);
      Alert.alert(
        'Feedback recorded',
        type === 'thumbs_up' ? 'Glad you liked it! 👍' : "We'll improve recommendations! 👎"
      );
    } catch {
      Alert.alert('Feedback', 'Thank you for your rating!');
    }
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <Stack.Screen options={{ title: meme.name || 'Meme Detail', headerShown: false }} />

      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
        {/* Back navigation header */}
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>

        {/* Media Preview Box */}
        <View style={styles.imageWrap}>
          {mediaUrl ? (
            <Image
              source={{ uri: mediaUrl }}
              style={styles.image}
              contentFit="contain"
              transition={300}
            />
          ) : (
            <View style={[styles.image, styles.placeholder]}>
              <Text style={styles.placeholderText}>🎭</Text>
            </View>
          )}
        </View>

        {/* Info & Details */}
        <View style={styles.info}>
          <Text style={styles.title}>{meme.name}</Text>
          {meme.explanation ? <Text style={styles.subtitle}>{meme.explanation}</Text> : null}

          {/* Tags */}
          {(categoriesList.length > 0 || emotionsList.length > 0) && (
            <View style={styles.tags}>
              {categoriesList.map((c: string) => (
                <View key={`cat-${c}`} style={styles.catTag}>
                  <Text style={styles.catTagText}>#{c}</Text>
                </View>
              ))}
              {emotionsList.map((e: string) => (
                <View key={`emo-${e}`} style={styles.tag}>
                  <Text style={styles.tagText}>{e}</Text>
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Primary Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.btn, styles.btnPurple]}
            onPress={async () => {
              const ok = await downloadMeme(mediaUrl);
              if (ok) Alert.alert('Saved!', 'Meme saved to your photo library.');
            }}
            accessibilityRole="button"
            accessibilityLabel="Save to Photos"
          >
            <Text style={styles.btnText}>💾 Save to Photos</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btn, styles.btnDark]}
            onPress={() => shareMeme(mediaUrl, meme.name)}
            accessibilityRole="button"
            accessibilityLabel="Share meme"
          >
            <Text style={styles.btnText}>📤 Share Meme</Text>
          </TouchableOpacity>
        </View>

        {/* Relevance / Feedback Section */}
        <View style={styles.feedbackRow}>
          <Text style={styles.feedbackLabel}>Is this meme relevant?</Text>
          <View style={styles.voteBtns}>
            <TouchableOpacity
              style={[styles.voteBtn, feedbackSent === 'thumbs_up' && styles.voteBtnActive]}
              onPress={() => handleVote('thumbs_up')}
            >
              <Text style={styles.voteText}>👍 Yes</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.voteBtn, feedbackSent === 'thumbs_down' && styles.voteBtnActive]}
              onPress={() => handleVote('thumbs_down')}
            >
              <Text style={styles.voteText}>👎 No</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A0A0A' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0A0A0A', padding: 20 },
  container: { flex: 1, backgroundColor: '#0A0A0A' },
  contentContainer: { paddingBottom: 40 },
  backBtn: { paddingHorizontal: 16, paddingVertical: 10, alignSelf: 'flex-start' },
  backBtnInline: { marginTop: 16 },
  backText: { color: '#7C3AED', fontSize: 16, fontWeight: '700' },
  imageWrap: {
    width,
    height: width * 0.85,
    backgroundColor: '#18181B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: { width: '100%', height: '100%' },
  placeholder: { justifyContent: 'center', alignItems: 'center' },
  placeholderText: { fontSize: 48 },
  info: { padding: 16 },
  title: { fontSize: 22, fontWeight: '800', color: '#F5F5F5', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#A3A3A3', lineHeight: 21 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 12, gap: 6 },
  catTag: {
    backgroundColor: 'rgba(56, 189, 248, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  catTagText: { color: '#38BDF8', fontSize: 12, fontWeight: '700' },
  tag: {
    backgroundColor: '#7C3AED22',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  tagText: { color: '#7C3AED', fontSize: 12, fontWeight: '700' },
  actions: { paddingHorizontal: 16, gap: 10, marginTop: 16 },
  btn: { paddingVertical: 14, borderRadius: 12, alignItems: 'center' },
  btnPurple: { backgroundColor: '#7C3AED' },
  btnDark: { backgroundColor: '#18181B', borderWidth: 1, borderColor: '#3F3F46' },
  btnText: { color: '#ffffff', fontWeight: '700', fontSize: 15 },
  feedbackRow: {
    marginHorizontal: 16,
    marginTop: 20,
    padding: 16,
    backgroundColor: '#18181B',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#27272A',
    alignItems: 'center',
    gap: 12,
  },
  feedbackLabel: { color: '#A1A1AA', fontSize: 14, fontWeight: '600' },
  voteBtns: { flexDirection: 'row', gap: 12 },
  voteBtn: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: '#27272A',
  },
  voteBtnActive: { backgroundColor: '#7C3AED' },
  voteText: { color: '#ffffff', fontWeight: '700', fontSize: 14 },
  error: { color: '#EF4444', textAlign: 'center', fontSize: 16, fontWeight: '600' },
});
