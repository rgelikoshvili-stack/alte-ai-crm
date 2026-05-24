// Production config example for join.alte.edu.ge.
// This file documents the config only. It does not initialize the widget by itself.
// Use the object below inside the embed snippet before loading alte-chat-widget.js.

export const joinProductionWidgetConfig = {
  apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
  sourceDomain: "join.alte.edu.ge",
  defaultLanguage: "en",
  proactiveEnabled: true,
  proactiveDelayMs: 30000,
};

// If approved for an admission landing page, proactiveDelayMs may be changed to 5000.
