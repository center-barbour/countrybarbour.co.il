"""בדיקת נעילת העיצוב (design-lock-v1, נעילה 16.11.2026).
רצה לפני כל בנייה. אם אחד מסממני העיצוב הנעול השתנה, הבנייה נכשלת והאתר לא מתעדכן.
שינוי מכוון בעיצוב הנעול: רק באישור מפורש של דניאל, ואז מעדכנים גם את הבדיקה הזו ואת DESIGN-LOCK.md.
"""
import json, pathlib, re, sys
H = pathlib.Path(__file__).resolve().parent.parent
S = json.loads((H / 'content' / 'site.json').read_text(encoding='utf-8'))
css = (H / 'site.css').read_text(encoding='utf-8')
idx = (H / 'index.html').read_text(encoding='utf-8') if (H / 'index.html').exists() else ''
bad = []
def need(cond, msg):
    if not cond: bad.append(msg)

# 1. הפתיחה הגדולה: סרטון הרחפן ראשון, כותרת נבחרת
need(S['hero'] and S['hero'][0]['media'] == 'v:drone', 'הפריט הראשון בפתיחה חייב להיות סרטון הרחפן (v:drone)')
need((H / 'm' / 'drone.mp4').exists() and (H / 'm' / 'drone.jpg').exists(), 'קובצי סרטון הרחפן חסרים (m/drone.mp4, m/drone.jpg)')
need(S['meta'].get('headline') == 'מקום אחד לכל מה שטוב.', 'הכותרת הראשית חייבת להיות "מקום אחד לכל מה שטוב."')

# 2. מחלקות העיצוב
build = (H / 'tools' / 'build.py').read_text(encoding='utf-8')
need('look-b look-c' in build, 'מחלקות העיצוב look-b look-c הוסרו מהבנייה')
if idx:
    need('class="look-b look-c"' in idx, 'דף הבית לא נבנה עם look-b look-c')
    need('logo/main.png' in idx, 'הלוגו המלא (logo/main.png) לא מופיע בדף הבית')

# 3. צבעי המחלקות וצבעי הסלוגן
COLORS = {'pool': '#037cab', 'swim': '#13808f', 'tots': '#cc3349', 'dance': '#8f5d99', 'youth': '#65478a',
          'sport': '#103d6c', 'music': '#3f454c', 'culture': '#961a2d'}
for k, c in COLORS.items():
    need(re.search(r'\.t-%s,\.d-%s\{--dc:%s\}' % (k, k, c), css, re.I), f'צבע המחלקה {k} השתנה (צריך {c})')
need('--dc:#336299' in css, 'הצבע הכללי למחלקות (#336299) השתנה')
for c in ('#29abd9', '#e2475f', '#f19b3a'):
    need(c in css.lower(), f'צבע הסלוגן {c} חסר')

# 4. רכיבי מבנה נעולים
for sel, name in (('.marq', 'פס המחלקות הנע'), ('.scrolled .top', 'הכותרת שהופכת ללבנה בגלילה'),
                  ('.look-c', 'עיצוב הפתיחה המלאה'), ('prefers-reduced-motion', 'כיבוי תנועה למי שביקש')):
    need(sel in css, f'{name} ({sel}) הוסר מ-site.css')
need('Heebo' in css, 'הגופן Heebo הוסר')

if bad:
    print('נעילת העיצוב נפרצה:'); [print(' -', b) for b in bad]; sys.exit(1)
print('העיצוב הנעול שלם')
