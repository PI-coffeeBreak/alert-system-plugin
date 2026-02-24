import React, { useEffect, useState } from "react";
import { getApi, useWebSocket } from "coffeebreak/event-app";

function Alert() {
  const [alerts, setAlerts] = useState([]);
  const {
    subscribe,
    unsubscribe,
    addMessageHandler,
    removeMessageHandler,
    isConnected,
  } = useWebSocket();

  const handleAlertMessage = (message) => {
    setAlerts((prev) => {
      const newAlerts = [message.data, ...prev];
      return newAlerts.slice(0, 3);
    });
  };

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const { data } = await getApi().get(`/alert-system-plugin/alert/high-priority/`);
        setAlerts(data);
      } catch (error) {
        console.error("Error fetching alerts:", error.response?.data || error.message);
      }
    };

    if (isConnected) {
      console.log("Subscribing to high-priority-alerts");

      subscribe("high-priority-alerts")
        .then(() => {
          console.log("Successfully subscribed to high-priority-alerts");
          addMessageHandler("high-priority-alerts", handleAlertMessage);
          fetchAlerts();
        })
        .catch((error) => {
          console.error("Failed to subscribe to high-priority-alerts:", error);
        });
    }

    return () => {
      console.log("Unsubscribing from high-priority-alerts");
      removeMessageHandler("high-priority-alerts", handleAlertMessage);

      unsubscribe("high-priority-alerts")
        .then(() => {
          console.log("Successfully unsubscribed from high-priority-alerts");
        })
        .catch((error) => {
          console.error("Failed to unsubscribe from high-priority-alerts:", error);
        });
    };
  }, [isConnected, subscribe, unsubscribe, addMessageHandler, removeMessageHandler]);

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col w-15/16 mx-auto gap-3 my-4">
      {alerts.map((alert) => (
        <div key={alert.id} className="px-4 py-1 bg-warning text-warning-content rounded-xl">
          <div className="font-medium">{alert.message}</div>
          <div className="text-xs opacity-75">{new Date(alert.created_at).toLocaleTimeString()}</div>
        </div>
      ))}
    </div>
  );
}

export default Alert;
