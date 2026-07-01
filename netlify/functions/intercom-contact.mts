const INTERCOM_API_BASE = "https://api.intercom.io";
const INTERCOM_VERSION = "2.14";

type ContactPayload = {
  name?: unknown;
  phone?: unknown;
  email?: unknown;
  language?: unknown;
  topic?: unknown;
  message?: unknown;
};

const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
};

function jsonResponse(body: Record<string, unknown>, status = 200) {
  return Response.json(body, {
    status,
    headers: jsonHeaders,
  });
}

function textValue(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function buildIntercomMessage(payload: ContactPayload) {
  const name = textValue(payload.name);
  const phone = textValue(payload.phone);
  const email = textValue(payload.email);
  const language = textValue(payload.language);
  const topic = textValue(payload.topic);
  const message = textValue(payload.message);

  return {
    name,
    phone,
    email,
    language,
    topic,
    message,
    body: [
      "ახალი საკონტაქტო მოთხოვნა:",
      `სახელი: ${name}`,
      `ტელეფონი: ${phone}`,
      `ენა: ${language}`,
      `ელფოსტა: ${email}`,
      `ინტერესი/თემა: ${topic}`,
      `შეტყობინება: ${message}`,
    ].join("\n"),
  };
}

async function intercomFetch(path: string, token: string, init: RequestInit) {
  return fetch(`${INTERCOM_API_BASE}${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${token}`,
      accept: "application/json",
      "content-type": "application/json",
      "intercom-version": INTERCOM_VERSION,
      ...(init.headers || {}),
    },
  });
}

async function createIntercomContact(token: string, payload: ReturnType<typeof buildIntercomMessage>) {
  const body: Record<string, unknown> = {
    role: "lead",
    name: payload.name || undefined,
    phone: payload.phone || undefined,
    custom_attributes: {
      language: payload.language,
      topic: payload.topic,
      contact_message: payload.message,
      source: "alte_contact_form",
    },
  };

  if (payload.email) {
    body.email = payload.email;
  }

  const response = await intercomFetch("/contacts", token, {
    method: "POST",
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(`Intercom contact creation failed (${response.status}): ${JSON.stringify(data)}`);
  }

  const contactId = typeof data.id === "string" ? data.id : "";
  if (!contactId) {
    throw new Error("Intercom contact creation did not return a contact id.");
  }

  return contactId;
}

async function createIntercomConversation(token: string, contactId: string, body: string) {
  const response = await intercomFetch("/conversations", token, {
    method: "POST",
    body: JSON.stringify({
      from: {
        type: "lead",
        id: contactId,
      },
      body,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(`Intercom conversation creation failed (${response.status}): ${JSON.stringify(data)}`);
  }

  return data;
}

export default async function handler(req: Request) {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "POST, OPTIONS",
        "access-control-allow-headers": "content-type",
      },
    });
  }

  if (req.method !== "POST") {
    return jsonResponse({ ok: false, error: "Method not allowed. Use POST." }, 405);
  }

  const token = process.env.INTERCOM_ACCESS_TOKEN;
  if (!token) {
    return jsonResponse({ ok: false, error: "INTERCOM_ACCESS_TOKEN is not configured." }, 500);
  }

  let payload: ContactPayload;
  try {
    payload = await req.json();
  } catch {
    return jsonResponse({ ok: false, error: "Invalid JSON payload." }, 400);
  }

  const formatted = buildIntercomMessage(payload);

  try {
    const contactId = await createIntercomContact(token, formatted);
    const conversation = await createIntercomConversation(token, contactId, formatted.body);

    return jsonResponse({
      ok: true,
      intercom_conversation_id: typeof conversation.id === "string" ? conversation.id : null,
    });
  } catch (error) {
    console.error(error);
    return jsonResponse({ ok: false, error: "Failed to send contact request to Intercom." }, 502);
  }
}
