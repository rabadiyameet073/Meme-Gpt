/**
 * Root layout — Expo Router with tab navigation.
 * Dark mode, status bar, fonts as per design spec.
 */
import { Tabs } from 'expo-router';
import React from 'react';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" backgroundColor="#0A0A0A" />
      <Tabs
        screenOptions={{
          headerStyle: { backgroundColor: '#0A0A0A' },
          headerTintColor: '#F5F5F5',
          headerTitleStyle: { fontWeight: '700' },
          tabBarStyle: {
            backgroundColor: '#141414',
            borderTopColor: '#2a2a2a',
            paddingBottom: 4,
          },
          tabBarActiveTintColor: '#7C3AED',
          tabBarInactiveTintColor: '#525252',
          tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        }}
      >
        <Tabs.Screen
          name="(tabs)/index"
          options={{
            title: 'Search',
            tabBarLabel: 'Search',
            tabBarIcon: ({ color }) => (
              <TabIcon emoji="🔍" color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="(tabs)/trending"
          options={{
            title: 'Trending',
            tabBarLabel: 'Trending',
            tabBarIcon: ({ color }) => (
              <TabIcon emoji="🔥" color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="(tabs)/library"
          options={{
            title: 'Library',
            tabBarLabel: 'Library',
            tabBarIcon: ({ color }) => (
              <TabIcon emoji="📚" color={color} />
            ),
          }}
        />
      </Tabs>
    </>
  );
}

function TabIcon({ emoji, color }: { emoji: string; color: string }) {
  const { Text } = require('react-native');
  return <Text style={{ fontSize: 20, opacity: color === '#7C3AED' ? 1 : 0.5 }}>{emoji}</Text>;
}
