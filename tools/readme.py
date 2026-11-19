#!/usr/bin/env python3
"""Lab 5: README.md-г results/newman-*.txt болон collection-оос үүсгэнэ (тоо үргэлж таарна).
   python3 tools/readme.py
"""
import json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def rd(p):
    p = os.path.join(ROOT, p)
    return ANSI.sub("", open(p, encoding="utf-8", errors="replace").read()) if os.path.exists(p) else None


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip() or "?"


def stats(t):
    if not t:
        return None
    d = {}
    for k in ("iterations", "requests", "test-scripts", "assertions"):
        m = re.search(rf"[│|]\s*{k}\s*[│|]\s*(\d+)\s*[│|]\s*(\d+)\s*[│|]", t)
        if m:
            d[k] = (int(m.group(1)), int(m.group(2)))
    m = re.findall(r"^exit=(\d+)", t, re.M)
    d["exit"] = int(m[-1]) if m else None
    d["econn"] = len(re.findall(r"ECONNREFUSED", t))
    d["fails"] = re.findall(r"^\s*\d+\.\s+(AssertionError|Error|SyntaxError)\s+(.+?)\s*$", t, re.M)
    d["fail_detail"] = re.findall(r"^\s+(expected .+?)\s*$", t, re.M)
    return d


P, F, D, X, U = (stats(rd(f"results/{n}")) for n in
                 ("newman-pass.txt", "newman-fail.txt", "newman-down.txt", "newman-defects.txt", "newman-public.txt"))
col = json.load(open(os.path.join(ROOT, "lab05-collection.json"), encoding="utf-8"))
specs = col["item"]

L = []
a = L.append
a("# Лаб 5: API системийн тест — Postman ба Newman\n")
a("**Нэр:** М. Батдорж  \n**Оюутны код:** B252270136\n")
a("```\n$ node -v\n" + sh("node -v") + "\n$ newman -v\n" + sh("newman -v") + "\n```\n")
a("| Файл | Агуулга |\n|---|---|")
a("| `server.js` | Багшийн өгсөн бүртгэлийн API (өөрчлөөгүй) |")
a(f"| `lab05-collection.json` | Үндсэн collection: {len(specs)} бие даасан тест (спецификаци) |")
a("| `lab05-collection-fail.json` | S01-ийн oracle-ыг зориуд 201 → 200 болгосон хувилбар |")
a("| `lab05-defects.json` | Олдсон согогуудыг ЗӨВ гэж үзэж буй хүлээгдэх үр дүнгээр шалгах collection (нэмэлт) |")
a("| `lab05-public-api.json` | Даалгавар 5: jsonplaceholder /users (нэмэлт) |")
a("| `results/newman-*.txt` | Newman-ы бүтэн текст гаралт + төгсгөлд `exit=` мөр |")
a("| `tools/readme.py` | Энэ README-г results/-аас үүсгэдэг скрипт (тоо файлтай заавал таарна) |\n")

# ---- Task 2: design
a("## Даалгавар 2: Тест дизайн (Лекц 5-ын 5 алхам)\n")
a("**1. Бие даан тестлэгдэх функц:** `POST /registrations` — оюутныг хичээлд бүртгэх. PUT endpoint-ууд нь зөвхөн setup (Initialization).\n")
a("**2–3. Сонголтууд ба төлөөлөх утгууд (эквивалент ангиуд):**\n")
a("| Сонголт | Эквивалент анги → төлөөлөх утга |\n|---|---|")
a("| studentID-гийн хүчинтэй байдал | **идэвхтэй** (`status:\"active\"`, эсвэл status орхисон) · **идэвхгүй** (`\"inactive\"`) · **байхгүй** (PUT хийгээгүй ID, ж: `B00-NOT-EXIST`) · **талбар дутуу/хоосон** (→ 400) |")
a("| Оюутны үзсэн хичээлүүд (coursesTaken) | **урьдачийг бүгд агуулсан** (`[\"CS201\"]`) · **хоосон** (`[]`) · **зарим нь** (`[\"CS201\"]` vs урьдач `[CS201, CS202]`) |")
a("| courseID-гийн хүчинтэй байдал | **байгаа** (PUT хийсэн) · **байхгүй** (`CS999-NOT-EXIST`) · **талбар дутуу** (→ 400) |")
a("| Хичээлийн урьдач нөхцөл (prerequisites) | **байхгүй** (`[]`) · **нэг** (`[\"CS201\"]`) · **олон** (`[\"CS201\",\"CS202\"]`) |")
a("| Хүсэлтийн формат | **зөв JSON** · **буруу JSON** (→ 400 ERROR_BAD_JSON) |\n")
a("**Боломжгүй хослолууд (тестлэх шаардлагагүй гэж хассан):** байхгүй оюутан + \"урьдач хангасан/хангаагүй\" (байхгүй оюутанд coursesTaken гэж байхгүй); "
  "байхгүй хичээл + \"урьдач бүгд/зарим нь\" (байхгүй хичээлд урьдач байхгүй); урьдачгүй хичээл + \"урьдач дутуу\" (дутах зүйл байхгүй); "
  "талбар дутуу (400) + аливаа бизнес дүрэм (сервер талбар шалгаад шууд буцаана).\n")
a("**4–5. Спецификаци → бодит тест кейс** (лекцийн стратеги: happy path 1, алдааны анги бүрд 1, давхар алдаа, хязгаар):\n")
a("| ID | Ангилал | studentID / status / coursesTaken | courseID / prerequisites | Хүлээгдэх статус | Хүлээгдэх result |")
a("|---|---|---|---|---|---|")
rows = [
    ("S01", "Happy path", "B231234567 / active / [CS201]", "CS313 / [CS201]", "201", "OK (+ registrationID тоо)"),
    ("S02", "Алдааны анги", "байхгүй (B00-NOT-EXIST)", "CS313-S02 / []", "200", "ERROR_NO_STUDENT"),
    ("S03", "Алдааны анги", "B23-S03 / inactive / [CS201]", "CS313-S03 / [CS201]", "200", "ERROR_INACTIVE_STUDENT"),
    ("S04", "Алдааны анги", "B23-S04 / active / [CS201]", "байхгүй (CS999-NOT-EXIST)", "200", "ERROR_NO_COURSE"),
    ("S05", "Алдааны анги + хязгаар (хоосон coursesTaken)", "B23-S05 / active / []", "CS313-S05 / [CS201]", "200", "ERROR_PREREQUISITES, missing [CS201]"),
    ("S06", "Урьдачийн зарим нь", "B23-S06 / active / [CS201]", "CS313-S06 / [CS201, CS202]", "200", "ERROR_PREREQUISITES, missing [CS202]"),
    ("S07", "Давхар алдаа", "B23-S07 / inactive / []", "байхгүй", "200", "ERROR_INACTIVE_STUDENT"),
    ("S08", "Давхар алдаа", "байхгүй", "байхгүй", "200", "ERROR_NO_STUDENT"),
    ("S09", "Давхар алдаа", "B23-S09 / inactive / []", "CS313-S09 / [CS201]", "200", "ERROR_INACTIVE_STUDENT"),
    ("S10", "Хязгаар: урьдачгүй хичээл", "B23-S10 / active / []", "CS101-S10 / []", "201", "OK"),
    ("S11", "Хязгаар: status орхисон", "B23-S11 / (орхисон→active) / [CS201]", "CS313-S11 / [CS201]", "201", "OK"),
    ("S12", "Хязгаар: талбар дутуу", "B23-S12", "(courseID байхгүй)", "400", "ERROR_BAD_REQUEST"),
    ("S13", "Хязгаар: буруу JSON", "`{\"studentID\": \"B23-S13\", \"courseID\": ` (тасархай)", "—", "400", "ERROR_BAD_JSON"),
    ("S14", "Давтан бүртгэл", "B23-S14 / active / [] (2 удаа)", "CS101-S14 / []", "201, 201", "OK, OK (спецификацид заагаагүй)"),
]
for r in rows:
    a("| " + " | ".join(r) + " |")
a("\n**Давхар алдааны дүгнэлт (S07–S09):** зааварт аль алдаа түрүүлж буцахыг бичээгүй тул тестээр тогтоов — сервер **оюутныг (байгаа эсэх → идэвхтэй эсэх) хичээлээс өмнө**, хичээлийн байгаа эсэхийг урьдачаас өмнө шалгадаг.\n")

# ---- Task 3
a("## Даалгавар 3: Collection\n")
a(f"`lab05-collection.json` — {len(specs)} тест тус бүр **бие даасан**: өөрийн оюутан/хичээлийг өвөрмөц ID-аар (`B23-S05`, `CS313-S05` …) PUT-ээр өөрөө бэлддэг тул дараалал болон бусад тестээс хамаарахгүй, давтан ажиллуулахад ч PASS. "
  "Oracle бүр **статус + result** хоёуланг шалгана; ERROR_PREREQUISITES-д `missing` массивыг, 201-д `registrationID` нь **тоо** эсэхийг (яг утгыг биш — сервер in-memory тул хуримтлагддаг) шалгана. Setup PUT бүрт `200` oracle бий. `{{baseUrl}}` = `http://localhost:3000` collection variable.\n")

# ---- Task 4
a("## Даалгавар 4: Newman\n")


def row(name, st, fn):
    if not st:
        return f"| {name} | — | — | — | — | `results/{fn}` алга |"
    r, s = st.get("requests", (0, 0)), st.get("assertions", (0, 0))
    return f"| {name} | {r[0]} / {r[1]} | {s[0]} / {s[1]} | {st.get('econn', 0)} | **{st.get('exit')}** | `results/{fn}` |"


a("| Ажиллуулалт | requests executed / failed | assertions executed / failed | ECONNREFUSED мөр | exit code | Файл |")
a("|---|---|---|---|---|---|")
a(row("PASS — `lab05-collection.json`", P, "newman-pass.txt"))
a(row("FAIL — `lab05-collection-fail.json`", F, "newman-fail.txt"))
a(row("DOWN — сервер унтраастай", D, "newman-down.txt"))
if X:
    a(row("Согог — `lab05-defects.json` (нэмэлт)", X, "newman-defects.txt"))
if U:
    a(row("Нийтийн API — `lab05-public-api.json` (нэмэлт)", U, "newman-public.txt"))
a("")
if P:
    a(f"**Тестийн тоо:** {len(specs)} тест (спецификаци), {P['requests'][0]} хүсэлт, **{P['assertions'][0]} assertion executed** (`results/newman-pass.txt`), failed {P['assertions'][1]}, exit code {P['exit']}.\n")
if F:
    det = F["fail_detail"][0] if F["fail_detail"] else ""
    a(f"**FAIL:** зөвхөн S01-ийн статусын oracle-ыг 200 гэж зориуд буруу болгосон → assertions failed {F['assertions'][1]} (`{det}`), exit code **{F['exit']}**. "
      "CI quality gate яг энэ тэг биш exit code-оор pipeline-ийг зогсооно. Үндсэн collection зөв хэвээр.\n")
if D:
    a(f"**DOWN:** сервер унтраастай үед {D['requests'][0]} хүсэлт бүгд `connect ECONNREFUSED 127.0.0.1:3000` алдаатай ({D['econn']} мөр), exit code **{D['exit']}**. "
      "Энэ бол **интерфейсийн алдаа** — хүсэлт серверт хүрээгүй тул хариу огт ирээгүй; харин **oracle-ийн алдаа** нь сервер хариулсан ч хариуны агуулга хүлээгдэж буйгаас зөрөхийг хэлнэ (FAIL ажиллуулалт шиг). "
      "DOWN үед assertion-ууд fail болсон нь функц буруу ажилласныг биш, холболт байхгүйг харуулна.\n")

# ---- Defects
a("## Олдсон согогууд\n")
a("Тест дизайны явцад (сонголт бүрийн \"сонирхолтой\" утгыг туршихад) дараах согог олдсон. Үндсэн collection-ийг ногоон байлгах үүднээс тэдгээрийг тусдаа `lab05-defects.json`-д **зөв гэж үзэж буй хүлээгдэх үр дүнгээр** бичсэн (тиймээс FAIL болдог):\n")
a("1. **`courseID: \"toString\"` серверийг унагадаг (DoS).** `courses` нь энгийн JS объект тул `courses[\"toString\"]` нь `Object.prototype.toString` функцийг буцаана → `course.prerequisites` undefined → `.filter` дээр `TypeError` → барьж аваагүй exception Node процессыг зогсооно. "
  "Дараагийн бүх хүсэлт ECONNREFUSED. `constructor`, `valueOf`, `hasOwnProperty` зэрэг нэр ч мөн адил.")
a("2. **`studentID: \"toString\"` / `\"__proto__\"` (байхгүй оюутан) → `ERROR_NO_STUDENT` биш `ERROR_INACTIVE_STUDENT` буцаана** — ижил шалтгаан (prototype-ийн гишүүнийг оюутан гэж үзэж, `status` undefined ≠ \"active\").")
a("3. **Давтан бүртгэл хориглогдоогүй** (S14): ижил оюутан ижил хичээлд дахин 201 авна. Спецификацид заагаагүй тул согог гэхээсээ асуулт гэж тэмдэглэв.\n")
a("**Засах санал:** `students`/`courses`-ийг `Map` эсвэл `Object.create(null)` болгох, эсвэл `Object.hasOwn(courses, courseID)`-ээр шалгах.\n")
if X:
    a(f"`results/newman-defects.txt`: assertions failed {X['assertions'][1]} / {X['assertions'][0]}, requests failed {X['requests'][1]} (`socket hang up` → дараа нь ECONNREFUSED), exit {X['exit']}.\n")

if U:
    a("## Даалгавар 5: Нийтийн API\n")
    a(f"`GET https://jsonplaceholder.typicode.com/users` — 3 oracle (статус 200, массив эсэх, эхний хэрэглэгч \"Leanne Graham\"): assertions {U['assertions'][0]} / failed {U['assertions'][1]}. "
      "GET-only тул setup хэрэггүй, тест бичихэд хялбар; харин өгөгдлийг бид удирддаггүй тул oracle (жишээ нь нэр) нь гуравдагч этгээд өгөгдлөө өөрчилбөл бидний кодгүйгээр унах эрсдэлтэй.\n")

a("## Дүгнэлт\n")
a("<!-- conclusion -->")
na = P["assertions"][0] if P else "?"
a(f"Дизайны 5 алхмаас хамгийн их бодол шаардсан нь 2–3 дахь алхам буюу сонголтуудыг тодорхойлж, эквивалент анги болгон хуваах байсан: \"оюутан\" гэдэг нэг сонголт мэт боловч байгаа эсэх, идэвхтэй эсэх, үзсэн хичээл гэсэн гурван бие даасан хэмжээс болж задарсан. "
  "Боломжгүй хослолуудыг (байхгүй оюутан + урьдач хангасан, байхгүй хичээл + урьдач дутуу, урьдачгүй хичээл + урьдач дутуу, талбар дутуу + бизнес дүрэм) хассанаар бүх хослолын оронд 14 утга учиртай спецификацид хүрсэн. "
  "Зааварт давхар алдааны дарааллыг заагаагүй байсныг S07–S09 тестээр тогтоосон: сервер оюутныг хичээлээс өмнө шалгадаг. "
  f"Collection-ийн {len(specs)} тест тус бүр өөрийн өвөрмөц ID-тай setup-аа хийдэг тул бие даасан бөгөөд давтан ажиллуулахад ч {na} assertion бүгд PASS байсан; registrationID-ийн яг утгын оронд тоо эсэхийг шалгасан нь in-memory серверийн хуримтлалд тэсвэртэй болгосон. "
  "Зориуд буруу oracle-той FAIL collection exit code 1 буцааж, CI quality gate хэрхэн ажилладгийг харуулсан бол сервер унтраастай DOWN ажиллуулалт ECONNREFUSED-ээр интерфейсийн алдаа ба oracle-ийн алдааны ялгааг тод харуулсан. "
  "Хамгийн чухал үр дүн нь тестүүд жинхэнэ согог олсон явдал: `courseID: \"toString\"` илгээхэд сервер бүхэлдээ унадаг (DoS), `studentID: \"toString\"` нь байхгүй оюутныг идэвхгүй гэж буруу ангилдаг. "
  "Энэ хоёр согогийг \"хүчинтэй/хүчингүй ID\" ангийн дотор JavaScript-ийн онцлогтой холбоотой онцгой утгыг санаатайгаар туршсаны дүнд олсон нь эквивалент ангийг зөвхөн бизнесийн утгаар бус, хэрэгжүүлэлтийн технологийн эрсдэлээр ч бодох хэрэгтэйг харуулсан. "
  "Мөн давтан бүртгэлийг сервер хориглодоггүйг S14 илрүүлсэн ч спецификацид заагаагүй тул үүнийг шаардлагын асуулт гэж тэмдэглэв.")
a("<!-- /conclusion -->\n")
a("## AI ашиглалт\n")
a("<!-- ai -->")
a("Claude (Anthropic-ийн AI туслах)-ыг дараах зүйлд ашигласан: сонголт/эквивалент ангийн хүснэгт ба 14 спецификацийн ноорог, Postman v2.1 collection-уудыг (pass, fail, defects, public) скриптээр үүсгэх, server.js-ийн онцгой утгуудыг туршиж `toString` согогуудыг илрүүлэх, README үүсгэх `tools/readme.py`, дүгнэлтийн ноорог. "
  "Newman-ы бүх ажиллуулалтыг (pass, fail, down, defects) өөрийн Ubuntu машин дээр зөвхөн localhost:3000 руу өөрөө хийж, бүтэн гаралтыг results/-д хадгалсан. README-ийн бүх тоо results/ файлуудаас скриптээр уншигдсан тул файлтай таарч байгаа.")
a("<!-- /ai -->\n")

open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("README.md үүслээ:", f"{len(specs)} тест,", f"assertions={P['assertions'] if P else '?'}", f"pass exit={P['exit'] if P else '?'}",
      f"fail exit={F['exit'] if F else '?'}", f"down exit={D['exit'] if D else '?'}")
