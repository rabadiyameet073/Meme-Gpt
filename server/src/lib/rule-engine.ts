export interface RuleMatch {
  tags: string[];
  categories: string[];
  scores: Record<string, number>;
}

interface RulePattern {
  tag: string;
  category: string;
  patterns: RegExp[];
  weight: number;
}

const RULES: RulePattern[] = [
  {
    tag: "success",
    category: "success",
    patterns: [/achiev/i, /promot/i, /pass(?:ed)?/i, /won/i, /crack(?:ed)?/i, /selected/i, /offer letter/i, /celebrat/i],
    weight: 1,
  },
  {
    tag: "failure",
    category: "failure",
    patterns: [/fail(?:ed|ure)?/i, /reject/i, /flunk/i, /disappoint/i, /ruin/i, /disaster/i, /worst/i, /only \d+%/i],
    weight: 1,
  },
  {
    tag: "coding",
    category: "coding",
    patterns: [/bug/i, /code/i, /deploy/i, /git/i, /merge conflict/i, /stack overflow/i, /api/i, /database/i, /compile/i, /runtime/i, /typescript/i, /python/i, /javascript/i],
    weight: 1,
  },
  {
    tag: "startup",
    category: "startup",
    patterns: [/startup/i, /funding/i, /investor/i, /pitch/i, /mvp/i, /burn rate/i, /runway/i, /cofounder/i, /unicorn/i],
    weight: 1,
  },
  {
    tag: "relationship",
    category: "relationship",
    patterns: [/girlfriend/i, /boyfriend/i, /crush/i, /breakup/i, /dating/i, /marriage/i, /friendzone/i, /relationship/i, /ghost/i],
    weight: 1,
  },
  {
    tag: "exam",
    category: "exam",
    patterns: [/exam/i, /test/i, /jee/i, /neet/i, /gate/i, /upsc/i, /result/i, /marks/i, /rank/i, /stud(?:y|ying)/i],
    weight: 1,
  },
  {
    tag: "college",
    category: "college",
    patterns: [/college/i, /hostel/i, /professor/i, /assignment/i, /attendance/i, /campus/i, /semester/i, /backlog/i],
    weight: 1,
  },
  {
    tag: "job",
    category: "office",
    patterns: [/job/i, /salary/i, /boss/i, /manager/i, /meeting/i, /deadline/i, /client/i, /office/i, /hr/i, /interview/i, /layoff/i],
    weight: 1,
  },
  {
    tag: "motivation",
    category: "motivation",
    patterns: [/motivat/i, /inspir/i, /never give up/i, /hustle/i, /grind/i, /hard work/i, /believe/i],
    weight: 0.8,
  },
  {
    tag: "unrealistic_expectation",
    category: "unrealistic_goals",
    patterns: [/100%/i, /perfect/i, /impossible/i, /overnight/i, /tomorrow/i, /asap/i, /make it \d+/i, /can you make/i, /unrealistic/i, /magic/i],
    weight: 1.2,
  },
  {
    tag: "funny",
    category: "funny",
    patterns: [/funny/i, /lol/i, /hilarious/i, /embarrass/i, /awkward/i, /drunk/i, /meme/i, /roast/i],
    weight: 0.7,
  },
  {
    tag: "ai",
    category: "ai",
    patterns: [/ai\b/i, /chatgpt/i, /machine learning/i, /llm/i, /neural/i, /model/i, /accuracy/i, /training/i, /gpt/i],
    weight: 1,
  },
  {
    tag: "business",
    category: "business",
    patterns: [/business/i, /profit/i, /revenue/i, /sales/i, /customer/i, /market/i, /competition/i],
    weight: 0.9,
  },
  {
    tag: "gaming",
    category: "gaming",
    patterns: [/game/i, /gaming/i, /pubg/i, /bgmi/i, /valorant/i, /rank/i, /noob/i, /pro player/i, /lag/i],
    weight: 0.9,
  },
  {
    tag: "bollywood",
    category: "bollywood",
    patterns: [/bollywood/i, /movie/i, /dialogue/i, /srk/i, /salman/i, /amir/i, /film/i],
    weight: 0.6,
  },
  {
    tag: "youtube",
    category: "youtube",
    patterns: [/youtube/i, /vlog/i, /subscriber/i, /carryminati/i, /stream/i, /content creator/i],
    weight: 0.6,
  },
  {
    tag: "hypocrisy",
    category: "funny",
    patterns: [/double standard/i, /hypocri/i, /doglapan/i, /fake/i, /pretend/i],
    weight: 1,
  },
  {
    tag: "overconfidence",
    category: "funny",
    patterns: [/overconfident/i, /main character/i, /sigma/i, /attitude/i, /aukat/i],
    weight: 1,
  },
];

export function runRuleEngine(input: string): RuleMatch {
  const tags: string[] = [];
  const categories: string[] = [];
  const scores: Record<string, number> = {};

  for (const rule of RULES) {
    const matched = rule.patterns.some((p) => p.test(input));
    if (matched) {
      tags.push(rule.tag);
      if (!categories.includes(rule.category)) {
        categories.push(rule.category);
      }
      scores[rule.category] = (scores[rule.category] ?? 0) + rule.weight;
      scores[`tag:${rule.tag}`] = (scores[`tag:${rule.tag}`] ?? 0) + rule.weight;
    }
  }

  if (categories.length === 0) {
    categories.push("funny");
    tags.push("general");
    scores.funny = 0.3;
  }

  return { tags, categories, scores };
}
