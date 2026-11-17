# -*- coding: utf-8 -*-
# בארבור · בניית האתר: קורא את content/site.json וכותב את קובצי ה-HTML לשורש המאגר.
# הרצה: python3 tools/build.py
import html, pathlib
import json, datetime
H = pathlib.Path(__file__).resolve().parent.parent          # שורש המאגר: לשם נכתבים קובצי האתר
S = json.loads((H / 'content' / 'site.json').read_text(encoding='utf-8'))
BADGE = {'culture':(239,162),'dance':(233,169),'music':(222,139),'pool':(187,166),
         'sport':(196,148),'swim':(240,156),'tots':(213,151),'youth':(222,161)}
CONTACT = S['contact']
DEPTS = S['depts']
D = {d['k']: d for d in DEPTS}
HERO = [(h['media'], h['caption'], h['dept']) for h in S['hero']]
TODAY = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).strftime('%Y-%m-%d')
WEEK = sorted([w for w in S['week'] if w.get('date_iso', '9999') >= TODAY], key=lambda w: w.get('date_iso', ''))[:4]
HOURS = {k: (v['title'], [(r['days'], r['time']) for r in v['rows']]) for k, v in S['hours'].items()}
MEMBERS = S['members']
META = S['meta']
MDESC = S.get('media_desc', {})   # חלופה טקסטואלית לסרטונים (ת"י 5568, 1.2.1), לא נראית על המסך
def e(s): return html.escape(s, quote=True)
def ltr(s): return f'<span class="ltr">{e(s)}</span>'
C = CONTACT

PP = ('<button class="pp" type="button" aria-label="עצירת התנועה">'
      '<svg class="i-pause" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.5" height="12" fill="currentColor"/><rect x="9.5" y="2" width="3.5" height="12" fill="currentColor"/></svg>'
      '<svg class="i-play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2l10 6-10 6z" fill="currentColor"/></svg></button>')

def m(spec, first=False):
    kind, src = spec.split(':', 1)
    src, _, pos = src.partition('@')
    st = f' style="object-position:{pos}"' if pos else ''
    if kind == 'v':
        desc = f'<p class="vh">{e(MDESC[src])}</p>' if MDESC.get(src) else ''
        return (f'<video class="m"{st} muted playsinline preload="{"auto" if first else "none"}" poster="m/{src}.jpg" aria-hidden="true">'
                f'<source src="m/{src}.mp4" type="video/mp4"></video>{desc}')
    lazy = '' if first else ' loading="lazy"'
    return f'<img class="m"{st} src="m/{src}.jpg" alt=""{lazy} decoding="async">'

def frame(specs):
    return '<div class="frame">' + ''.join(m(s, k == 0) for k, s in enumerate(specs)) + PP + '</div>'

NAV = [('index.html#week','השבוע'),('index.html#depts','המחלקות'),('index.html#members','מנוי'),('index.html#hours','שעות'),('#contact','צור קשר')]
def header():
    navh = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    navh += f'<li><a class="tel" href="tel:{C["tel_i"]}">{ltr(C["tel"])}</a></li>'
    return f'''<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html"><img src="logo/main.png" alt="קאנטרי קהילתי בארבור: ספורט, חוגים, קהילה. לדף הבית" width="360" height="360"></a>
    <button class="menu" type="button" aria-expanded="false" aria-controls="nav">תפריט</button>
    <nav class="nav" id="nav" aria-label="ניווט ראשי"><ul>{navh}</ul></nav>
  </div>
</header>'''


def marquee():
    def items(hidden):
        ti = ' tabindex="-1"' if hidden else ''
        return ''.join(f'<li><a class="t-{d["k"]}" href="{d["k"]}.html"{ti}><i aria-hidden="true"></i>{e(d["name"])}</a></li>' for d in DEPTS)
    return f'''<section class="marq" aria-label="כל המחלקות של בארבור">
  <div class="marq-view"><div class="marq-track"><ul>{items(False)}</ul><ul aria-hidden="true">{items(True)}</ul></div></div>
  <button class="marq-pp" type="button" aria-label="עצירת הפס הנע"><svg class="i-pause" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.5" height="12" fill="currentColor"/><rect x="9.5" y="2" width="3.5" height="12" fill="currentColor"/></svg><svg class="i-play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2l10 6-10 6z" fill="currentColor"/></svg></button>
</section>'''

def tagcls(k): return f't-{k}'

def card(w):
    return f'''<li class="card"><a href="{e(w['href'])}">
  <div class="ph"><img src="m/{w['img']}.jpg" alt="" loading="lazy" decoding="async" width="400" height="300"></div>
  <div class="tx"><span class="tag {tagcls(w['tag'])}">{e(w['tagname'])}</span>
    <p class="when"><span class="d">{e(w['day'])} {e(w['date'])}</span><span class="t">{ltr(w['time'])}</span></p>
    <h3>{e(w['title'])}</h3>
    <p class="who">{e(w['who'])} · {e(w['where'])}</p>
  </div></a></li>'''

def week(items, title='השבוע בבארבור', sub='ומה שמחכה בשבועות הקרובים', sid='week', cls='week'):
    if not items:
        return ''
    return f'''<section class="{cls}" id="{sid}" aria-labelledby="{sid}-t">
  <div class="wrap">
    <div class="sec-head">
      <div><h2 id="{sid}-t">{e(title)}</h2><p>{e(sub)}</p></div>
      <a class="more" href="https://www.coing.co/TelAvivBarbur/events">כל האירועים <span aria-hidden="true">←</span></a>
    </div>
    <ul class="cards">{''.join(card(w) for w in items)}</ul>
  </div>
</section>'''

def dcard(d):
    src, _, pos = d['card'].partition('@')
    st = f' style="object-position:{pos}"' if pos else ''
    return f'''<li class="t-{d['k']}"><a href="{d['k']}.html">
  <div class="ph"><img src="m/{src}.jpg"{st} alt="" loading="lazy" decoding="async" width="600" height="400"></div>
  <div class="band"><h3>{e(d['name'])}</h3><p>{e(d['lead'])}</p></div></a></li>'''

def hours_dl(k):
    name, rows = HOURS[k]
    return f'<h3>{e(name)}</h3><dl>' + ''.join(f'<dt>{e(a)}</dt><dd>{ltr(b)}</dd>' for a, b in rows) + '</dl>'

def info():
    checks = ''.join(f'<li>{e(x)}</li>' for x in MEMBERS)
    return f'''<div class="info">
  <div class="wrap">
    <section id="members" aria-labelledby="m-t"><h2 id="m-t">מנויי הקאנטרי נהנים יותר</h2><ul class="checks">{checks}</ul>
      <p class="m-cta"><a class="btn" href="https://wa.me/{C['wa_i']}">שאלה על המנוי? בוואטסאפ <span aria-hidden="true">←</span></a></p></section>
    <section id="hours" class="hours" aria-labelledby="h-t"><h2 id="h-t">שעות פעילות</h2>{hours_dl('tots')}{hours_dl('youth')}{hours_dl('library')}</section>
    <section class="contact" aria-labelledby="c-t"><h2 id="c-t">איך מגיעים</h2>
      <p class="addr">{e(C['addr'])}</p>
      <ul>
        <li><a href="https://www.google.com/maps/search/?api=1&query=%D7%A7%D7%90%D7%A0%D7%98%D7%A8%D7%99%20%D7%A7%D7%94%D7%99%D7%9C%D7%AA%D7%99%20%D7%91%D7%90%D7%A8%D7%91%D7%95%D7%A8%2C%20%D7%93%D7%A8%D7%9A%20%D7%94%D7%94%D7%92%D7%A0%D7%94%20135%2C%20%D7%AA%D7%9C%20%D7%90%D7%91%D7%99%D7%91-%D7%99%D7%A4%D7%95">פתיחה במפות <span aria-hidden="true">←</span></a></li>
        <li>טלפון: <a href="tel:{C['tel_i']}">{ltr(C['tel'])}</a></li>
        <li>וואטסאפ: <a href="https://wa.me/{C['wa_i']}">{ltr(C['wa'])}</a></li>
      </ul>
    </section>
  </div>
</div>'''

def footer():
    dl = ''.join(f'<li><a href="{d["k"]}.html">{e(d["name"])}</a></li>' for d in DEPTS)
    return f'''<footer class="field foot" id="contact">
  <div class="wrap">
    <div class="cols">
      <div>
        <img src="logo/main.png" alt="" width="360" height="360" loading="lazy">
        <p>{e(C['addr'])}</p>
        <p>מנהל קהילה, תרבות וספורט, עיריית תל אביב-יפו</p>
      </div>
      <nav aria-labelledby="f-d"><h2 id="f-d">המחלקות</h2><ul class="dl">{dl}</ul></nav>
      <div><h2>יצירת קשר</h2>
        <ul>
          <li>טלפון: <a href="tel:{C['tel_i']}">{ltr(C['tel'])}</a></li>
          <li>וואטסאפ: <a href="https://wa.me/{C['wa_i']}">{ltr(C['wa'])}</a></li>
          <li><a href="mailto:{C['mail']}">{ltr(C['mail'])}</a></li>
          <li><a href="https://www.facebook.com/countrybarbur">פייסבוק</a> · <a href="https://instagram.com/barbur_community">אינסטגרם</a></li>
        </ul>
      </div>
    </div>
    <div class="base">
      <p>האתר נבנה לפי התקן הישראלי 5568 ברמה AA. <a href="accessibility.html">הצהרת נגישות</a>. צילומים: דין אהרוני רולנד, וסרטון התדמית של בארבור.</p>
      {'<p><span class="proto-note">אב טיפוס</span></p>' if META.get('prototype_label') else ''}
    </div>
  </div>
</footer>'''

def page(fn, title, body, desc=None, bcls="home"):
    doc = f'''<!DOCTYPE html>
<html lang="he" dir="rtl" class="look-b look-c">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'קאנטרי קהילתי בארבור, דרך ההגנה 135, תל אביב-יפו. ספורט, חוגים וקהילה בבית אחד.')}">
{'<meta name="robots" content="noindex">' if META.get('noindex') else ''}
<link rel="icon" href="data:,">
<link rel="preload" href="fonts/heebo-hebrew-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="site.css">
<script>try{{var l=new URLSearchParams(location.search).get("look");if(l)document.documentElement.classList.add("look-"+l)}}catch(e){{}}</script>
</head>
<body class="{bcls}">
<a class="skip" href="#main">דילוג לתוכן הראשי</a>
<a class="skip" href="accessibility.html">הצהרת נגישות</a>
<div class="field">
{header()}
</div>
<main id="main">
{body}
</main>
{footer()}
<script src="site.js"></script>
</body>
</html>
'''
    (H / fn).write_text(doc, encoding='utf-8')

# =========================== דף הבית ===========================
caps = ''.join(f'<a data-pn href="{k}.html"{"" if n == 0 else " hidden"}>{e(t)} <span aria-hidden="true">←</span></a>'
               for n, (_, t, k) in enumerate(HERO))
home = f'''<section class="field hero" aria-labelledby="h1">
  <div class="wrap">
    <h1 id="h1">{e(META['headline'])}</h1>
    <p class="sub"><span class="nw">{e(C['addr'])}</span><a href="tel:{C['tel_i']}">טלפון {ltr(C['tel'])}</a><a href="https://wa.me/{C['wa_i']}">וואטסאפ {ltr(C['wa'])}</a></p>
  </div>
</section>
<div class="heroband">
  <div class="wrap" data-rot="6500">
    <div class="big">{frame([h[0] for h in HERO])}<div class="caps">{caps}</div></div>
  </div>
</div>
{marquee()}
{week(WEEK)}
<section class="depts" id="depts" aria-labelledby="depts-t">
  <div class="wrap">
    <div class="sec-head"><h2 id="depts-t">המחלקות</h2></div>
    <ul class="grid">{''.join(dcard(d) for d in DEPTS)}</ul>
  </div>
</section>
{info()}'''
page('index.html', META['title'], home)

# =========================== עמודי המחלקות ===========================
for i, d in enumerate(DEPTS):
    k = d['k']
    side = ''
    if k in BADGE:
        w, h = BADGE[k]
        side += f'<img class="badge" src="logo/badge-{k}.svg" alt="{e(d["name"])}" width="{w}" height="{h}">'
    if d.get('go'):
        href, txt = d['go']
        ext = href.startswith('http')
        side += f'<a class="btn" href="{e(href)}">{e(txt)} <span aria-hidden="true">←</span></a>'
    if d.get('hours'):
        side += f'<div class="hours">{hours_dl(d["hours"]).replace("<h3>", "<h2>").replace("</h3>", "</h2>")}</div>'
    if d.get('hours_note'):
        side += f'<h2>שעות פתיחה</h2><p class="note">{e(d["hours_note"])}</p>'
    reach = ''
    if d.get('tel'):
        num, num_i, lab = d['tel']
        reach += f'<li>{e(lab)}: <a href="tel:{num_i}">{ltr(num)}</a></li>'
    reach += f'<li>מזכירות בארבור: <a href="tel:{C["tel_i"]}">{ltr(C["tel"])}</a></li>'
    reach += f'<li>וואטסאפ: <a href="https://wa.me/{C["wa_i"]}">{ltr(C["wa"])}</a></li>'
    side += f'<h2>יש שאלה?</h2><ul class="reach">{reach}</ul>'
    lis = ''.join(f'<li>{e(x)}</li>' for x in d['lst'])
    ev = [w for w in WEEK if w['tag'] == k]
    evs = week(ev, title=f'בקרוב ב{d["name"]}', sub='אירועים קרובים', sid='dweek', cls='week devents') if ev else ''
    others = [DEPTS[(i + j) % len(DEPTS)] for j in (1, 2, 3)]
    body = f'''<section class="field hero dhero" aria-labelledby="h1">
  <div class="wrap">
    <nav class="crumbs" aria-label="מיקום באתר"><a href="index.html">דף הבית</a><span aria-hidden="true">/</span><a href="index.html#depts">המחלקות</a></nav>
    <h1 id="h1">{e(d['name'])}</h1>
    <p class="lead">{e(d['lead'])}</p>
  </div>
</section>
<div class="heroband">
  <div class="wrap" data-rot="6000">
    <div class="big">{frame(d['media'])}</div>
  </div>
</div>
<div class="dbody t-{k}">
  <div class="wrap">
    <p class="say">{e(d['say'])}</p>
    <aside class="aside" aria-label="הרשמה ופרטים">{side}</aside>
    <section class="what" aria-labelledby="what-t"><h2 id="what-t">מה יש כאן</h2><ul>{lis}</ul></section>
  </div>
</div>
{evs}
<section class="more-d" aria-labelledby="more-t">
  <div class="wrap">
    <div class="sec-head"><h2 id="more-t">עוד בבארבור</h2><a class="more" href="index.html#depts">כל המחלקות <span aria-hidden="true">←</span></a></div>
    <ul class="grid">{''.join(dcard(o) for o in others)}</ul>
  </div>
</section>'''
    page(f'{k}.html', f'{d["name"]} · קאנטרי קהילתי בארבור', body, desc=f'{d["name"]} בקאנטרי קהילתי בארבור: {d["lead"]}', bcls=f'dept d-{k}')
print('ok')

# =========================== הצהרת נגישות ===========================
# לפי תקנה 35ה לתקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), התשע"ג-2013.
A = S.get('a11y', {})
if A:
    co = A['coordinator']
    stmt = f"""<section class="field hero a11y-hero" aria-labelledby="h1">
  <div class="wrap">
    <nav class="crumbs" aria-label="מיקום באתר"><a href="index.html">דף הבית</a><span aria-hidden="true">/</span><span class="here" aria-current="page">הצהרת נגישות</span></nav>
    <h1 id="h1">הצהרת נגישות</h1>
    <p class="lead">קאנטרי קהילתי בארבור פתוח לכל הקהילה, והאתר שלו צריך להיות פתוח לכולם באותה מידה. כאן מפורט מה עשינו כדי שהאתר יהיה נגיש, מה עדיין לא נגיש, ואיך פונים אלינו.</p>
  </div>
</section>
<div class="doc">
  <div class="wrap">
    <p class="upd">ההצהרה עודכנה בתאריך {e(A['updated'])}</p>

    <section aria-labelledby="s1"><h2 id="s1">רמת הנגישות של האתר</h2>
      <p>קאנטרי קהילתי בארבור הוא חלק ממנהל קהילה, תרבות וספורט בעיריית תל אביב-יפו. האתר הותאם לתקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), התשע"ג-2013, ולתקן הישראלי ת"י 5568 חלק 1, מהדורת ספטמבר 2023, ברמה AA, כפי שקובעת תקנה 35א.</p>
      <p>בנוסף לתקן הישראלי, בדקנו את האתר גם מול המהדורה 2.1 של הקווים המנחים הבינלאומיים, ברמה AA, כיעד נוסף:</p>
      <table class="terms"><caption class="vh">התקנים שהאתר נבדק מולם</caption>
        <thead><tr><th scope="col">מה</th><th scope="col">שם התקן</th><th scope="col">רמה</th></tr></thead>
        <tbody>
          <tr><td>התקן הישראלי, מחייב</td><td>ת"י 5568 חלק 1, ספטמבר 2023</td><td lang="en" dir="ltr">AA</td></tr>
          <tr><td>הקווים המנחים הבינלאומיים, יעד נוסף</td><td lang="en" dir="ltr">WCAG 2.1</td><td lang="en" dir="ltr">AA</td></tr>
        </tbody>
      </table>
    </section>

    <section aria-labelledby="s2"><h2 id="s2">מה עשינו באתר</h2>
      <h3>התאמה למשתמשי מקלדת</h3>
      <ul class="bul">
        <li>אפשר לגלוש בכל האתר עם מקלדת בלבד: מעבר בין רכיבים במקש Tab, חזרה ב־Shift ו־Tab, והפעלה ב־Enter. סדר המעבר תואם את סדר הקריאה.</li>
        <li>הרכיב שבמיקוד מסומן במסגרת ברורה, בצבע שבולט על הרקע שלו.</li>
        <li>בראש כל עמוד יש קישורי דילוג לתוכן הראשי ולהצהרת הנגישות. הם מופיעים כשמגיעים אליהם במקלדת.</li>
      </ul>
      <h3>התאמה לבעלי לקות ראייה</h3>
      <ul class="bul">
        <li>הצבעים נבחרו כך שיש ניגודיות מספקת בין הטקסט לרקע, גם מעל הצילומים והסרטונים.</li>
        <li>אפשר להגדיל את התצוגה עד פי 2 בתפריט הזום של הדפדפן (Ctrl ופלוס) בלי לאבד תוכן. האתר מתאים את עצמו גם למסך צר ברוחב 320 פיקסלים, בלי גלילה לצדדים.</li>
      </ul>
      <h3>התאמה למשתמשים בתוכנות קריאת מסך</h3>
      <ul class="bul">
        <li>לכל עמוד יש כותרת ראשית אחת וכותרות משנה מסודרות. אזורי העמוד (כותרת עליונה, ניווט, תוכן ותחתית) מסומנים, כדי שאפשר לנווט ביניהם.</li>
        <li>שפת האתר מוגדרת כעברית, וכיוון הכתיבה מימין לשמאל. מספרי טלפון מוצגים משמאל לימין, כדי שיוקראו נכון.</li>
        <li>לתמונות שמעבירות מידע יש טקסט חלופי. תמונות אווירה מסומנות כקישוטיות, והמידע שלידן מופיע בטקסט.</li>
        <li>הקישורים מנוסחים כך שברור לאן הם מובילים. קישורי הטלפון, הוואטסאפ והמייל ניתנים להפעלה ישירה.</li>
      </ul>
      <h3>תנועה וסרטונים</h3>
      <ul class="bul">
        <li>הסרטונים באתר הם סרטוני אווירה קצרים, ללא קול וללא דיבור. לכל סרטון יש תיאור טקסטואלי שתוכנות קריאת מסך מקריאות.</li>
        <li>הפתיחה המתחלפת ופס המחלקות הנע נעצרים בלחיצה על כפתור העצירה שלידם. שניהם נעצרים גם כשהמיקוד מהמקלדת נמצא בתוכם, כך שקישור שבמיקוד לא נעלם.</li>
        <li>מי שהגדיר במכשיר שלו "הפחתת תנועה" יראה את האתר בלי תנועה בכלל: בלי מעבר אוטומטי בין צילומים ובלי פס נע.</li>
      </ul>
    </section>

    <section aria-labelledby="s3"><h2 id="s3">איך בדקנו</h2>
      <p>{e(A.get('tested', ''))}</p>
      <table class="terms"><caption class="vh">סביבת הבדיקה</caption>
        <thead><tr><th scope="col">מה</th><th scope="col">פרטים</th></tr></thead>
        <tbody>
          <tr><td>דפדפן</td><td lang="en" dir="ltr">{e(A.get('browser', ''))}</td></tr>
          <tr><td>בדיקה אוטומטית</td><td lang="en" dir="ltr">{e(A.get('tool', ''))}</td></tr>
          <tr><td>תצוגות</td><td>מחשב ברוחב 1440 פיקסלים, טלפון ברוחב 390, מסך צר ברוחב 320, והגדלה של פי 2</td></tr>
        </tbody>
      </table>
      <p>{e(A.get('audit_note', ''))}</p>
    </section>

    <section aria-labelledby="s4"><h2 id="s4">מגבלות ידועות</h2>
      <p>אלה הנושאים שעדיין לא הושלמו. אם אחד מהם מקשה עליכם, פנו אלינו ונעזור בדרך אחרת:</p>
      <ul class="bul">
        {''.join(f'<li>{e(x)}</li>' for x in A.get('limits', []))}
      </ul>
    </section>

    <section aria-labelledby="s4b"><h2 id="s4b">שירותים חיצוניים</h2>
      <p>חלק מהשירותים שהאתר מקשר אליהם פועלים על מערכות של חברות אחרות:</p>
      <ul class="bul">
        <li>טופסי ההרשמה לחוגים פועלים על טופסי גוגל. התוכן בטפסים, כולל המחירונים, הוא של בארבור ובאחריותו.</li>
        <li>האירועים והרכישה פועלים במערכת קוינג. מערכת קוינג עצמה באחריות החברה שמפעילה אותה, ופרטי האירועים שבארבור מפרסם בה באחריותו.</li>
        <li>וואטסאפ, מפות גוגל, פייסבוק ואינסטגרם הם שירותים של חברות אחרות, ונגישותם באחריותן.</li>
      </ul>
      <p>אם נתקלתם בקושי באחד מהם, פנו אלינו בטלפון, בוואטסאפ או במייל, ונשלים את ההרשמה, הרכישה או הבירור יחד איתכם.</p>
    </section>

    <section aria-labelledby="s5"><h2 id="s5">נתקלתם בבעיה? פנו לרכז הנגישות</h2>
      <p>אם משהו באתר לא נגיש לכם, או שאתם צריכים מידע מהאתר בדרך אחרת, נשמח לשמוע ולתקן. כדאי לציין באיזה עמוד מדובר, מה הבעיה, ובאיזה מכשיר ודפדפן השתמשתם.</p>
      <dl class="coord">
        <dt>רכז הנגישות</dt><dd>{e(co['name'])}</dd>
        <dt>טלפון</dt><dd><a href="tel:{co['tel_i']}">{ltr(co['tel'])}</a></dd>
        <dt>מייל</dt><dd><a href="mailto:{e(co['mail'])}">{ltr(co['mail'])}</a></dd>
        <dt>כתובת</dt><dd>קאנטרי קהילתי בארבור, {e(C['addr'])}</dd>
      </dl>
      <p>אפשר לפנות גם למזכירות בארבור: טלפון <a href="tel:{C['tel_i']}">{ltr(C['tel'])}</a>, וואטסאפ <a href="https://wa.me/{C['wa_i']}">{ltr(C['wa'])}</a>.</p>
      <p>מידע על נגישות השירותים של העירייה כולה מופיע ב<a href="https://www.tel-aviv.gov.il/Transparency/Pages/AccessibilityStatement.aspx">הצהרת הנגישות של עיריית תל אביב-יפו</a>.</p>
    </section>
  </div>
</div>"""
    page('accessibility.html', 'הצהרת נגישות · קאנטרי קהילתי בארבור', stmt,
         desc='הצהרת הנגישות של אתר קאנטרי קהילתי בארבור: רמת הנגישות, ההתאמות שבוצעו, ופרטי רכז הנגישות.', bcls='page a11y-page')
