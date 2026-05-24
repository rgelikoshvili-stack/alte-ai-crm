const messages = document.querySelector("#messages");
const quickReplies = document.querySelector("#quickReplies");
const composer = document.querySelector("#composer");
const input = document.querySelector("#messageInput");
const widget = document.querySelector("#chatWidget");
const launcher = document.querySelector("#chatLauncher");
const closeChat = document.querySelector("#closeChat");
const languageToggle = document.querySelector("#languageToggle");

let lang = "ka";
let leadDraft = { program: "", name: "", phone: "", email: "" };

const sources = {
  law: "https://alte.edu.ge/ka/samartlis",
  admission: "https://alte.edu.ge/ka/migheba",
  bachelors: "https://alte.edu.ge/ka/sabakalavro-programebi",
  contact: "https://alte.edu.ge/ka/kontaqti",
  international: "https://alte.edu.ge/ka/saertashoriso-studentebistvis"
};

const copy = {
  ka: {
    hello:
      "გამარჯობა, მე ვარ Alte Assistant. შემიძლია გიპასუხო პროგრამებზე, მიღებაზე, დაფინანსებაზე და საჭირო შემთხვევაში კონსულტანტს დაგაკავშირო.",
    placeholder: "მკითხე პროგრამაზე, მიღებაზე ან დაფინანსებაზე...",
    send: "გაგზავნა",
    quick: ["პროგრამები", "სამართალი", "მიღება", "დაფინანსება", "საერთაშორისო სტუდენტი", "ადამიანთან საუბარი"],
    leadAsk:
      "კონსულტაციისთვის მომწერე სახელი და ტელეფონი ან ელ-ფოსტა. მაგ: ნინო, +995599000000, nino@email.com",
    handover:
      "კარგი, გადავცემ ოპერატორს. მოგვწერე სახელი და საკონტაქტო ნომერი, რომ გუნდმა დაგიკავშირდეს.",
    leadCreated: "CRM-ში შეიქმნებოდა lead და დავალება Admissions გუნდისთვის.",
    fallback:
      "ამაზე ზუსტი პასუხისთვის ოფიციალური წყარო მჭირდება. შემიძლია კონსულტანტს გადავცე კითხვა."
  },
  en: {
    hello:
      "Hi, I am Alte Assistant. I can help with programs, admissions, funding, and connect you with a consultant when needed.",
    placeholder: "Ask about programs, admissions, or funding...",
    send: "Send",
    quick: ["Programs", "Law", "Admission", "Funding", "International student", "Talk to human"],
    leadAsk:
      "For a consultation, please share your name and phone or email. Example: Nino, +995599000000, nino@email.com",
    handover:
      "Sure, I will route this to an operator. Please share your name and contact number.",
    leadCreated: "A CRM lead and Admissions follow-up task would be created.",
    fallback:
      "I need an official source for an exact answer. I can hand this over to a consultant."
  }
};

function addMessage(role, html) {
  const item = document.createElement("div");
  item.className = `message ${role}`;
  item.innerHTML = html;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function sourceLabel(url) {
  return `<div class="source">წყარო: ${url}</div>`;
}

function renderQuickReplies() {
  quickReplies.innerHTML = "";
  copy[lang].quick.forEach((label) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;
    btn.addEventListener("click", () => handleUser(label));
    quickReplies.appendChild(btn);
  });
}

function extractContact(text) {
  const phone = text.match(/(\+?995)?\s?5\d{2}\s?\d{2}\s?\d{2}\s?\d{2}/);
  const email = text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  const name = text
    .replace(phone?.[0] || "", "")
    .replace(email?.[0] || "", "")
    .replace(/[,+]/g, " ")
    .trim();
  return {
    phone: phone?.[0] || "",
    email: email?.[0] || "",
    name: name.length > 1 ? name : ""
  };
}

function answerFor(text) {
  const q = text.toLowerCase();
  const wantsHuman = /(ადამიან|ოპერატორ|კონსულტანტ|human|operator|consultant)/i.test(text);
  const hasContact = /@|\+?995\s?5\d{2}|5\d{8}/i.test(text);

  if (hasContact) {
    const contact = extractContact(text);
    leadDraft = { ...leadDraft, ...contact };
    return `
      ${copy[lang].leadCreated}
      <div class="lead-card">
        <strong>Lead preview</strong>
        პროგრამა: ${leadDraft.program || "Admission interest"}<br>
        სახელი: ${leadDraft.name || "დასაზუსტებელია"}<br>
        ტელეფონი: ${leadDraft.phone || "დასაზუსტებელია"}<br>
        ელ-ფოსტა: ${leadDraft.email || "დასაზუსტებელია"}<br>
        Stage: New Lead
      </div>`;
  }

  if (wantsHuman) {
    return copy[lang].handover;
  }

  if (/(სამართალ|law)/i.test(text)) {
    leadDraft.program = "სამართალი";
    return `
      სამართლის საბაკალავრო პროგრამა არის 240 კრედიტიანი, 4 წლიანი პროგრამა. სწავლების ენა არის ქართული.
      პროგრამა მოიცავს სამართლის სავალდებულო და არჩევით კურსებს, ინგლისური ენის კომპონენტს და თავისუფალ არჩევით კურსებს.
      ${sourceLabel(sources.law)}
      <br>${copy[lang].leadAsk}`;
  }

  if (/(პროგრამ|program|სწავლა|ბაკალავრ|მაგისტრ)/i.test(text)) {
    return `
      Alte-ს პროგრამები იყოფა საბაკალავრო, სამაგისტრო და ერთსაფეხურიან სამედიცინო პროგრამებად.
      შემიძლია დაგეხმარო კონკრეტული მიმართულებით: სამართალი, ბიზნესი, კომპიუტერული მეცნიერება, AI და მონაცემთა ანალიტიკა, მედიცინა, ტურიზმი, ჟურნალისტიკა.
      ${sourceLabel(sources.bachelors)}`;
  }

  if (/(მიღებ|ჩარიცხვ|admission|apply|application)/i.test(text)) {
    return `
      მიღების ბილიკი იყოფა ბაკალავრებისთვის, მაგისტრებისთვის და საერთაშორისო სტუდენტებისთვის.
      თუ ჩარიცხვა გაინტერესებს, მომწერე სასურველი პროგრამა და საკონტაქტო მონაცემი.
      ${sourceLabel(sources.admission)}
      <br>${copy[lang].leadAsk}`;
  }

  if (/(საერთაშორისო|international|visa|უცხო)/i.test(text)) {
    leadDraft.program = "International admissions";
    return `
      საერთაშორისო სტუდენტების კითხვა უნდა გადავიდეს International Admissions მიმართულებაზე.
      შეგვიძლია დავაზუსტოთ ქვეყანა, პროგრამა და საკონტაქტო მონაცემები.
      ${sourceLabel(sources.international)}
      <br>${copy[lang].leadAsk}`;
  }

  if (/(დაფინანს|გრანტ|ფას|tuition|funding|scholarship|price)/i.test(text)) {
    return `
      დაფინანსებასა და საფასურზე ბოტმა უნდა უპასუხოს მხოლოდ ოფიციალური active source-ით.
      თუ კონკრეტული პროგრამის საფასური გჭირდება, მითხარი პროგრამის სახელი და საჭიროების შემთხვევაში კონსულტანტს გადავცემ.
      ${sourceLabel(sources.admission)}`;
  }

  if (/(კონტაქტ|მისამართ|ტელეფონ|contact|address|phone)/i.test(text)) {
    return `
      საკონტაქტო ინფორმაციისთვის ბოტმა უნდა გამოიყენოს Alte-ს კონტაქტის გვერდი და CRM-ში lead არ შექმნას, თუ მომხმარებელი კონსულტაციას არ ითხოვს.
      ${sourceLabel(sources.contact)}`;
  }

  return copy[lang].fallback;
}

function handleUser(text) {
  addMessage("user", text);
  window.setTimeout(() => addMessage("bot", answerFor(text)), 220);
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  handleUser(text);
});

closeChat.addEventListener("click", () => {
  widget.classList.remove("is-open");
  launcher.classList.add("is-visible");
});

launcher.addEventListener("click", () => {
  widget.classList.add("is-open");
  launcher.classList.remove("is-visible");
});

languageToggle.addEventListener("click", () => {
  lang = lang === "ka" ? "en" : "ka";
  languageToggle.textContent = lang === "ka" ? "EN" : "KA";
  input.placeholder = copy[lang].placeholder;
  composer.querySelector("button").textContent = copy[lang].send;
  renderQuickReplies();
  addMessage("bot", copy[lang].hello);
});

renderQuickReplies();
input.placeholder = copy[lang].placeholder;
composer.querySelector("button").textContent = copy[lang].send;
addMessage("bot", copy[lang].hello);
