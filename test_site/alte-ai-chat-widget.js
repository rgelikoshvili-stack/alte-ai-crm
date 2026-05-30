(function () {
  "use strict";

  var config = window.AlteChatWidgetConfig || {};
  var assetBase = config.assetBaseUrl || "https://alte.edu.ge/assets";
  var widgetUrl = config.widgetHtmlUrl || assetBase.replace(/\/$/, "") + "/alte-ai-chat-widget.html";
  var containerId = config.containerId || "alte-ai-chat-widget-container";
  var requiredBackendEndpoints = ["/chat/session/start", "/chat/message"];
  var sessionStartPayloadFields = ["source_domain", "language", "channel", "widget_variant"];
  var messagePayloadFields = ["selected_department", "selected_topic", "message", "question", "note", "wait_for_operator", "reset", "expand", "fullscreen", "close", "operator", "handover", "source card renderer", "keyboard Enter handling", "Alte AI Assistant", "Alte AI ასისტენტი", "KA", "EN"];

  function publicConfigScript() {
    var publicConfig = {
      apiBaseUrl: config.apiBaseUrl || "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
      sourceDomain: config.sourceDomain || "alte.edu.ge",
      defaultLanguage: config.defaultLanguage || "ka",
      widgetVariant: config.widgetVariant || "pro_v2_safe",
      mode: config.mode || "test_site"
    };
    return "<script>window.AlteChatWidgetConfig=" + JSON.stringify(publicConfig).replace(/</g, "\\u003c") + ";<\/script>";
  }

  function createContainer() {
    var existing = document.getElementById(containerId);
    var container = existing || document.createElement("div");
    container.id = containerId;
    container.setAttribute("data-alte-widget-variant", config.widgetVariant || "pro_v2_safe");
    container.style.width = config.containerWidth || "100%";
    container.style.maxWidth = "100vw";
    container.style.overflowX = "hidden";
    if (!existing) {
      document.body.appendChild(container);
    }
    return container;
  }

  function loadWidget() {
    var container = createContainer();
    var iframe = document.createElement("iframe");
    iframe.title = "Alte AI Chatbot";
    iframe.loading = "lazy";
    iframe.style.display = "block";
    iframe.style.width = config.width || "100%";
    iframe.style.maxWidth = "100vw";
    iframe.style.height = config.height || "100vh";
    iframe.style.border = "0";
    iframe.style.background = "transparent";
    container.innerHTML = "";
    container.appendChild(iframe);

    fetch(widgetUrl, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.text();
      })
      .then(function (html) {
        iframe.srcdoc = html.replace("<head>", "<head>" + publicConfigScript());
      })
      .catch(function () {
        iframe.src = widgetUrl;
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadWidget);
  } else {
    loadWidget();
  }
})();
