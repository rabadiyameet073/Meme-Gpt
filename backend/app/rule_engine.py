import re
from dataclasses import dataclass, field


@dataclass
class RuleMatch:
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


RULES = [
    ("success", "success", [r"achiev", r"promot", r"pass(?:ed)?", r"won", r"crack(?:ed)?", r"selected", r"offer letter", r"celebrat", r"topper", r"victory"], 1.0),
    ("failure", "failure", [r"fail(?:ed|ure)?", r"reject", r"flunk", r"disappoint", r"ruin", r"disaster", r"worst", r"only \d+%", r"chutiyap", r"kharab"], 1.0),
    ("coding", "coding", [r"bug", r"code", r"deploy", r"git", r"merge conflict", r"stack overflow", r"api", r"database", r"compile", r"runtime", r"typescript", r"python", r"javascript", r"frontend", r"backend", r"prod"], 1.0),
    ("startup", "startup", [r"startup", r"funding", r"investor", r"pitch", r"mvp", r"burn rate", r"runway", r"cofounder", r"unicorn", r"equity"], 1.0),
    ("relationship", "relationship", [r"girlfriend", r"boyfriend", r"crush", r"breakup", r"dating", r"marriage", r"friendzone", r"relationship", r"ghost", r"pyaar", r"dil", r"shadi"], 1.0),
    ("exam", "exam", [r"exam", r"test", r"jee", r"neet", r"gate", r"upsc", r"result", r"marks", r"rank", r"stud(?:y|ying)", r"paper", r"syllabus"], 1.0),
    ("college", "college", [r"college", r"hostel", r"professor", r"assignment", r"attendance", r"campus", r"semester", r"backlog", r"canteen", r"btech"], 1.0),
    ("job", "office", [r"job", r"salary", r"boss", r"manager", r"meeting", r"deadline", r"client", r"office", r"hr", r"interview", r"layoff", r"appraisal", r"wfh", r"resignation"], 1.0),
    ("motivation", "motivation", [r"motivat", r"inspir", r"never give up", r"hustle", r"grind", r"hard work", r"believe", r"focus", r"mindset"], 0.8),
    ("unrealistic_expectation", "unrealistic_goals", [r"100%", r"perfect", r"impossible", r"overnight", r"tomorrow", r"asap", r"make it \d+", r"can you make", r"unrealistic", r"magic", r"zero bug"], 1.2),
    ("funny", "funny", [r"funny", r"lol", r"hilarious", r"embarrass", r"awkward", r"drunk", r"meme", r"roast", r"chutkule", r"joke"], 0.7),
    ("ai", "ai", [r"ai\b", r"chatgpt", r"machine learning", r"llm", r"neural", r"model", r"accuracy", r"training", r"gpt", r"openai", r"gemini", r"claude"], 1.0),
    ("business", "business", [r"business", r"profit", r"revenue", r"sales", r"customer", r"market", r"competition", r"dhandha", r"paisa"], 0.9),
    ("gaming", "gaming", [r"game", r"gaming", r"pubg", r"bgmi", r"valorant", r"rank", r"noob", r"pro player", r"lag", r"steam", r"headshot"], 0.9),
    ("bollywood", "bollywood", [r"bollywood", r"movie", r"dialogue", r"srk", r"salman", r"amir", r"film", r"cinema"], 0.6),
    ("youtube", "youtube", [r"youtube", r"vlog", r"subscriber", r"carryminati", r"stream", r"content creator", r"views"], 0.6),
    ("hypocrisy", "funny", [r"double standard", r"hypocri", r"doglapan", r"fake", r"pretend", r"jhooth"], 1.0),
    ("overconfidence", "funny", [r"overconfident", r"main character", r"sigma", r"attitude", r"aukat", r"ego"], 1.0),
    ("money", "office", [r"money", r"rich", r"poor", r"broke", r"tax", r"salary", r"bank", r"crypto", r"paisa"], 0.9),
    ("sleep", "college", [r"sleep", r"night owl", r"3 am", r"insomnia", r"tired", r"subah", r"neend"], 0.8),
]


def run_rule_engine(text: str) -> RuleMatch:
    result = RuleMatch()
    for tag, category, patterns, weight in RULES:
        if any(re.search(p, text, re.I) for p in patterns):
            result.tags.append(tag)
            if category not in result.categories:
                result.categories.append(category)
            result.scores[category] = result.scores.get(category, 0) + weight
            result.scores[f"tag:{tag}"] = result.scores.get(f"tag:{tag}", 0) + weight

    if not result.categories:
        result.categories.append("funny")
        result.tags.append("general")
        result.scores["funny"] = 0.3

    return result


EMOTION_PATTERNS = {
    "frustration": [r"bug", r"error", r"stuck", r"ruined", r"annoy", r"fail", r"broken", r"hate"],
    "anxiety": [r"exam", r"scared", r"fear", r"nervous", r"worry", r"panic", r"deadline", r"test"],
    "stress": [r"work", r"boss", r"client", r"overtime", r"busy", r"pressure", r"tired"],
    "ambition": [r"startup", r"build", r"goal", r"hustle", r"grow", r"rich", r"future"],
    "triumph": [r"\bwin\b", r"\bwon\b", r"lottery", r"success", r"passed (?:exam|test|interview|jee|gate|neet)", r"\bpassed\b(?! away)", r"cracked", r"promoted", r"celebrate", r"finally"],
    "joy": [r"happy", r"joy", r"yay", r"glad", r"excited", r"awesome", r"lottery"],
    "despair": [r"rejected", r"broke", r"hopeless", r"over", r"crying", r"sad", r"loss", r"passed away", r"died"],
    "sadness": [r"sad", r"depressed", r"grief", r"unhappy", r"mourn", r"passed away", r"miss"],
    "anger": [r"angry", r"furious", r"unacceptable", r"mad", r"rage"],
    "neutral": [r"weather", r"degrees", r"today", r"temperature", r"factual"],
    "humor": [r"lol", r"joke", r"funny", r"haha", r"lmao", r"roast"],
}


def detect_emotion(text: str) -> dict:
    t_lower = text.lower()
    scores = {}
    for emotion, patterns in EMOTION_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, t_lower))
        if count > 0:
            scores[emotion] = count

    if not scores:
        return {"primary": "humor", "confidence": 0.60, "all": {"humor": 0.60}}

    top_emotion = max(scores, key=scores.get)
    max_score = scores[top_emotion]
    confidence = min(0.65 + (max_score * 0.1), 0.95)

    return {
        "primary": top_emotion,
        "confidence": round(confidence, 2),
        "all": {k: round(v / sum(scores.values()), 2) for k, v in scores.items()},
    }

