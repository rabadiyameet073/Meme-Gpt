import type { MemeCategory, MemeData } from "../src/lib/types.js";

const INDIAN_MEMES: Omit<MemeData, "category">[] = [
  { name: "Aukat Me Reh", keywords: ["aukat", "impossible", "dream", "100%", "unrealistic"], dialogue: "Khwab To Dekho Magar Aukat Ke Hisab Se", explanation: "When someone expects more than what's realistically possible.", video: "https://www.youtube.com/watch?v=aukat-meme", gif: "aukat.gif" },
  { name: "Ye Sab Doglapan Hai", keywords: ["hypocrisy", "fake", "double standards", "doglapan"], dialogue: "Ye Sab Doglapan Hai", explanation: "Perfect for hypocritical expectations or double standards.", video: "https://www.youtube.com/watch?v=doglapan", gif: "doglapan.gif" },
  { name: "Khwab Dekho Raat Bhar", keywords: ["dream", "100% accuracy", "impossible", "overnight"], dialogue: "Khwab Dekho Raat Bhar", explanation: "When unrealistic expectations meet harsh reality.", video: "https://www.youtube.com/watch?v=khwab", gif: "khwab.gif" },
  { name: "Bhai Tu Toh Gaya", keywords: ["screwed", "dead", "finished", "problem"], dialogue: "Bhai Tu Toh Gaya", explanation: "When you're in deep trouble with no easy fix.", gif: "gaya.gif" },
  { name: "Thak Gaya Hu Bhai", keywords: ["tired", "exhausted", "burnout", "overwork"], dialogue: "Thak Gaya Hu Bhai", explanation: "Burnout from endless work or unrealistic demands.", gif: "thak.gif" },
  { name: "Itna Confidence Kahan Se Laata Hai", keywords: ["overconfident", "confidence", "delusion"], dialogue: "Itna Confidence Kahan Se Laata Hai", explanation: "When someone is absurdly overconfident about impossible tasks.", gif: "confidence.gif" },
  { name: "Samajh Gaya Sab", keywords: ["understand", "got it", "sarcasm"], dialogue: "Samajh Gaya Sab", explanation: "Sarcastic acknowledgment of a ridiculous situation.", gif: "samajh.gif" },
  { name: "Main Character Syndrome", keywords: ["main character", "delusion", "special"], dialogue: "Main Character Syndrome", explanation: "When someone acts like the world revolves around them.", gif: "mc.gif" },
  { name: "Sigma Male Grindset", keywords: ["sigma", "grind", "hustle", "motivation"], dialogue: "Sigma Male Grindset", explanation: "Over-the-top motivational grind culture satire.", gif: "sigma.gif" },
  { name: "Padhai Likhai Karo", keywords: ["study", "exam", "college", "parents"], dialogue: "Padhai Likhai Karo", explanation: "Classic parental advice when you're struggling.", gif: "padhai.gif" },
  { name: "Beta Tumse Na Ho Payega", keywords: ["can't do", "failure", "impossible"], dialogue: "Beta Tumse Na Ho Payega", explanation: "When the task is clearly beyond current capability.", video: "https://www.youtube.com/watch?v=gangs-of-wasseypur", gif: "naho.gif" },
  { name: "All Is Well", keywords: ["denial", "everything fine", "3 idiots"], dialogue: "All Is Well", explanation: "Denying problems while everything falls apart.", video: "https://www.youtube.com/watch?v=3idiots", gif: "alliswell.gif" },
  { name: "Bade Bade Deshon Mein", keywords: ["excuse", "big companies", "corporate"], dialogue: "Bade Bade Deshon Mein Aisi Chhoti Chhoti Baatein Hoti Rehti Hain", explanation: "Corporate excuse for absurd requests.", video: "https://www.youtube.com/watch?v=ddlj", gif: "bade.gif" },
  { name: "Mogambo Khush Hua", keywords: ["villain", "evil plan", "boss happy"], dialogue: "Mogambo Khush Hua", explanation: "When the boss/client is pleased with unreasonable demands.", gif: "mogambo.gif" },
  { name: "Rasode Mein Kaun Tha", keywords: ["drama", "gossip", "office politics"], dialogue: "Rasode Mein Kaun Tha", explanation: "Office drama and unnecessary investigations.", gif: "rasode.gif" },
  { name: "Kya Kar Raha Hai Tu", keywords: ["what are you doing", "confused", "mistake"], dialogue: "Kya Kar Raha Hai Tu", explanation: "Reacting to someone's questionable actions.", gif: "kya.gif" },
  { name: "Chal Be", keywords: ["get lost", "nonsense", "reject"], dialogue: "Chal Be", explanation: "Dismissal of absurd requests or ideas.", gif: "chalbe.gif" },
  { name: "Bhai Kya Kar Diya", keywords: ["messed up", "broke", "disaster"], dialogue: "Bhai Kya Kar Diya", explanation: "When someone broke production or failed badly.", gif: "kyakar.gif" },
  { name: "Maa Kasam", keywords: ["swear", "promise", "dramatic"], dialogue: "Maa Kasam", explanation: "Dramatic promise about fixing something impossible.", gif: "maakasam.gif" },
  { name: "Gazab Bebsi Hai", keywords: ["embarrassing", "cringe", "awkward"], dialogue: "Gazab Bebsi Hai", explanation: "Peak embarrassment moment.", gif: "bebsi.gif" },
];

const CODING_MEMES: Omit<MemeData, "category">[] = [
  { name: "It Works On My Machine", keywords: ["bug", "deploy", "works locally", "production"], dialogue: "It Works On My Machine", explanation: "Classic developer excuse when code fails in production.", gif: "machine.gif" },
  { name: "Stack Overflow Copy Paste", keywords: ["stackoverflow", "copy paste", "code", "borrowed"], dialogue: "Ctrl+C Ctrl+V From Stack Overflow", explanation: "When your entire solution is borrowed code.", gif: "stackoverflow.gif" },
  { name: "Merge Conflict Hell", keywords: ["merge conflict", "git", "branch"], dialogue: "Merge Conflict Hell", explanation: "Git merge conflicts destroying your day.", gif: "merge.gif" },
  { name: "One Semicolon Bug", keywords: ["semicolon", "syntax", "bug", "hours"], dialogue: "Spent 6 Hours On A Missing Semicolon", explanation: "Tiny syntax error, massive time waste.", gif: "semicolon.gif" },
  { name: "Production Is Down", keywords: ["production", "down", "outage", "panic"], dialogue: "Production Is Down And It's My Code", explanation: "The moment of terror when prod breaks.", gif: "prod.gif" },
  { name: "Legacy Code Archaeology", keywords: ["legacy", "old code", "spaghetti", "maintain"], dialogue: "Digging Through Legacy Code Like An Archaeologist", explanation: "Maintaining ancient undocumented code.", gif: "legacy.gif" },
  { name: "Rubber Duck Debugging", keywords: ["debug", "stuck", "explain"], dialogue: "Explaining Bug To Rubber Duck At 3 AM", explanation: "Desperate late-night debugging sessions.", gif: "duck.gif" },
  { name: "99 Bugs In The Code", keywords: ["bugs", "fix", "more bugs"], dialogue: "99 Bugs In The Code, Fix One, 127 More Appear", explanation: "Fixing one bug creates ten more.", gif: "bugs.gif" },
  { name: "Deadline Tomorrow", keywords: ["deadline", "tomorrow", "client", "rush"], dialogue: "Client Wants It Tomorrow", explanation: "Impossible deadline from client.", gif: "deadline.gif" },
  { name: "AI Will Replace Us", keywords: ["ai", "chatgpt", "replace", "job"], dialogue: "ChatGPT Wrote Better Code Than Me", explanation: "AI outperforming your coding skills.", gif: "ai-code.gif" },
];

const STARTUP_MEMES: Omit<MemeData, "category">[] = [
  { name: "We Are Like A Family", keywords: ["startup", "family", "toxic", "hr"], dialogue: "We Are Like A Family Here (No Salary Raise)", explanation: "Toxic startup culture masking low pay.", gif: "family.gif" },
  { name: "Pivot Again", keywords: ["pivot", "startup", "idea", "change"], dialogue: "Time To Pivot Again", explanation: "Constantly changing startup direction.", gif: "pivot.gif" },
  { name: "Runway Ending", keywords: ["runway", "funding", "burn rate", "money"], dialogue: "Runway Ending In 2 Weeks", explanation: "Startup running out of money.", gif: "runway.gif" },
  { name: "Unicorn Dreams", keywords: ["unicorn", "valuation", "dream"], dialogue: "We Will Be Unicorn In 6 Months", explanation: "Unrealistic unicorn expectations.", gif: "unicorn.gif" },
  { name: "Equity Instead Of Salary", keywords: ["equity", "salary", "exposure"], dialogue: "Take Equity Instead Of Salary", explanation: "Getting paid in dreams and equity.", gif: "equity.gif" },
  { name: "Pitch Deck Perfection", keywords: ["pitch", "investor", "deck", "slides"], dialogue: "100 Slides But No Revenue", explanation: "Beautiful pitch deck, zero traction.", gif: "pitch.gif" },
];

const RELATIONSHIP_MEMES: Omit<MemeData, "category">[] = [
  { name: "Friendzone Level Max", keywords: ["friendzone", "crush", "reject"], dialogue: "Friendzone Level: Legendary", explanation: "Getting permanently friendzoned.", gif: "friendzone.gif" },
  { name: "Seen But No Reply", keywords: ["ghost", "seen", "message", "ignore"], dialogue: "Seen At 2 AM, No Reply", explanation: "Being left on read.", gif: "seen.gif" },
  { name: "Red Flag Parade", keywords: ["red flag", "toxic", "relationship"], dialogue: "Red Flag Parade", explanation: "Ignoring obvious relationship red flags.", gif: "redflag.gif" },
  { name: "Ex Posted Story", keywords: ["ex", "breakup", "social media"], dialogue: "Ex Posted A Happy Story", explanation: "Ex seems happy while you're suffering.", gif: "ex.gif" },
  { name: "Situationship", keywords: ["situationship", "confused", "dating"], dialogue: "Situationship Loading...", explanation: "Undefined romantic situation.", gif: "situationship.gif" },
];

const COLLEGE_MEMES: Omit<MemeData, "category">[] = [
  { name: "Backlog Mountain", keywords: ["backlog", "failed", "supplementary"], dialogue: "Backlog Mountain Growing", explanation: "Accumulating failed subjects.", gif: "backlog.gif" },
  { name: "Attendance Short", keywords: ["attendance", "short", "professor"], dialogue: "Attendance Short By 1%", explanation: "Missing attendance by tiny margin.", gif: "attendance.gif" },
  { name: "Assignment Night Before", keywords: ["assignment", "last minute", "deadline"], dialogue: "Assignment Due Tomorrow, Starting Now", explanation: "Procrastination until last moment.", gif: "assignment.gif" },
  { name: "Hostel Maggi Life", keywords: ["hostel", "maggi", "broke", "student"], dialogue: "Hostel Maggi For Dinner Again", explanation: "Broke student hostel life.", gif: "maggi.gif" },
  { name: "Proxy Attendance", keywords: ["proxy", "attendance", "friend"], dialogue: "Proxy Attendance Request Sent", explanation: "Classic college proxy attendance.", gif: "proxy.gif" },
];

const OFFICE_MEMES: Omit<MemeData, "category">[] = [
  { name: "This Meeting Could Be Email", keywords: ["meeting", "email", "waste time"], dialogue: "This Meeting Could Have Been An Email", explanation: "Unnecessary long meetings.", gif: "meeting.gif" },
  { name: "Boss Is Watching", keywords: ["boss", "watching", "pressure"], dialogue: "Boss Is Watching", explanation: "Pressure when manager is monitoring.", gif: "boss.gif" },
  { name: "Reply All Disaster", keywords: ["reply all", "email", "embarrass"], dialogue: "Accidentally Replied All", explanation: "Email disaster with reply all.", gif: "replyall.gif" },
  { name: "Friday Deployment", keywords: ["deploy", "friday", "risk"], dialogue: "Deploying On Friday Like A Hero", explanation: "Risky Friday deployment.", gif: "friday.gif" },
  { name: "HR Wants To Talk", keywords: ["hr", "talk", "fired", "scared"], dialogue: "HR Wants To Talk", explanation: "The dreaded HR meeting message.", gif: "hr.gif" },
];

const EXAM_MEMES: Omit<MemeData, "category">[] = [
  { name: "JEE Advanced Trauma", keywords: ["jee", "exam", "trauma", "rank"], dialogue: "JEE Advanced Trauma Activated", explanation: "Competitive exam pressure.", gif: "jee.gif" },
  { name: "One Night Syllabus", keywords: ["exam tomorrow", "syllabus", "panic"], dialogue: "Exam Tomorrow, Syllabus Untouched", explanation: "Last night exam preparation panic.", gif: "syllabus.gif" },
  { name: "Relative Asking Marks", keywords: ["marks", "relatives", "result"], dialogue: "Relative Asking Marks At Family Function", explanation: "Indian relatives asking about exam results.", gif: "marks.gif" },
  { name: "Neet Dropper", keywords: ["neet", "drop", "year", "retry"], dialogue: "Neet Drop Year 3", explanation: "Multiple attempts at competitive exams.", gif: "neet.gif" },
];

const GAMING_MEMES: Omit<MemeData, "category">[] = [
  { name: "Lag Spike During Clutch", keywords: ["lag", "gaming", "clutch", "rank"], dialogue: "Lag Spike During Clutch Moment", explanation: "Internet lag at worst moment.", gif: "lag.gif" },
  { name: "Noob Team", keywords: ["noob", "team", "rank", "carry"], dialogue: "Carrying Noob Team Again", explanation: "Matched with bad teammates.", gif: "noob.gif" },
  { name: "One More Game", keywords: ["one more", "addiction", "gaming", "sleep"], dialogue: "One More Game At 4 AM", explanation: "Gaming addiction keeping you up.", gif: "onemore.gif" },
  { name: "BGMI Chicken Dinner", keywords: ["bgmi", "pubg", "chicken dinner", "win"], dialogue: "Finally Chicken Dinner", explanation: "Victory after many tries.", gif: "chicken.gif" },
];

const AI_MEMES: Omit<MemeData, "category">[] = [
  { name: "12% Accuracy Fix", keywords: ["accuracy", "12%", "100%", "model", "ml"], dialogue: "12% Accuracy To 100% By Tomorrow?", explanation: "Unrealistic ML model improvement expectations.", gif: "accuracy.gif" },
  { name: "ChatGPT Wrote My Thesis", keywords: ["chatgpt", "thesis", "ai", "cheat"], dialogue: "ChatGPT Wrote My Entire Thesis", explanation: "Over-relying on AI for work.", gif: "thesis.gif" },
  { name: "Hallucination Nation", keywords: ["hallucination", "llm", "wrong", "ai"], dialogue: "AI Hallucinated The Entire Answer", explanation: "AI making up false information.", gif: "hallucination.gif" },
  { name: "Prompt Engineer", keywords: ["prompt", "engineer", "job", "ai"], dialogue: "Prompt Engineer By Day, Unemployed By Night", explanation: "Satire on prompt engineering hype.", gif: "prompt.gif" },
];

const MOTIVATION_MEMES: Omit<MemeData, "category">[] = [
  { name: "Rise And Grind", keywords: ["grind", "hustle", "5am", "motivation"], dialogue: "Rise And Grind At 5 AM", explanation: "Toxic productivity culture.", gif: "grind.gif" },
  { name: "Pain Is Weakness", keywords: ["pain", "weakness", "gym", "motivation"], dialogue: "Pain Is Weakness Leaving Body", explanation: "Over-the-top motivational quote.", gif: "pain.gif" },
  { name: "Manifesting Success", keywords: ["manifest", "law of attraction", "success"], dialogue: "Manifesting Success Without Working", explanation: "Manifestation without action.", gif: "manifest.gif" },
];

const BUSINESS_MEMES: Omit<MemeData, "category">[] = [
  { name: "Synergy Buzzword", keywords: ["synergy", "corporate", "buzzword"], dialogue: "We Need More Synergy", explanation: "Corporate buzzword overload.", gif: "synergy.gif" },
  { name: "Q4 Target", keywords: ["target", "sales", "q4", "pressure"], dialogue: "Q4 Target Is Impossible", explanation: "Unrealistic sales targets.", gif: "q4.gif" },
  { name: "Competitor Did What", keywords: ["competitor", "market", "panic"], dialogue: "Competitor Did What Now?", explanation: "Competitor shock.", gif: "competitor.gif" },
];

const YOUTUBE_MEMES: Omit<MemeData, "category">[] = [
  { name: "Like Share Subscribe", keywords: ["youtube", "subscribe", "content"], dialogue: "Like Share Subscribe Or Else", explanation: "YouTuber call to action satire.", gif: "subscribe.gif" },
  { name: "Thumbnail Face", keywords: ["thumbnail", "clickbait", "youtube"], dialogue: "Shocked Face In Thumbnail", explanation: "Clickbait YouTube thumbnails.", gif: "thumbnail.gif" },
  { name: "Ad Before Video", keywords: ["ad", "skip", "youtube", "annoying"], dialogue: "Two Unskippable Ads", explanation: "YouTube ad frustration.", gif: "ads.gif" },
];

const BOLlywood_MEMES: Omit<MemeData, "category">[] = [
  { name: "Don Ko Pakadna Mushkil", keywords: ["don", "catch", "impossible", "bollywood"], dialogue: "Don Ko Pakadna Mushkil Hi Nahi Namumkin Hai", explanation: "Impossible task Bollywood style.", video: "https://www.youtube.com/watch?v=don", gif: "don.gif" },
  { name: "Picture Abhi Baaki Hai", keywords: ["not over", "twist", "bollywood"], dialogue: "Picture Abhi Baaki Hai Mere Dost", explanation: "When there's more drama coming.", gif: "picture.gif" },
  { name: "Kitne Aadmi The", keywords: ["question", "interrogation", "sholay"], dialogue: "Kitne Aadmi The?", explanation: "Classic interrogation dialogue.", video: "https://www.youtube.com/watch?v=sholay", gif: "aadmi.gif" },
];

const CATEGORY_TEMPLATES: { category: MemeCategory; memes: Omit<MemeData, "category">[] }[] = [
  { category: "unrealistic_goals", memes: INDIAN_MEMES.filter((m) => m.keywords.some((k) => ["impossible", "100%", "dream", "unrealistic", "aukat"].includes(k))) },
  { category: "funny", memes: INDIAN_MEMES },
  { category: "coding", memes: CODING_MEMES },
  { category: "startup", memes: STARTUP_MEMES },
  { category: "relationship", memes: RELATIONSHIP_MEMES },
  { category: "college", memes: COLLEGE_MEMES },
  { category: "office", memes: OFFICE_MEMES },
  { category: "exam", memes: EXAM_MEMES },
  { category: "gaming", memes: GAMING_MEMES },
  { category: "ai", memes: AI_MEMES },
  { category: "motivation", memes: MOTIVATION_MEMES },
  { category: "business", memes: BUSINESS_MEMES },
  { category: "youtube", memes: YOUTUBE_MEMES },
  { category: "bollywood", memes: BOLlywood_MEMES },
  { category: "failure", memes: [...INDIAN_MEMES, ...CODING_MEMES].filter((m) => m.keywords.some((k) => ["fail", "disaster", "broke", "messed"].some((f) => k.includes(f)))) },
  { category: "success", memes: INDIAN_MEMES.filter((m) => m.name.includes("Well") || m.keywords.includes("win")) },
];

const VARIATIONS = [
  "Classic", "Deluxe", "Ultra", "Pro Max", "2024 Edition", "Remix", "Reloaded",
  "OG", "Desi", "Elite", "Supreme", "Turbo", "Mega", "Mini", "Plus",
  "V2", "V3", "Final", "Ultimate", "HD", "4K", "Uncut", "Director's Cut",
];

const SITUATION_SUFFIXES = [
  "at 3 AM", "during meeting", "before deadline", "after result",
  "in hostel", "in startup", "during interview", "on Monday",
  "after breakup", "before exam", "in production", "on Friday",
];

function uniqueMemes(): MemeData[] {
  const seen = new Set<string>();
  const result: MemeData[] = [];

  const add = (meme: MemeData) => {
    const key = meme.name.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      result.push(meme);
    }
  };

  for (const group of CATEGORY_TEMPLATES) {
    for (const base of group.memes) {
      add({
        ...base,
        category: group.category,
        viralScore: 50 + Math.random() * 50,
      });
    }
  }

  // Generate variations to reach 500+
  for (const group of CATEGORY_TEMPLATES) {
    for (const base of group.memes) {
      for (const variation of VARIATIONS) {
        for (const suffix of SITUATION_SUFFIXES.slice(0, 3)) {
          const name = `${base.name} — ${variation}`;
          if (seen.has(name.toLowerCase())) continue;

          add({
            name,
            category: group.category,
            keywords: [...base.keywords, variation.toLowerCase(), ...suffix.split(" ")],
            dialogue: `${base.dialogue} (${suffix})`,
            explanation: `${base.explanation} Especially relatable ${suffix}.`,
            video: base.video,
            gif: base.gif,
            viralScore: 30 + Math.random() * 70,
          });

          if (result.length >= 520) return result;
        }
      }
    }
  }

  return result;
}

export const MEME_DATASET: MemeData[] = uniqueMemes();

export function getMemeCount(): number {
  return MEME_DATASET.length;
}
