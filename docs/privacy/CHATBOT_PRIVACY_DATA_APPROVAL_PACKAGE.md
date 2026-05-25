# Chatbot Privacy/Data Approval Package

PRIVACY_DATA_APPROVAL_STATUS=PENDING_REVIEW

## KA — კონფიდენციალურობა და მონაცემები

### რა მონაცემები შეიძლება შეგროვდეს

- სახელი
- ტელეფონი
- ელფოსტა
- ქვეყანა/ქალაქი საერთაშორისო მიღების კონტექსტში
- საინტერესო პროგრამა
- ჩათის შეტყობინებები
- source domain (`alte.edu.ge` ან `join.alte.edu.ge`)
- ენა
- consent status

### რატომ გროვდება მონაცემები

- სტუდენტის კითხვებზე პასუხის გასაცემად
- მისაღები კონსულტაციისთვის
- სწორი დეპარტამენტის/ოპერატორისკენ გადასამისამართებლად
- CRM lead-ის შესაქმნელად მხოლოდ მაშინ, როცა მომხმარებელი საკონტაქტო მონაცემებს დატოვებს

### რა არ გროვდება default რეჟიმში

- საბანკო/საგადახდო ბარათის მონაცემები
- პასპორტის სკანები
- პირადობის ან სხვა ID დოკუმენტები
- სენსიტიური სამედიცინო მონაცემები
- პაროლები

### Lead-ის შექმნის წესი

- საკონტაქტო მონაცემების გარეშე: არ იქმნება lead/customer.
- ტელეფონის ან ელფოსტის დატოვებისას: შესაძლებელია CRM profile/task/lead-ის შექმნა ბიზნეს წესების მიხედვით.
- frontend არ ქმნის CRM ჩანაწერებს; გადაწყვეტილებას იღებს backend.

### სენსიტიური პასუხების წესი

თუ ოფიციალური წყარო არ არსებობს, content არის `review_required`, confidence დაბალია ან თემა სენსიტიურია, ჩათბოტი პასუხობს კონსერვატიულად და მომხმარებელს შესაბამის დეპარტამენტთან/ოპერატორთან გადაამისამართებს.

### მონაცემების შენახვა

- Google Cloud SQL, region: `europe-west1`
- audit logs და conversation history

### მომხმარებლის უფლებები

- მონაცემების წაშლის მოთხოვნა
- მონაცემების export მოთხოვნა
- მონაცემების შესწორების მოთხოვნა

### Privacy Policy URL

PENDING_OFFICIAL_URL

## EN — Privacy And Data

### Data That May Be Collected

- name
- phone
- email
- country/city in international admissions context
- interested program
- chat messages
- source domain (`alte.edu.ge` or `join.alte.edu.ge`)
- language
- consent status

### Why Data Is Collected

- to answer student questions
- to provide admissions consultation
- to route the student to the correct department/operator
- to create a CRM lead only after contact details are provided

### What Is Not Collected By Default

- payment card data
- passport scans
- ID documents
- sensitive medical data
- passwords

### Lead Creation Rule

- no contact details: no lead/customer is created
- phone or email provided: CRM profile/task/lead may be created according to business rules
- the frontend never creates CRM records; the backend decides

### Sensitive Answer Rule

If an official source is missing, content is `review_required`, confidence is low, or the topic is sensitive, the chatbot must answer conservatively and route the student to the correct department/operator.

### Data Storage

- Google Cloud SQL, region: `europe-west1`
- audit logs and conversation history

### User Rights

- delete request
- data export request
- correction request

### Privacy Policy URL

PENDING_OFFICIAL_URL
