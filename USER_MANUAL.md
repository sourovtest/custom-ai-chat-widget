# Bongora Chatbot ব্যবহার নির্দেশিকা

এই নির্দেশিকা Bongora chatbot-এর ক্রেতা, বিক্রেতা এবং administrator—সবার জন্য।

## ১. ক্রেতা/বিক্রেতা হিসেবে চ্যাট ব্যবহার

1. Bongora ওয়েবসাইটের নিচের কোণায় থাকা **“সাহায্য লাগবে?”** বোতামে ক্লিক করুন।
2. বার্তার ঘরে প্রশ্ন লিখে **বার্তা পাঠান** চাপুন। Enter-ও কাজ করতে পারে।
3. দ্রুত শুরু করতে **অর্ডার ট্র্যাকিং** বা **পণ্য সম্পর্কে** বোতাম বেছে নিতে পারেন।
4. চ্যাট বন্ধ করতে উপরের **X** বোতামে বা কিবোর্ডের `Escape` চাপুন।
5. আগের সেশন একই ব্রাউজারে ফিরিয়ে আনতে পারবেন; সেশন আইডি browser-এর `localStorage`-এ থাকে।

### কী ধরনের প্রশ্ন করবেন

- পণ্য খোঁজা বা পণ্যের বৈশিষ্ট্য
- অর্ডার ট্র্যাকিং—প্রয়োজনে অর্ডার নম্বর দিন
- রিটার্ন/রিফান্ডের পরবর্তী ধাপ
- বিক্রেতা অ্যাকাউন্ট বা সাধারণ সহায়তা

চ্যাটে পাসওয়ার্ড, API key, card তথ্য বা অপ্রয়োজনীয় ব্যক্তিগত তথ্য দেবেন না। দাম, স্টক, ডেলিভারি বা অর্ডারের অবস্থা যাচাই করা না গেলে chatbot সেটি নিশ্চিত তথ্য হিসেবে বলার কথা নয়; প্রয়োজন হলে support team-এর সাহায্য নিন।

### সংযোগ না হলে

- `এখন সংযোগ পাওয়া যাচ্ছে না` দেখালে কিছুক্ষণ পরে আবার চেষ্টা করুন।
- ইন্টারনেট সংযোগ পরীক্ষা করুন।
- বার্তা পাঠাতে ব্যর্থ হলে লেখা বার্তাটি input-এ থেকে যাওয়ার কথা; সংযোগ ফিরে এলে আবার **বার্তা পাঠান** চাপুন।
- বারবার ব্যর্থ হলে administrator-কে API health, server log এবং database connection পরীক্ষা করতে বলুন।

## ২. Local development-এ চালু করা

PowerShell-এ project folder থেকে:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

তারপর browser-এ:

- Widget preview: `http://127.0.0.1:4173/index.html`
- API health: `http://127.0.0.1:8000/health`

Preview server আলাদাভাবে না চললে project root থেকে চালান:

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

Health response-এ `"status":"ok"` এবং `"database":"ok"` থাকলে API ও database প্রস্তুত। `"ai_provider":"gemini"` থাকলে Gemini সক্রিয়; provider অনুপলব্ধ হলে নিরাপদ fallback উত্তর আসতে পারে।

Environment file-এ API key বা database password আছে—সেটি কাউকে পাঠাবেন না, commit করবেন না, screenshot-এও দেখাবেন না।

## ৩. Administrator হিসেবে rules পরিচালনা

Admin panel খুলে **Administrator key** দিন। সঠিক key গ্রহণ হলে rule list, Active/Inactive সংখ্যা এবং **New rule** দেখা যাবে। Key-টি administrator-এর কাছ থেকে আলাদা নিরাপদ মাধ্যমে নিন; chat বা public document-এ লিখবেন না।

### নতুন rule তৈরি

1. **New rule** চাপুন।
2. Rule name দিন।
3. Trigger event বেছে নিন:
   - **On first visit** — visitor-এর প্রথম page visit-এ।
   - **URL match** — URL path-এ নির্দিষ্ট লেখা থাকলে।
   - **Time on page** — নির্দিষ্ট সময় পর।
4. Action type বেছে নিন:
   - **Static Message** — নির্দিষ্ট লেখা দেখায়।
   - **AI Persona** — নির্বাচিত assistant role ব্যবহার করে।
5. প্রয়োজনমতো message, assigned role, trigger config, priority এবং execution frequency দিন।
6. Active রাখলে rule সংরক্ষণের পর widget-এ চালু হবে। Inactive রাখলে সংরক্ষিত থাকবে, কিন্তু visitor-এর কাছে চলবে না।
7. **Save rule** চাপুন।

### Trigger config উদাহরণ

Trigger config ঘরে JSON object দিতে হয়:

URL path-এ `product` থাকলে:

```json
{"url_match":"product"}
```

URL path-এ `cart` থাকলে:

```json
{"url_match":"cart"}
```

Page খোলার ৫ সেকেন্ড পর:

```json
{"delay_seconds":5}
```

JSON ভুল হলে rule save হবে না। URL match শুধু page path-এর অংশ খোঁজে।

### Action, priority ও frequency

- **Static Message:** Static message ঘরে visitor-কে দেখানোর লেখা লিখুন।
- **AI Persona:** Assigned role থেকে Sales Assistant, Customer Support, Vendor Assistant, FAQ Assistant অথবা Custom AI Persona বেছে নিন।
- **Priority:** কম সংখ্যা আগে বিবেচিত হয়।
- **Once per session:** একই visitor session-এ rule পুনরায় চালায় না।
- **Once:** একবার চালানোর জন্য।
- **Always:** প্রতিবার trigger মিললে চালানোর জন্য।
- Rule পরিবর্তন করতে **Edit**, সরাতে **Delete** চাপুন। Delete নিশ্চিত করতে prompt এলে যাচাই করে সিদ্ধান্ত নিন।

API-তে administrator authentication না থাকলে Admin panel rules পরিবর্তন করতে পারবে না। Access denied বা server error হলে key এবং backend availability administrator-এর মাধ্যমে যাচাই করুন।

## ৪. Administrator-এর নিরাপত্তা ও পরিচালনা

- `backend/.env`-এর `GEMINI_API_KEY`, `ADMIN_API_KEY`, এবং database credentials গোপন রাখুন।
- `.env` file source control-এ commit করবেন না।
- Production-এ MySQL `root` account ব্যবহার করবেন না; সীমিত অনুমতিসম্পন্ন database user তৈরি করুন।
- Production-এ widget ও API দুটোই HTTPS-এ চালান এবং `CORS_ALLOWED_ORIGINS`-এ কেবল অনুমোদিত website origin রাখুন।
- API key বা Admin key প্রকাশ পেলে সংশ্লিষ্ট provider/পরিবেশে key revoke বা rotate করে backend restart করুন।
- নিয়মিত database backup নিন এবং backup থেকে restore পরীক্ষা করুন।
- Production-এ deploy করার আগে staging site-এ chat, admin rules, CORS, HTTPS এবং mobile view পরীক্ষা করুন।

## ৫. সাধারণ সমস্যা সমাধান

| সমস্যা | কী পরীক্ষা করবেন |
|---|---|
| Widget offline দেখায় | `/health`, backend process, database এবং browser network |
| Admin key প্রত্যাখ্যাত | সঠিক `ADMIN_API_KEY` এবং backend restart হয়েছে কি না |
| Gemini reply না আসে | Provider key, quota, configured model এবং server log; fallback reply আসতে পারে |
| Rule চালু হয় না | Rule Active কি না, trigger event/config ঠিক কি না, URL path মিলছে কি না |
| Session ফিরে আসে না | একই browser/profile ব্যবহার হচ্ছে কি না এবং browser storage অনুমোদিত কি না |
| Browser-এ CORS error | API environment-এর allowed origin-এ page-এর exact origin আছে কি না |

## আরও তথ্য

- Developer/API setup: [README.md](./README.md)
- Website integration: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- Current project status: [PROJECT_PROGRESS.md](./PROJECT_PROGRESS.md)
