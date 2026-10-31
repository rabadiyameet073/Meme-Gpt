import { useCallback, useEffect, useRef, useState } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import { api } from '../lib/api';

try {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  });
} catch {
  // Graceful fallback for non-native test environments
}

export function usePushNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string>('');
  const [registered, setRegistered] = useState(false);
  const notificationListener = useRef<Notifications.Subscription | any>();


  useEffect(() => {
    registerForPushNotifications().then(async (token) => {
      if (!token) return;
      setExpoPushToken(token);

      // Persist the token on the backend — without this the device is unreachable
      // and push notifications are a feature that exists only on paper.
      try {
        await api.registerPushToken(
          token,
          Platform.OS === 'ios' ? 'ios' : Platform.OS === 'web' ? 'web' : 'android',
          Constants.expoConfig?.version,
        );
        setRegistered(true);
      } catch (err) {
        console.warn('Could not register push token with MemeGPT:', err);
      }
    });

    try {
      notificationListener.current = Notifications.addNotificationReceivedListener((notification) => {
        console.log('Notification received:', notification);
      });
    } catch {}

    return () => {
      if (notificationListener.current && notificationListener.current.remove) {
        notificationListener.current.remove();
      }
    };
  }, []);

  /** Deactivate this device (user disabled notifications, or signed out). */
  const unregister = useCallback(async () => {
    if (!expoPushToken) return;
    try {
      await api.unregisterPushToken(expoPushToken);
    } catch (err) {
      console.warn('Could not unregister push token:', err);
    } finally {
      setRegistered(false);
    }
  }, [expoPushToken]);

  return { expoPushToken, registered, unregister };
}

async function registerForPushNotifications(): Promise<string | null> {
  try {
    if (!Device.isDevice) {
      console.log('Push notifications only work on physical devices');
      return null;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') return null;

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'MemeGPT',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
      });
    }

    const tokenData = await Notifications.getExpoPushTokenAsync({
      // EAS project id is required by expo-notifications >= 0.28. It comes from
      // app.json (set by `eas init`) or the EXPO_PUBLIC_EAS_PROJECT_ID env var.
      projectId: resolveProjectId(),
    });
    return tokenData.data;
  } catch (err) {
    console.warn('Could not register for push notifications:', err);
    return null;
  }
}

function resolveProjectId(): string | undefined {
  const fromConfig =
    (Constants.expoConfig?.extra as { eas?: { projectId?: string } } | undefined)?.eas?.projectId ??
    (Constants as unknown as { easConfig?: { projectId?: string } }).easConfig?.projectId;
  const projectId = fromConfig || process.env.EXPO_PUBLIC_EAS_PROJECT_ID;
  if (!projectId) {
    console.warn(
      'No EAS projectId found — run `eas init` or set EXPO_PUBLIC_EAS_PROJECT_ID to obtain a push token.',
    );
  }
  return projectId || undefined;
}
