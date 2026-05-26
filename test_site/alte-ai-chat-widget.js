(function () {
  "use strict";

  var config = window.AlteChatWidgetConfig || {};
  var assetBase = config.assetBaseUrl || "https://alte.edu.ge/assets";
  var widgetUrl = config.widgetHtmlUrl || assetBase.replace(/\/$/, "") + "/alte-ai-chat-widget.html";
  var containerId = config.containerId || "alte-ai-chat-widget-container";
  var requiredBackendEndpoints = ["/chat/session/start", "/chat/message"];
  var sessionStartPayloadFields = ["source_domain", "language", "channel", "widget_variant"];

  function publicConfigScript() {
    var publicConfig = {
      apiBaseUrl: config.apiBaseUrl || "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
      sourceDomain: config.sourceDomain || "alte.edu.ge",
      defaultLanguage: config.defaultLanguage || "ka",
      widgetVariant: config.widgetVariant || "safe_pro_sidebar"
    };
    return "<script>window.AlteChatWidgetConfig=" + JSON.stringify(publicConfig).replace(/</g, "\\u003c") + ";<\/script>";
  }

  function createContainer() {
    var existing = document.getElementById(containerId);
    var container = existing || document.createElement("div");
    container.id = containerId;
    container.setAttribute("data-alte-widget-variant", config.widgetVariant || "safe_pro_sidebar");
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
    iframe.style.width = config.width || "min(760px, 100%)";
    iframe.style.height = config.height || "640px";
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
