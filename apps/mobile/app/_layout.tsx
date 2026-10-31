/**
 * Root layout — Expo Router Stack navigation.
 * Handles tab group and modal / detail screens.
 */
import { Stack } from 'expo-router';
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { usePushNotifications } from '../hooks/usePushNotifications';

export default function RootLayout() {
  // Ask for notification permission once at startup and register the device
  // token with the backend, so "push notifications" is a working feature and
  // not just a listed dependency.
  usePushNotifications();

  return (
    <>
      <StatusBar style="light" backgroundColor="#0A0A0A" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: '#0A0A0A' },
          headerTintColor: '#F5F5F5',
          headerTitleStyle: { fontWeight: '700' },
          contentStyle: { backgroundColor: '#0A0A0A' },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="meme/[id]"
          options={{
            presentation: 'card',
            headerShown: false,
          }}
        />
      </Stack>
    </>
  );
}
