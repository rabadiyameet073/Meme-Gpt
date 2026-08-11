"""MemeGPT — Master Meme Dataset Collector & Builder.

1. Downloads 100 top global meme templates from Imgflip API (with real image URLs).
2. Enriches Imgflip memes with categories, dialogues, explanations, and keywords.
3. Merges 60+ iconic Indian/Hindi viral pop-culture memes (Hera Pheri, Welcome, Wasseypur, 3 Idiots, etc.).
4. Builds a clean, unified dataset of 160+ unique meme templates.
"""
import json
import re
from pathlib import Path
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "backend" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Indian & Hindi Viral Meme Dataset (Iconic Pop Culture) ─────────────────

INDIAN_MEMES = [
    {
        "name": "Aukat Me Reh",
        "category": "unrealistic_goals",
        "keywords": ["aukat", "impossible", "dream", "100%", "unrealistic", "overnight", "goal", "target", "accuracy", "hindi"],
        "dialogue": "Khwab To Dekho Magar Aukat Ke Hisab Se",
        "explanation": "When someone demands or expects something far beyond realistic possibilities.",
        "gif": "aukat.gif",
        "video": "https://youtube.com/aukat",
        "viralScore": 97.5,
    },
    {
        "name": "Ye Sab Doglapan Hai",
        "category": "funny",
        "keywords": ["hypocrisy", "fake", "double standards", "doglapan", "shark tank", "anupam", "lie", "pretend", "hindi"],
        "dialogue": "Ye Sab Doglapan Hai",
        "explanation": "Calling out hypocritical behavior, fake promises, or double standards.",
        "gif": "doglapan.gif",
        "viralScore": 96.0,
    },
    {
        "name": "Khwab Dekho Raat Bhar",
        "category": "unrealistic_goals",
        "keywords": ["dream", "100% accuracy", "impossible", "overnight", "accuracy", "12%", "effort", "lazy", "hindi"],
        "dialogue": "Khwab Dekho Raat Bhar, Kaam Karo Jhaat Bhar",
        "explanation": "Grand ambitions accompanied by zero effort or preparation.",
        "gif": "khwab.gif",
        "viralScore": 94.0,
    },
    {
        "name": "Bhai Tu Toh Gaya",
        "category": "failure",
        "keywords": ["screwed", "dead", "finished", "trouble", "caught", "bhai gaya", "disaster", "hindi"],
        "dialogue": "Bhai Tu Toh Gaya!",
        "explanation": "When you realize you've made a fatal mistake or production is down.",
        "gif": "gaya.gif",
        "viralScore": 91.5,
    },
    {
        "name": "Thak Gaya Hu Bhai",
        "category": "office",
        "keywords": ["tired", "exhausted", "burnout", "fatigue", "corporate", "life", "overtime", "monday", "hindi"],
        "dialogue": "Thak Gaya Hu Bhai, Jiya Nahi Ja Raha",
        "explanation": "Complete physical and mental exhaustion from endless work or stress.",
        "gif": "thak.gif",
        "viralScore": 98.0,
    },
    {
        "name": "Beta Tumse Na Ho Payega",
        "category": "failure",
        "keywords": ["can't do", "failure", "impossible", "gangs of wasseypur", "hopeless", "give up", "hindi"],
        "dialogue": "Beta Tumse Na Ho Payega",
        "explanation": "A brutal reality check when a task is completely out of reach.",
        "gif": "naho.gif",
        "viralScore": 95.5,
    },
    {
        "name": "All Is Well",
        "category": "success",
        "keywords": ["denial", "everything fine", "3 idiots", "panic", "calm", "all is well", "exam", "hindi"],
        "dialogue": "All Is Well! All Is Well!",
        "explanation": "Chanting fake reassurance while everything around you crumbles.",
        "gif": "alliswell.gif",
        "viralScore": 93.0,
    },
    {
        "name": "Itna Confidence Kahan Se Aata Hai",
        "category": "funny",
        "keywords": ["overconfident", "confidence", "bold", "arrogant", "ego", "prep", "fake it", "hindi"],
        "dialogue": "Itna Confidence Kahan Se Aata Hai?",
        "explanation": "Mind-boggling confidence despite having zero preparation.",
        "gif": "confidence.gif",
        "viralScore": 89.0,
    },
    {
        "name": "Chal Be",
        "category": "funny",
        "keywords": ["nonsense", "reject", "dismiss", "move on", "hawa aane de", "ignore", "hindi"],
        "dialogue": "Chal Be Hawa Aane De",
        "explanation": "Immediate rejection of unwanted advice or absurd requests.",
        "gif": "chalbe.gif",
        "viralScore": 87.0,
    },
    {
        "name": "Bhai Kya Kar Diya",
        "category": "coding",
        "keywords": ["messed up", "disaster", "broke production", "error", "bug", "what did you do", "hindi"],
        "dialogue": "Bhai Kya Kar Diya Tumne!",
        "explanation": "Instant regret and panic after accidentally breaking something vital.",
        "gif": "kyakar.gif",
        "viralScore": 97.0,
    },
    {
        "name": "Control Uday Control",
        "category": "office",
        "keywords": ["anger", "rage", "control", "welcome", "majnu", "chill", "calm down", "frustration", "hindi"],
        "dialogue": "Control Uday Control...",
        "explanation": "Fighting the urge to snap at an annoying boss, client, or situation.",
        "gif": "control.gif",
        "viralScore": 96.5,
    },
    {
        "name": "Seh Lenge Thoda",
        "category": "office",
        "keywords": ["seh lenge", "suffering", "pain", "endurance", "compromise", "welcome", "sad", "hindi"],
        "dialogue": "Seh Lenge Thoda Sa...",
        "explanation": "Resigned acceptance of unfair suffering or extra workload.",
        "gif": "sehlenge.gif",
        "viralScore": 95.0,
    },
    {
        "name": "Kaun Hai Ye Log",
        "category": "funny",
        "keywords": ["kaun hai ye log", "kahan se aate hain", "disbelief", "stupid", "absurd", "shock", "hindi"],
        "dialogue": "Kaun Hai Ye Log? Kahan Se Aate Hain Ye?",
        "explanation": "Utter bewilderment at incomprehensibly silly decisions or questions.",
        "gif": "kaunhai.gif",
        "viralScore": 94.5,
    },
    {
        "name": "Paisa Hi Paisa Hoga",
        "category": "money",
        "keywords": ["paisa", "money", "rich", "hera pheri", "profit", "scheme", "stonks", "wealth", "hindi"],
        "dialogue": "Paisa Hi Paisa Hoga!",
        "explanation": "Daydreaming about infinite riches after a new investment or idea.",
        "gif": "paisa.gif",
        "viralScore": 98.5,
    },
    {
        "name": "Babu Bhaiya Utha Le",
        "category": "office",
        "keywords": ["babu bhaiya", "hera pheri", "utha le", "frustration", "annoyed", "coworkers", "hindi"],
        "dialogue": "Utha Le Re Baba, Mereko Nahi Re In Dono Ko Utha Le!",
        "explanation": "Extreme irritation with incompetent teammates or annoying situations.",
        "gif": "uthale.gif",
        "viralScore": 97.8,
    },
    {
        "name": "Zindagi Jhand Ba Phir Bhi Ghamand Ba",
        "category": "funny",
        "keywords": ["zindagi jhand", "ghamand", "attitude", "mess", "flex", "broke", "bhojpuri", "hindi"],
        "dialogue": "Zindagi Jhand Ba, Phir Bhi Ghamand Ba!",
        "explanation": "Maintaining unshakeable swagger even when life is completely ruined.",
        "gif": "zindagi.gif",
        "viralScore": 92.0,
    },
    {
        "name": "Teja Main Hu Mark Idhar Hai",
        "category": "office",
        "keywords": ["teja", "mark", "credit stealer", "andaz apna apna", "fake", "identity", "hindi"],
        "dialogue": "Teja Main Hu, Mark Idhar Hai!",
        "explanation": "When someone tries to steal credit for work they didn't do.",
        "gif": "teja.gif",
        "viralScore": 88.0,
    },
    {
        "name": "Waah Kya Acting Kar Raha Hai",
        "category": "funny",
        "keywords": ["acting", "fake", "drama", "sarcastic", "applause", "paresh rawal", "excuse", "hindi"],
        "dialogue": "Waah Kya Acting Kar Raha Hai!",
        "explanation": "Sarcastic applause for melodramatic excuses or transparent lies.",
        "gif": "acting.gif",
        "viralScore": 91.0,
    },
    {
        "name": "Arey Mujhe Chakkar Aane Laga Hai",
        "category": "exam",
        "keywords": ["chakkar", "dizzy", "shock", "workload", "panic", "welcome", "headache", "hindi"],
        "dialogue": "Arey Mujhe Chakkar Aane Laga Hai!",
        "explanation": "Physical dizziness triggered by sudden bad news, exam papers, or tasks.",
        "gif": "chakkar.gif",
        "viralScore": 93.5,
    },
    {
        "name": "Jor Jor Se Bolke Sabko Scheme Batade",
        "category": "business",
        "keywords": ["scheme", "secret", "leak", "loud", "hera pheri", "confidential", "shortcut", "hindi"],
        "dialogue": "Jor Jor Se Bolke Sabko Scheme Batade!",
        "explanation": "Accidentally shouting out secret strategies or internal hacks.",
        "gif": "scheme.gif",
        "viralScore": 95.2,
    },
    {
        "name": "Systummm Hang",
        "category": "gaming",
        "keywords": ["systumm", "elvish", "hang", "crash", "power", "flex", "hype", "hindi"],
        "dialogue": "Systummm Hang Kar Diya!",
        "explanation": "Causing total overload, hype, or crashing the server by sheer dominance.",
        "gif": "systumm.gif",
        "viralScore": 89.5,
    },
    {
        "name": "Moye Moye",
        "category": "failure",
        "keywords": ["moye moye", "tragedy", "disappointment", "fail", "sad reality", "karma", "hindi"],
        "dialogue": "Moye Moye... (Tragic reality hits)",
        "explanation": "High expectations getting crushed by unexpected, comical tragedy.",
        "gif": "moye.gif",
        "viralScore": 99.0,
    },
    {
        "name": "Rasode Mein Kaun Tha",
        "category": "funny",
        "keywords": ["rasode mein kaun tha", "investigation", "blame", "culprit", "kokilaben", "who broke build", "hindi"],
        "dialogue": "Rasode Mein Kaun Tha? Main Thi? Tum Thi? Kaun Tha?",
        "explanation": "Interrogating the team to find out who broke the build or caused the issue.",
        "gif": "rasode.gif",
        "viralScore": 90.0,
    },
    {
        "name": "Risk Hai Toh Ishq Hai",
        "category": "startup",
        "keywords": ["risk", "ishq", "mirzapur", "scam 1992", "harshad mehta", "bold", "gamble", "hindi"],
        "dialogue": "Risk Hai Toh Ishq Hai!",
        "explanation": "Taking extreme, dangerous bets in code, career, or business.",
        "gif": "risk.gif",
        "viralScore": 96.8,
    },
    {
        "name": "Choti Bacchi Ho Kya",
        "category": "funny",
        "keywords": ["choti bacchi ho kya", "immature", "childish", "obvious", "tiger shroff", "hindi"],
        "dialogue": "Choti Bacchi Ho Kya?",
        "explanation": "When someone acts childlike or fails to grasp basic common sense.",
        "gif": "bacchi.gif",
        "viralScore": 91.2,
    },
    {
        "name": "Kya Karu Main Mar Jau",
        "category": "relationship",
        "keywords": ["mar jau", "feelings", "ignored", "dramatic", "shehnaaz", "offended", "hindi"],
        "dialogue": "Kya Karu Main Mar Jau? Meri Koi Feelings Nahi Hai?",
        "explanation": "Over-the-top dramatic reaction to being neglected or unappreciated.",
        "gif": "marjau.gif",
        "viralScore": 94.2,
    },
    {
        "name": "Looking Like A Wow",
        "category": "success",
        "keywords": ["looking like a wow", "elegant", "beautiful", "aesthetic", "clean code", "perfection", "hindi"],
        "dialogue": "So Beautiful, So Elegant, Just Looking Like A Wow!",
        "explanation": "Admiring something that turns out absolutely gorgeous and perfect.",
        "gif": "wow.gif",
        "viralScore": 95.8,
    },
    {
        "name": "Abhi Hum Zinda Hain",
        "category": "success",
        "keywords": ["zinda hain", "alive", "survived", "comeback", "welcome", "not dead yet", "hindi"],
        "dialogue": "Abhi Hum Zinda Hain!",
        "explanation": "Surviving a brutal ordeal, exam, or system crash against all odds.",
        "gif": "zinda.gif",
        "viralScore": 92.5,
    },

    # ── BABU RAO & HERA PHERI COMEDY HALL OF FAME ─────────────────────────────
    {
        "name": "Babu Rao Deviprasad Ghar Pe Hai",
        "category": "funny",
        "keywords": ["babu rao", "hera pheri", "deviprasad", "wrong number", "call", "miscommunication", "pehle lagaya aisa", "hindi"],
        "dialogue": "Deviprasad Ghar Pe Hai?... Pehle Lagaya Aisa, Toh Main Bola Aisa!",
        "explanation": "Hilarious confusion over wrong numbers, miscommunication, or bad phone calls.",
        "gif": "deviprasad.gif",
        "viralScore": 99.5,
    },
    {
        "name": "Babu Rao Ye Babu Rao Ka Style Hai",
        "category": "funny",
        "keywords": ["babu rao", "hera pheri", "style", "swagger", "flex", "kutriya", "confidence", "attitude", "hindi"],
        "dialogue": "Kutriya... Ye Babu Rao Ka Style Hai!",
        "explanation": "Unapologetic swagger and chaotic flex in front of everyone.",
        "gif": "style.gif",
        "viralScore": 99.2,
    },
    {
        "name": "Babu Rao Khopdi Tod Saale Ka",
        "category": "funny",
        "keywords": ["babu rao", "hera pheri", "khopdi tod", "rage", "anger", "slap", "destroy", "annoyed", "hindi"],
        "dialogue": "Saala Khopdi Tod Re Khopdi Tod Saale Ka!",
        "explanation": "Extreme urge to physically smack someone who asks a incredibly stupid question.",
        "gif": "khopditod.gif",
        "viralScore": 99.8,
    },
    {
        "name": "Babu Rao Mast Joke Mara Re",
        "category": "funny",
        "keywords": ["babu rao", "hera pheri", "mast joke", "halka cut", "laughing", "sarcastic", "hahas", "joke", "hindi"],
        "dialogue": "Mast Joke Mara Re Hahahaha Ha... Yeh Has Re Halka Cut!",
        "explanation": "Bursting into uncontrollable laughter at a terrible or sarcastic joke.",
        "gif": "mastjoke.gif",
        "viralScore": 98.9,
    },
    {
        "name": "Babu Rao Dhak Dhak Horela Hai",
        "category": "exam",
        "keywords": ["babu rao", "hera pheri", "dhak dhak", "panic", "anxiety", "scared", "heartbeat", "deadline", "hindi"],
        "dialogue": "Arey Mere Ko To Aisa Dhak Dhak Horela Hai!",
        "explanation": "Severe anxiety and heart palpitations before exam results, prod deploys, or interview.",
        "gif": "dhakdhak.gif",
        "viralScore": 99.7,
    },
    {
        "name": "Raju 25 Din Mein Paisa Double",
        "category": "money",
        "keywords": ["raju", "hera pheri", "paisa double", "scam", "scheme", "investment", "crypto", "stonks", "get rich quick", "hindi"],
        "dialogue": "25 Din Mein Paisa Double!",
        "explanation": "Shady financial schemes promising instant doubling of money.",
        "gif": "paisadouble.gif",
        "viralScore": 99.1,
    },
    {
        "name": "Kachra Seth 150 Rupiya Dega",
        "category": "money",
        "keywords": ["kachra seth", "hera pheri", "150 rupiya", "lowball", "cheap", "negotiation", "budget", "freelance", "hindi"],
        "dialogue": "150 Rupiya Dega!",
        "explanation": "Insultingly low price offer during budget talks or client negotiations.",
        "gif": "150rupiya.gif",
        "viralScore": 98.6,
    },
    {
        "name": "Munna Bhai Circuit Bhai Ne Bola Karne Ka",
        "category": "office",
        "keywords": ["munna bhai", "circuit", "bhai ne bola", "loyalty", "boss order", "blind follow", "do it", "hindi"],
        "dialogue": "Bhai Ne Bola Karne Ka... Toh Karne Ka!",
        "explanation": "Blindly following a senior's or boss's bizarre command without questioning.",
        "gif": "bhai-ne-bola.gif",
        "viralScore": 97.4,
    },
    {
        "name": "Circuit Jadu Ki Jhappi",
        "category": "funny",
        "keywords": ["circuit", "munna bhai", "jadu ki jhappi", "hug", "comfort", "wholesome", "friendship", "hindi"],
        "dialogue": "Mamu Jadu Ki Jhappi De Na!",
        "explanation": "Offering warm emotional comfort to a stressed-out friend or teammate.",
        "gif": "jhappi.gif",
        "viralScore": 95.8,
    },
    {
        "name": "Dekh Raha Hai Binod",
        "category": "office",
        "keywords": ["dekh raha hai binod", "panchayat", "binod", "scam", "fooled", "corporate english", "manipulation", "hindi"],
        "dialogue": "Dekh Raha Hai Binod, Kaise Angrezi Mein Humko Bewakoof Banaya Ja Raha Hai!",
        "explanation": "Watching someone use fancy jargon or English to scam or fool people.",
        "gif": "binod.gif",
        "viralScore": 98.4,
    },
    {
        "name": "Crime Master Gogo Gotiyan Khelunga",
        "category": "funny",
        "keywords": ["crime master gogo", "andaz apna apna", "gotiyan", "threat", "scary", "comedy villain", "gogo", "hindi"],
        "dialogue": "Aankhein Nikal Kar Gotiyan Khelunga!",
        "explanation": "Comical villainous threats when someone tampers with your stuff.",
        "gif": "gogo.gif",
        "viralScore": 96.2,
    },
    {
        "name": "Vasooli Bhai Paisa Kab Dega",
        "category": "money",
        "keywords": ["vasooli bhai", "golmaal", "paisa kab dega", "debt", "salary late", "payment overdue", "chillar", "hindi"],
        "dialogue": "Aaye Raka! Paisa Kab Dega Vasooli?!",
        "explanation": "Demanding long-overdue payments, salary, or splitwise dues.",
        "gif": "vasooli.gif",
        "viralScore": 97.1,
    },
    {
        "name": "Jethalal Chai Piyo Biskut Khao",
        "category": "funny",
        "keywords": ["jethalal", "tmkoc", "chai piyo", "biskut khao", "chill", "break", "tea time", "taarak mehta", "hindi"],
        "dialogue": "Chai Piyo Biskut Khao... Nonsense!",
        "explanation": "Taking a peaceful tea break while refusing to deal with chaotic drama.",
        "gif": "jethalal.gif",
        "viralScore": 98.7,
    },
    {
        "name": "Faizal Badla Lega Re",
        "category": "failure",
        "keywords": ["faizal", "wasseypur", "badla", "revenge", "payback", "gangs of wasseypur", "never forget", "hindi"],
        "dialogue": "Baap Ka, Dada Ka, Bhai Ka... Sabka Badla Lega Re Tera Faizal!",
        "explanation": "Planning grand vengeance against bugs, exes, or rival teams.",
        "gif": "faizal.gif",
        "viralScore": 97.9,
    },

]

# ── 2. Helper to categorise and enrich Imgflip template names ─────────────────

CATEGORY_MAP = {
    "coding": ["drake", "buttons", "brain", "disaster", "homer", "change my mind", "exit", "batman", "computer", "matrix", "spiderman"],
    "office": ["yelling", "harold", "pablo", "pigeon", "office", "clown", "work", "meeting", "boss"],
    "failure": ["fine", "pikachu", "bad luck", "gru", "panik", "first time", "burn", "fail", "noose"],
    "success": ["success", "chad", "epic", "won", "nod"],
    "unrealistic_goals": ["trade", "drawing", "cards", "car", "wish", "impossible"],
    "money": ["stonks", "money", "asking", "cash", "crypto", "rich"],
    "relationship": ["boyfriend", "girl", "cheating", "text", "crush"],
    "ai": ["robot", "future", "ai", "bot", "gpt"],
}


def infer_metadata(name: str, url: str) -> dict:
    nl = name.lower()

    # Category matching
    category = "funny"
    for cat, keywords in CATEGORY_MAP.items():
        if any(k in nl for k in keywords):
            category = cat
            break

    # Dialogue creation
    dialogue = f"{name} Reaction"
    if "drake" in nl:
        dialogue = "Nah / Yeah Drake Reaction"
    elif "buttons" in nl:
        dialogue = "Sweating over two impossible choices"
    elif "distracted" in nl:
        dialogue = "Distracted by new shiny options"
    elif "change my mind" in nl:
        dialogue = "Sitting at the table... Change My Mind!"
    elif "this is fine" in nl:
        dialogue = "This is fine. Everything is totally fine."
    elif "disaster girl" in nl:
        dialogue = "Smiling while watching the chaos burn"
    elif "yelling" in nl:
        dialogue = "Yelling at someone who has no idea what happened"
    elif "pikachu" in nl:
        dialogue = "Surprised Pikachu Face!"
    elif "harold" in nl:
        dialogue = "Smiling on the outside, pain on the inside"
    elif "trade offer" in nl:
        dialogue = "I receive... You receive..."

    # Keywords creation
    words = re.findall(r"\b[a-zA-Z]{3,}\b", nl)
    keywords = list(set(words + [category, "meme", "viral", "reaction"]))

    explanation = f"The classic '{name}' meme template, perfect for {category.replace('_', ' ')} scenarios."

    return {
        "name": name,
        "category": category,
        "keywords": keywords,
        "dialogue": dialogue,
        "explanation": explanation,
        "image": url,
        "gif": None,
        "viralScore": 85.0,
    }


def fetch_imgflip_memes() -> list[dict]:
    print("Fetching top 100 meme templates from Imgflip API...")
    try:
        r = requests.get("https://api.imgflip.com/get_memes", timeout=10)
        data = r.json().get("data", {}).get("memes", [])
        print(f"Downloaded {len(data)} Imgflip meme templates.")
        res = []
        for m in data:
            res.append(infer_metadata(m["name"], m["url"]))
        return res
    except Exception as e:
        print(f"Error fetching Imgflip: {e}")
        return []


def main():
    imgflip = fetch_imgflip_memes()

    seen_names = set()
    master = []

    for item in INDIAN_MEMES:
        seen_names.add(item["name"].lower())
        master.append(item)

    for item in imgflip:
        if item["name"].lower() not in seen_names:
            seen_names.add(item["name"].lower())
            master.append(item)

    print(f"\n[OK] Total master meme dataset size: {len(master)} distinct memes!")

    out_file = DATA_DIR / "memes.json"
    out_file.write_text(json.dumps(master, indent=2), encoding="utf-8")
    print(f"Saved master dataset to {out_file}")


if __name__ == "__main__":
    main()
