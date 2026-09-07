/**
 * Push Notification Hook for MemeGPT Mobile
 * Handles notification permissions and registration token retrieval.
 */

import { useState, useEffect } from "react";
import { Platform } from "react-native";

export interface PushNotificationState {
  expoPushToken: string | null;
  notification: any | null;
  error: Error | null;
}

export function usePushNotifications(): PushNotificationState {
  const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
  const [notification, setNotification] = useState<any | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function registerForPushNotifications() {
      try {
        let Notifications: any = null;
        let Device: any = null;

        try {
          Notifications = require("expo-notifications");
          Device = require("expo-device");
        } catch {
          // Native modules not available (e.g. standard browser preview)
          return;
        }

        if (!Device || !Device.isDevice) {
          return;
        }

        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== "granted") {
          const { status } = await Notifications.requestPermissionsAsync();
          finalStatus = status;
        }

        if (finalStatus !== "granted") {
          return;
        }

        const tokenData = await Notifications.getExpoPushTokenAsync();
        if (isMounted) {
          setExpoPushToken(tokenData.data);
        }

        if (Platform.OS === "android") {
          Notifications.setNotificationChannelAsync("default", {
            name: "default",
            importance: Notifications.AndroidImportance.MAX,
            vibrationPattern: [0, 250, 250, 250],
            lightColor: "#7C3AED",
          });
        }

        const subscription = Notifications.addNotificationReceivedListener((notif: any) => {
          if (isMounted) {
            setNotification(notif);
          }
        });

        return () => subscription.remove();
      } catch (err: any) {
        if (isMounted) {
          setError(err);
        }
      }
    }

    registerForPushNotifications();

    return () => {
      isMounted = false;
    };
  }, []);

  return { expoPushToken, notification, error };
}
