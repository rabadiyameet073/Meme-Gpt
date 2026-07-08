"""Generate 500+ meme dataset locally."""
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

INDIAN = [
    {"name": "Aukat Me Reh", "keywords": ["aukat", "impossible", "dream", "100%", "unrealistic"], "dialogue": "Khwab To Dekho Magar Aukat Ke Hisab Se", "explanation": "When someone expects more than what's realistically possible.", "video": "https://youtube.com/aukat", "gif": "aukat.gif"},
    {"name": "Ye Sab Doglapan Hai", "keywords": ["hypocrisy", "fake", "double standards", "doglapan"], "dialogue": "Ye Sab Doglapan Hai", "explanation": "Perfect for hypocritical expectations.", "gif": "doglapan.gif"},
    {"name": "Khwab Dekho Raat Bhar", "keywords": ["dream", "100% accuracy", "impossible", "overnight", "accuracy"], "dialogue": "Khwab Dekho Raat Bhar", "explanation": "When unrealistic expectations meet harsh reality.", "gif": "khwab.gif"},
    {"name": "Bhai Tu Toh Gaya", "keywords": ["screwed", "dead", "finished"], "dialogue": "Bhai Tu Toh Gaya", "explanation": "When you're in deep trouble.", "gif": "gaya.gif"},
    {"name": "Thak Gaya Hu Bhai", "keywords": ["tired", "exhausted", "burnout"], "dialogue": "Thak Gaya Hu Bhai", "explanation": "Burnout from endless work.", "gif": "thak.gif"},
    {"name": "Beta Tumse Na Ho Payega", "keywords": ["can't do", "failure", "impossible"], "dialogue": "Beta Tumse Na Ho Payega", "explanation": "Task beyond current capability.", "gif": "naho.gif"},
    {"name": "All Is Well", "keywords": ["denial", "everything fine"], "dialogue": "All Is Well", "explanation": "Denying problems while everything falls apart.", "gif": "alliswell.gif"},
    {"name": "Itna Confidence Kahan Se Laata Hai", "keywords": ["overconfident", "confidence"], "dialogue": "Itna Confidence Kahan Se Laata Hai", "explanation": "Absurd overconfidence about impossible tasks.", "gif": "confidence.gif"},
    {"name": "Chal Be", "keywords": ["nonsense", "reject"], "dialogue": "Chal Be", "explanation": "Dismissal of absurd requests.", "gif": "chalbe.gif"},
    {"name": "Bhai Kya Kar Diya", "keywords": ["messed up", "disaster"], "dialogue": "Bhai Kya Kar Diya", "explanation": "Someone broke production badly.", "gif": "kyakar.gif"},
]

CODING = [
    {"name": "It Works On My Machine", "keywords": ["bug", "deploy", "production"], "dialogue": "It Works On My Machine", "explanation": "Code fails only in production.", "gif": "machine.gif"},
    {"name": "Merge Conflict Hell", "keywords": ["merge conflict", "git"], "dialogue": "Merge Conflict Hell", "explanation": "Git merge conflicts.", "gif": "merge.gif"},
    {"name": "Production Is Down", "keywords": ["production", "down", "outage"], "dialogue": "Production Is Down And It's My Code", "explanation": "Prod broke because of your code.", "gif": "prod.gif"},
    {"name": "Deadline Tomorrow", "keywords": ["deadline", "tomorrow", "client"], "dialogue": "Client Wants It Tomorrow", "explanation": "Impossible deadline.", "gif": "deadline.gif"},
    {"name": "12% Accuracy Fix", "keywords": ["accuracy", "12%", "100%", "model", "ml"], "dialogue": "12% To 100% By Tomorrow?", "explanation": "Unrealistic ML improvement expectations.", "gif": "accuracy.gif"},
]

STARTUP = [
    {"name": "We Are Like A Family", "keywords": ["startup", "family", "toxic"], "dialogue": "We Are Like A Family Here", "explanation": "Toxic startup culture.", "gif": "family.gif"},
    {"name": "Runway Ending", "keywords": ["runway", "funding", "burn rate"], "dialogue": "Runway Ending In 2 Weeks", "explanation": "Startup running out of money.", "gif": "runway.gif"},
    {"name": "Pivot Again", "keywords": ["pivot", "startup"], "dialogue": "Time To Pivot Again", "explanation": "Constant direction changes.", "gif": "pivot.gif"},
]

RELATIONSHIP = [
    {"name": "Seen But No Reply", "keywords": ["ghost", "seen", "message"], "dialogue": "Seen At 2 AM, No Reply", "explanation": "Left on read.", "gif": "seen.gif"},
    {"name": "Friendzone Level Max", "keywords": ["friendzone", "crush"], "dialogue": "Friendzone Level: Legendary", "explanation": "Permanently friendzoned.", "gif": "friendzone.gif"},
]

COLLEGE = [
    {"name": "Backlog Mountain", "keywords": ["backlog", "failed"], "dialogue": "Backlog Mountain Growing", "explanation": "Accumulating failed subjects.", "gif": "backlog.gif"},
    {"name": "Assignment Night Before", "keywords": ["assignment", "deadline"], "dialogue": "Assignment Due Tomorrow, Starting Now", "explanation": "Last minute procrastination.", "gif": "assignment.gif"},
]

OFFICE = [
    {"name": "This Meeting Could Be Email", "keywords": ["meeting", "email"], "dialogue": "This Meeting Could Have Been An Email", "explanation": "Unnecessary meetings.", "gif": "meeting.gif"},
    {"name": "HR Wants To Talk", "keywords": ["hr", "fired"], "dialogue": "HR Wants To Talk", "explanation": "Dreaded HR message.", "gif": "hr.gif"},
]

EXAM = [
    {"name": "JEE Advanced Trauma", "keywords": ["jee", "exam", "rank"], "dialogue": "JEE Advanced Trauma Activated", "explanation": "Competitive exam pressure.", "gif": "jee.gif"},
    {"name": "One Night Syllabus", "keywords": ["exam tomorrow", "syllabus"], "dialogue": "Exam Tomorrow, Syllabus Untouched", "explanation": "Last night panic.", "gif": "syllabus.gif"},
]

GAMING = [
    {"name": "Lag Spike During Clutch", "keywords": ["lag", "gaming", "clutch"], "dialogue": "Lag Spike During Clutch", "explanation": "Lag at worst moment.", "gif": "lag.gif"},
    {"name": "One More Game", "keywords": ["gaming", "addiction"], "dialogue": "One More Game At 4 AM", "explanation": "Gaming addiction.", "gif": "onemore.gif"},
]

AI = [
    {"name": "Hallucination Nation", "keywords": ["hallucination", "llm", "ai"], "dialogue": "AI Hallucinated The Entire Answer", "explanation": "AI making up false info.", "gif": "hallucination.gif"},
    {"name": "ChatGPT Wrote My Code", "keywords": ["chatgpt", "code", "ai"], "dialogue": "ChatGPT Wrote Better Code Than Me", "explanation": "AI outcoding you.", "gif": "ai-code.gif"},
]

MOTIVATION = [
    {"name": "Rise And Grind", "keywords": ["grind", "hustle", "motivation"], "dialogue": "Rise And Grind At 5 AM", "explanation": "Toxic productivity culture.", "gif": "grind.gif"},
]

BUSINESS = [
    {"name": "Q4 Target", "keywords": ["target", "sales", "q4"], "dialogue": "Q4 Target Is Impossible", "explanation": "Unrealistic sales targets.", "gif": "q4.gif"},
]

YOUTUBE = [
    {"name": "Like Share Subscribe", "keywords": ["youtube", "subscribe"], "dialogue": "Like Share Subscribe Or Else", "explanation": "YouTuber CTA satire.", "gif": "subscribe.gif"},
]

BOLlywood = [
    {"name": "Don Ko Pakadna Mushkil", "keywords": ["don", "impossible", "bollywood"], "dialogue": "Don Ko Pakadna Mushkil Hi Nahi Namumkin Hai", "explanation": "Impossible task Bollywood style.", "gif": "don.gif"},
    {"name": "Picture Abhi Baaki Hai", "keywords": ["twist", "bollywood"], "dialogue": "Picture Abhi Baaki Hai Mere Dost", "explanation": "More drama coming.", "gif": "picture.gif"},
]

GROUPS = [
    ("unrealistic_goals", INDIAN),
    ("funny", INDIAN),
    ("coding", CODING),
    ("startup", STARTUP),
    ("relationship", RELATIONSHIP),
    ("college", COLLEGE),
    ("office", OFFICE),
    ("exam", EXAM),
    ("gaming", GAMING),
    ("ai", AI),
    ("motivation", MOTIVATION),
    ("business", BUSINESS),
    ("youtube", YOUTUBE),
    ("bollywood", BOLlywood),
    ("failure", INDIAN + CODING),
    ("success", [m for m in INDIAN if "Well" in m["name"]]),
]

VARIATIONS = [
    "Classic", "Deluxe", "Ultra", "Pro Max", "OG", "Desi", "Elite", "Turbo", "V2", "Final",
    "Remix", "Reloaded", "Supreme", "Mega", "Mini", "Plus", "HD", "4K", "Uncut", "Ultimate",
    "2024", "2025", "Legendary", "Premium", "Raw", "Unfiltered", "Peak", "Sigma", "Alpha", "Beta",
]
SUFFIXES = [
    "at 3 AM", "during meeting", "before deadline", "in production", "on Monday",
    "after result", "in hostel", "during interview", "before exam", "on Friday",
    "after deploy", "in standup", "during review", "at family function", "in traffic",
]


def build_dataset() -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []

    def add(meme: dict):
        key = meme["name"].lower()
        if key not in seen:
            seen.add(key)
            result.append(meme)

    for category, bases in GROUPS:
        for base in bases:
            add({**base, "category": category, "viralScore": random.uniform(50, 100)})

    for category, bases in GROUPS:
        for base in bases:
            for var in VARIATIONS:
                for suffix in SUFFIXES[:4]:
                    name = f"{base['name']} — {var}"
                    if name.lower() in seen:
                        continue
                    add({
                        "name": name,
                        "category": category,
                        "keywords": base["keywords"] + [var.lower()] + suffix.split(),
                        "dialogue": f"{base['dialogue']} ({suffix})",
                        "explanation": f"{base['explanation']} Especially relatable {suffix}.",
                        "video": base.get("video"),
                        "gif": base.get("gif"),
                        "viralScore": random.uniform(30, 100),
                    })
                    if len(result) >= 520:
                        return result
    return result


MEME_DATASET = build_dataset()


def export_json():
    path = DATA_DIR / "memes.json"
    path.write_text(json.dumps(MEME_DATASET, indent=2), encoding="utf-8")
    print(f"Exported {len(MEME_DATASET)} memes to {path}")


if __name__ == "__main__":
    export_json()
