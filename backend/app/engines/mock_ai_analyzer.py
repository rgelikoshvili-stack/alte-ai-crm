import re

from app.schemas.chat import AIAnalysisResult, ExtractedContact

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?:\+995)?\d{9}")


def analyze_message(message: str, source_domain: str | None = None) -> AIAnalysisResult:
    text = message.strip()
    lowered = text.lower()
    contact = extract_contact(text)
    language = detect_language(text)
    intent = detect_intent(lowered)
    medical_track = "medicine" in lowered or "md" in lowered or "სამედიცინო" in lowered

    missing_fields = missing_contact_fields(contact)
    should_create_lead = intent in {"admission_interest", "consultation_request", "international_admission"}
    should_handover = intent in {"human_request", "finance_question"}
    priority = "normal"
    department = None
    risk_flags: list[str] = []
    used_sources: list[str] = []
    interest_area = None
    program = detect_program(text)

    if intent == "general_info":
        reply = "ალტე უნივერსიტეტის საკონტაქტო ინფორმაციისთვის შეგიძლიათ გამოიყენოთ ოფიციალური საკონტაქტო არხები. ზუსტ ინფორმაციას ოპერატორიც დაგიდასტურებთ."
        should_create_lead = False
        used_sources = ["mock_contact_source"]
    elif intent == "finance_question":
        reply = "სწავლის საფასურსა და დაფინანსებას ზუსტად ფინანსური/მიღების კონსულტანტი დაგიდასტურებთ. შეგიძლიათ დატოვოთ საკონტაქტო ინფორმაცია?"
        risk_flags = ["finance_details_require_human_verification"]
        department = "Finance"
    elif intent == "human_request":
        reply = "გადაგამისამართებთ ადამიანთან. გთხოვთ მომწეროთ სახელი და ტელეფონი ან ელფოსტა."
    elif intent == "student_service":
        reply = "ეს სტუდენტური სერვისების საკითხია. თუ გსურთ, დაგაკავშირებთ შესაბამის გუნდთან."
        department = "Student Services"
        should_create_lead = False
    elif intent == "international_admission":
        reply = "International Admissions დაგეხმარებათ. გთხოვთ მოგვწეროთ სახელი, ქვეყანა/ქალაქი და ტელეფონი ან ელფოსტა."
        priority = "high"
        department = "International Admissions"
        interest_area = "International admission"
        if medical_track:
            program = program or "Medicine / 6-year MD"
    elif intent in {"admission_interest", "consultation_request"}:
        reply = "მიღების კონსულტაციისთვის გთხოვთ მომწეროთ სახელი და ტელეფონი ან ელფოსტა."
        department = "Admissions"
        interest_area = "Admissions"
    elif intent == "technical_issue":
        reply = "ტექნიკურ საკითხზე დაგეხმარებათ მხარდაჭერის გუნდი. გთხოვთ აღწეროთ პრობლემა და დატოვოთ საკონტაქტო ინფორმაცია."
        department = "IT Support"
        should_create_lead = False
        should_handover = True
    elif intent == "event_interest":
        reply = "ღონისძიების შესახებ ინფორმაციას დაგიზუსტებთ. თუ გსურთ, დატოვეთ საკონტაქტო ინფორმაცია."
        interest_area = "Event"
    else:
        reply = "გმადლობთ შეტყობინებისთვის. შემიძლია დაგეხმაროთ პროგრამებზე, მიღებაზე, დაფინანსებაზე ან კონტაქტზე."

    if source_domain == "join.alte.edu.ge":
        priority = "high"
        if intent in {"admission_interest", "consultation_request", "general_info"}:
            intent = "international_admission"
            department = "International Admissions"
            interest_area = "International admission"

    if should_create_lead and not has_minimum_contact(contact):
        should_create_lead = False

    return AIAnalysisResult(
        reply=reply,
        language=language,
        intent=intent,
        confidence=0.88 if intent != "unknown" else 0.5,
        should_create_lead=should_create_lead,
        should_handover=should_handover,
        department=department,
        priority=priority,
        missing_fields=missing_fields,
        extracted_contact=contact,
        interest_area=interest_area,
        program=program,
        program_language=language if language != "unknown" else None,
        source_domain=source_domain,
        conversation_summary=f"User intent: {intent}. Message: {text[:180]}",
        used_sources=used_sources,
        risk_flags=risk_flags,
    )


def detect_language(text: str) -> str:
    return "ka" if re.search(r"[\u10A0-\u10FF]", text) else "en"


def detect_intent(lowered: str) -> str:
    if contains_any(lowered, ["ადამიან", "ოპერატორ", "კონსულტანტ", "დამირეკეთ", "დამალაპარაკეთ", "call me"]):
        return "human_request"
    if contains_any(lowered, ["international", "medicine", "from india", "visa", "relocation"]):
        return "international_admission"
    if contains_any(lowered, ["ფასი", "ღირს", "გადასახადი", "დაფინანსება", "სტიპენდია", "tuition", "fee"]):
        return "finance_question"
    if contains_any(lowered, ["ბიბლიოთეკ", "სტუდენტ", "საგამოცდო", "ცხრილი"]):
        return "student_service"
    if contains_any(lowered, ["ტექნიკური", "ვერ შევდივარ", "login", "password"]):
        return "technical_issue"
    if contains_any(lowered, ["ღონისძიება", "open day", "event"]):
        return "event_interest"
    if contains_any(
        lowered,
        [
            "ჩარიცხვა",
            "მიღება",
            "პროგრამა",
            "ბაკალავრ",
            "მაგისტრ",
            "მაინტერესებს",
            "apply",
            "application",
            "admission",
            "requirements",
            "program information",
        ],
    ):
        return "admission_interest"
    if contains_any(lowered, ["სად ხართ", "სად მდებარეობს", "მისამართი", "ტელეფონი", "კონტაქტი", "contact"]):
        return "general_info"
    return "general_info"


def extract_contact(text: str) -> ExtractedContact:
    compact_text = text.replace(" ", "")
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(compact_text)
    first_name = None
    last_name = None
    parts = [part.strip() for part in text.split(",")]
    if len(parts) >= 2:
        name_parts = parts[0].split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[1]
    if not first_name:
        name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)", text)
        if name_match:
            first_name = name_match.group(1)
            last_name = name_match.group(2)
    if not first_name and re.search(r"[\u10A0-\u10FF]", text):
        name_match = re.search(r"([\u10A0-\u10FF]{2,})\s+([\u10A0-\u10FF]{2,})", text)
        if name_match and not any(word in name_match.group(0) for word in ["სად მდებარეობს", "მაინტერესებს"]):
            first_name = name_match.group(1)
            last_name = name_match.group(2)
    country = None
    city = None
    lowered = text.lower()
    if "india" in lowered:
        country = "India"
    if "tbilisi" in lowered or "თბილისი" in lowered:
        city = "Tbilisi"
    return ExtractedContact(
        first_name=first_name,
        last_name=last_name,
        phone=phone_match.group(0) if phone_match else None,
        email=email_match.group(0) if email_match else None,
        country=country,
        city=city,
    )


def detect_program(text: str) -> str | None:
    lowered = text.lower()
    if "ბიზნეს" in lowered or "business" in lowered:
        return "Business"
    if "medicine" in lowered or "md" in lowered or "სამედიცინო" in lowered:
        return "Medicine / 6-year MD"
    if "law" in lowered or "სამართ" in lowered:
        return "Law"
    if "computer science" in lowered or "it" in lowered or "კომპიუტერულ" in lowered:
        return "IT / Computer Science"
    if "mba" in lowered:
        return "MBA"
    if "bachelor" in lowered or "ბაკალავრ" in lowered:
        return "Bachelor"
    if "master" in lowered or "მაგისტრ" in lowered:
        return "Master"
    return None


def missing_contact_fields(contact: ExtractedContact) -> list[str]:
    missing = []
    if not contact.first_name:
        missing.append("first_name")
    if not (contact.phone or contact.email):
        missing.append("phone_or_email")
    return missing


def has_minimum_contact(contact: ExtractedContact) -> bool:
    return bool(contact.phone or contact.email)


def contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)
