# Alte AI Chatbot Knowledge Base - Reviewer Instructions

## მიზანი

ეს პაკეტი საჭიროა იმისთვის, რომ ადამიანის reviewer-მა ოფიციალურად გადაწყვიტოს, რომელი Knowledge Base ჩანაწერი შეიძლება გამოიყენოს chatbot-მა საჯარო პასუხებში.

საჯარო გაშვებამდე ეს review აუცილებელია, რადგან Knowledge Base შეიცავს სენსიტიურ თემებს: სწავლის საფასური, ვადები, ჩარიცხვის საბუთები, Medicine/MD, International Admissions, visa/relocation და ოფიციალური წესები.

## შესავსები ფაილი

შეავსეთ:

```text
docs/reviewer_package/alte_kb_human_review_decisions.csv
```

Reviewer ავსებს მხოლოდ ამ სვეტებს:

- `decision`
- `reviewer`
- `review_date`
- `reviewer_notes`

არ შეცვალოთ `source_key`, `source_url`, `content_preview` და სხვა წყაროს სვეტები, თუ ამის აუცილებლობა არ არის.

## დაშვებული გადაწყვეტილებები

- `APPROVE` - შეიძლება საჯაროდ პასუხი
- `REWRITE` - ტექსტი გადასაწერია
- `ARCHIVE` - არ გამოიყენოს ბოტმა
- `HANDOVER_ONLY` - ბოტმა პირდაპირ არ უპასუხოს, ადამიანთან გადაამისამართოს
- `NEEDS_OFFICIAL_SOURCE` - საჭიროა ოფიციალური დადასტურება

## კატეგორიების წესი

- Tuition / fees / prices: approve მხოლოდ მაშინ, თუ არსებობს მოქმედი ოფიციალური finance source.
- Deadlines: approve მხოლოდ მოქმედი official deadline/admissions source-ით.
- Required documents: approve მხოლოდ official admissions source-ით.
- Medicine / MD: approve მხოლოდ official program/admissions source-ით.
- International admissions: approve მხოლოდ official international admissions source-ით.
- Visa / relocation / legal: ჩვეულებრივ `HANDOVER_ONLY`, თუ ოფიციალური ტექსტი არ არსებობს.
- Contact / about / general FAQ: შეიძლება `APPROVE`, თუ official source სწორია და მიმდინარეა.

თუ დარწმუნებული არ ხართ, აირჩიეთ:

```text
NEEDS_OFFICIAL_SOURCE
```

## შემდეგი ნაბიჯი

CSV-ის შევსების შემდეგ შემდეგი ფაზაა:

```text
Apply Reviewer Decisions
```

ამ ეტაპზე გადაწყვეტილებები არ არის ავტომატურად შევსებული და public launch არ არის დასრულებული.
