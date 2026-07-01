(function () {
  var APP_ID = "q9gmpcfb";
  var w = window;
  w.intercomSettings = Object.assign({}, w.intercomSettings || {}, {
    app_id: APP_ID,
    hide_default_launcher: true
  });
  var ic = w.Intercom;

  if (typeof ic === "function") {
    ic("reattach_activator");
    ic("update", w.intercomSettings);
    return;
  }

  var d = document;
  var i = function () {
    i.c(arguments);
  };
  i.q = [];
  i.c = function (args) {
    i.q.push(args);
  };
  w.Intercom = i;
  w.AlteIntercom = w.AlteIntercom || {
    open: function () {
      if (typeof w.Intercom === "function") {
        w.Intercom("show");
      }
    },
    hide: function () {
      if (typeof w.Intercom === "function") {
        w.Intercom("hide");
      }
    }
  };

  function loadIntercom() {
    var s = d.createElement("script");
    s.type = "text/javascript";
    s.async = true;
    s.src = "https://widget.intercom.io/widget/" + APP_ID;
    var x = d.getElementsByTagName("script")[0];
    x.parentNode.insertBefore(s, x);
  }

  if (d.readyState === "complete") {
    loadIntercom();
  } else if (w.attachEvent) {
    w.attachEvent("onload", loadIntercom);
  } else {
    w.addEventListener("load", loadIntercom, false);
  }
}());
