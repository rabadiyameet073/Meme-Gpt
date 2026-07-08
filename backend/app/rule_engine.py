import re
from dataclasses import dataclass, field


@dataclass
class RuleMatch:
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


RULES = [
    ("success", "success", [r"achiev", r"promot", r"pass(?:ed)?", r"won", r"crack(?:ed)?", r"selected", r"offer letter", r"celebrat"], 1.0),
    ("failure", "failure", [r"fail(?:ed|ure)?", r"reject", r"flunk", r"disappoint", r"ruin", r"disaster", r"worst", r"only \d+%"], 1.0),
    ("coding", "coding", [r"bug", r"code", r"deploy", r"git", r"merge conflict", r"stack overflow", r"api", r"database", r"compile", r"runtime", r"typescript", r"python", r"javascript"], 1.0),
    ("startup", "startup", [r"startup", r"funding", r"investor", r"pitch", r"mvp", r"burn rate", r"runway", r"cofounder", r"unicorn"], 1.0),
    ("relationship", "relationship", [r"girlfriend", r"boyfriend", r"crush", r"breakup", r"dating", r"marriage", r"friendzone", r"relationship", r"ghost"], 1.0),
    ("exam", "exam", [r"exam", r"test", r"jee", r"neet", r"gate", r"upsc", r"result", r"marks", r"rank", r"stud(?:y|ying)"], 1.0),
    ("college", "college", [r"college", r"hostel", r"professor", r"assignment", r"attendance", r"campus", r"semester", r"backlog"], 1.0),
    ("job", "office", [r"job", r"salary", r"boss", r"manager", r"meeting", r"deadline", r"client", r"office", r"hr", r"interview", r"layoff"], 1.0),
    ("motivation", "motivation", [r"motivat", r"inspir", r"never give up", r"hustle", r"grind", r"hard work", r"believe"], 0.8),
    ("unrealistic_expectation", "unrealistic_goals", [r"100%", r"perfect", r"impossible", r"overnight", r"tomorrow", r"asap", r"make it \d+", r"can you make", r"unrealistic", r"magic"], 1.2),
    ("funny", "funny", [r"funny", r"lol", r"hilarious", r"embarrass", r"awkward", r"drunk", r"meme", r"roast"], 0.7),
    ("ai", "ai", [r"ai\b", r"chatgpt", r"machine learning", r"llm", r"neural", r"model", r"accuracy", r"training", r"gpt"], 1.0),
    ("business", "business", [r"business", r"profit", r"revenue", r"sales", r"customer", r"market", r"competition"], 0.9),
    ("gaming", "gaming", [r"game", r"gaming", r"pubg", r"bgmi", r"valorant", r"rank", r"noob", r"pro player", r"lag"], 0.9),
    ("bollywood", "bollywood", [r"bollywood", r"movie", r"dialogue", r"srk", r"salman", r"amir", r"film"], 0.6),
    ("youtube", "youtube", [r"youtube", r"vlog", r"subscriber", r"carryminati", r"stream", r"content creator"], 0.6),
    ("hypocrisy", "funny", [r"double standard", r"hypocri", r"doglapan", r"fake", r"pretend"], 1.0),
    ("overconfidence", "funny", [r"overconfident", r"main character", r"sigma", r"attitude", r"aukat"], 1.0),
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
