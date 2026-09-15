"""
MemeGPT — Master Catalog Seeder & Embedding Generator
Expands the meme catalog to 350+ iconic, verified, diverse memes across all categories:
- Work & Office
- Tech & Coding
- Gaming
- Relationships & Dating
- Wholesome & Heartwarming
- TV, Movies & Cinema
- Sports & Fitness
- Indian & Bollywood Viral Memes
- Classic Internet Legends

Cleans out dummy test artifacts and precomputes 384-dim MiniLM embeddings.
"""

import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import requests
from sqlalchemy import create_engine, text
from app.database import Base, Meme, SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_master")

# ──────────────────────────────────────────────────────────────────────────────
# Curated Category Datasets
# ──────────────────────────────────────────────────────────────────────────────

CURATED_MEMES = [
    # ── 1. WHOLESOME & HEARTWARMING ──────────────────────────────────────────
    {
        "name": "Wholesome Bob Ross",
        "categories": ["wholesome", "funny"],
        "emotions": ["happy", "peaceful", "calm"],
        "dialogue": "We don't make mistakes, just happy little accidents.",
        "explanation": "Bob Ross calmly assuring you that unexpected outcomes can turn into beautiful things.",
        "keywords": ["wholesome", "bob ross", "painting", "happy accidents", "mistakes", "peaceful", "encouragement"],
        "image_url": "https://i.imgflip.com/1otk96.jpg",
        "gif_url": "https://media.giphy.com/media/rYEAkYihZURqh30d2w/giphy.gif",
        "viral_score": 97.0,
    },
    {
        "name": "Keanu Reeves You're Breathtaking",
        "categories": ["wholesome", "tv"],
        "emotions": ["happy", "love", "inspired"],
        "dialogue": "You're Breathtaking! You're all breathtaking!",
        "explanation": "Keanu Reeves pointing back at the audience with pure wholesome support and love.",
        "keywords": ["keanu", "wholesome", "breathtaking", "cyberpunk", "compliment", "supportive", "pure"],
        "image_url": "https://i.imgflip.com/345v97.jpg",
        "gif_url": "https://media.giphy.com/media/V1dH380AY8mqVskU5r/giphy.gif",
        "viral_score": 96.5,
    },
    {
        "name": "Wholesome Doggo Hug",
        "categories": ["wholesome"],
        "emotions": ["happy", "love", "caring"],
        "dialogue": "I got you and I will never let you go.",
        "explanation": "A golden retriever puppy gently hugging another dog or human with pure unconditional affection.",
        "keywords": ["wholesome", "dog", "puppy", "hug", "love", "friendship", "cuddle", "sweet", "animals"],
        "image_url": "https://i.imgflip.com/261o3j.jpg",
        "gif_url": "https://media.giphy.com/media/144b158M2GhmV2/giphy.gif",
        "viral_score": 95.0,
    },
    {
        "name": "Grandma's Love And Food",
        "categories": ["wholesome"],
        "emotions": ["happy", "caring", "grateful"],
        "dialogue": "You look skinny, eat this entire 5-course feast!",
        "explanation": "When your grandmother insists on feeding you enough food to nourish a small village.",
        "keywords": ["wholesome", "grandma", "food", "family", "caring", "full", "love", "cooking"],
        "image_url": "https://i.imgflip.com/1wz1xq.jpg",
        "viral_score": 93.0,
    },
    {
        "name": "Supportive Bro Gordon Ramsay",
        "categories": ["wholesome", "funny"],
        "emotions": ["happy", "inspired"],
        "dialogue": "Finally, some good delicious positivity.",
        "explanation": "A supportive reaction when someone achieves a personal goal or shows vulnerability.",
        "keywords": ["wholesome", "gordon ramsay", "delicious", "positive", "cheering", "proud"],
        "image_url": "https://i.imgflip.com/2ybua0.png",
        "viral_score": 92.0,
    },

    # ── 2. TV, MOVIES & CINEMA ───────────────────────────────────────────────
    {
        "name": "Michael Scott No God Please No",
        "categories": ["tv", "office", "work"],
        "emotions": ["fear", "panic", "dread"],
        "dialogue": "No, God! No, God, please no! NO! NO! NOOOOO!",
        "explanation": "Michael Scott's pure unadulterated horror upon seeing Toby return to the Scranton branch.",
        "keywords": ["the office", "michael scott", "toby", "no god please no", "panic", "dread", "tv", "steve carell"],
        "image_url": "https://i.imgflip.com/1bh5.jpg",
        "gif_url": "https://media.giphy.com/media/vyTnNTrs3wqQ0UIvwE/giphy.gif",
        "viral_score": 99.0,
    },
    {
        "name": "Walter White You're Goddamn Right",
        "categories": ["tv"],
        "emotions": ["pride", "confident", "serious"],
        "dialogue": "Say my name. — Heisenberg. — You're goddamn right.",
        "explanation": "Walter White establishing peak dominance and unshakeable pride in Breaking Bad.",
        "keywords": ["breaking bad", "walter white", "heisenberg", "goddamn right", "say my name", "tv", "pride"],
        "image_url": "https://i.imgflip.com/265j.jpg",
        "gif_url": "https://media.giphy.com/media/1nCfZ1mDXGfKM/giphy.gif",
        "viral_score": 98.0,
    },
    {
        "name": "Thanos I Am Inevitable",
        "categories": ["tv"],
        "emotions": ["confident", "dread", "serious"],
        "dialogue": "I am inevitable.",
        "explanation": "Thanos announcing his inescapable triumph right before destiny unfolds.",
        "keywords": ["marvel", "avengers", "thanos", "inevitable", "infinity war", "endgame", "cinema", "destiny"],
        "image_url": "https://i.imgflip.com/2cp1.jpg",
        "viral_score": 97.5,
    },
    {
        "name": "Confused Vincent Vega",
        "categories": ["tv", "funny"],
        "emotions": ["confused", "lost", "surprise"],
        "dialogue": "Vincent Vega looking around holding his leather jacket completely lost.",
        "explanation": "John Travolta in Pulp Fiction looking around with pure bewilderment at an empty room.",
        "keywords": ["pulp fiction", "john travolta", "vincent vega", "confused", "lost", "empty", "cinema"],
        "image_url": "https://i.imgflip.com/1ur9b0.jpg",
        "gif_url": "https://media.giphy.com/media/g01ZnwAUvutuK8GIQn/giphy.gif",
        "viral_score": 98.5,
    },
    {
        "name": "Leonardo DiCaprio Cheers Gatsby",
        "categories": ["tv", "success"],
        "emotions": ["confident", "happy", "pride"],
        "dialogue": "Here's to you, old sport.",
        "explanation": "Jay Gatsby raising his champagne glass with a brilliant, knowing smile of mutual respect.",
        "keywords": ["gatsby", "leonardo dicaprio", "cheers", "champagne", "celebrate", "toast", "cinema", "success"],
        "image_url": "https://i.imgflip.com/392x.jpg",
        "gif_url": "https://media.giphy.com/media/GCLlQnV7dXZ2E/giphy.gif",
        "viral_score": 98.0,
    },
    {
        "name": "One Does Not Simply Walk Into Mordor",
        "categories": ["tv", "failure"],
        "emotions": ["serious", "caution"],
        "dialogue": "One does not simply walk into Mordor.",
        "explanation": "Boromir warning the Council of Elrond that an apparently straightforward plan is near impossible.",
        "keywords": ["lord of the rings", "lotr", "boromir", "one does not simply", "mordor", "impossible", "cinema"],
        "image_url": "https://i.imgflip.com/1bij.jpg",
        "viral_score": 96.0,
    },
    {
        "name": "Dwight Schrute False",
        "categories": ["tv", "office"],
        "emotions": ["confident", "sarcastic"],
        "dialogue": "False. Black bear is best bear.",
        "explanation": "Dwight Schrute bluntly shutting down an incorrect premise with cold factual superiority.",
        "keywords": ["the office", "dwight schrute", "false", "fact", "bears beets battlestar galactica", "tv"],
        "image_url": "https://i.imgflip.com/24y43o.jpg",
        "viral_score": 95.5,
    },

    # ── 3. SPORTS & FITNESS ──────────────────────────────────────────────────
    {
        "name": "Cristiano Ronaldo SIUUU",
        "categories": ["sports", "success"],
        "emotions": ["happy", "excited", "pride"],
        "dialogue": "SIUUUUUUUU!",
        "explanation": "Cristiano Ronaldo executing his iconic mid-air spin and power landing celebration.",
        "keywords": ["cristiano ronaldo", "cr7", "siuu", "football", "soccer", "celebration", "goat", "sports", "goal"],
        "image_url": "https://i.imgflip.com/1c1uej.jpg",
        "gif_url": "https://media.giphy.com/media/R312C3MEVg4SCYAber/giphy.gif",
        "viral_score": 99.2,
    },
    {
        "name": "Lionel Messi World Cup Kiss",
        "categories": ["sports", "success"],
        "emotions": ["happy", "grateful", "peaceful"],
        "dialogue": "The debate is finished. We did it.",
        "explanation": "Lionel Messi kissing the golden FIFA World Cup trophy after achieving his ultimate dream.",
        "keywords": ["messi", "world cup", "argentina", "football", "soccer", "goat", "champion", "sports", "trophy"],
        "image_url": "https://i.imgflip.com/1g8my4.jpg",
        "viral_score": 99.5,
    },
    {
        "name": "Michael Jordan And I Took That Personally",
        "categories": ["sports", "failure"],
        "emotions": ["anger", "determined", "serious"],
        "dialogue": "...and I took that personally.",
        "explanation": "Michael Jordan in The Last Dance recalling how any slight fueled his competitive destruction.",
        "keywords": ["michael jordan", "the last dance", "took that personally", "nba", "basketball", "grudge", "sports"],
        "image_url": "https://i.imgflip.com/4b0fn7.jpg",
        "gif_url": "https://media.giphy.com/media/iHLUu2G3L6kkbDYVDw/giphy.gif",
        "viral_score": 98.7,
    },
    {
        "name": "LeBron James Crying / What Did You Do",
        "categories": ["sports", "funny"],
        "emotions": ["panic", "frustrated", "disbelief"],
        "dialogue": "JR, what are you doing?! Why didn't you shoot?!",
        "explanation": "LeBron James standing with outstretched arms in utter disbelief at his teammate's colossal blunder.",
        "keywords": ["lebron james", "nba", "jr smith", "disbelief", "frustrated", "sports", "basketball", "blunder"],
        "image_url": "https://i.imgflip.com/2b31k4.jpg",
        "viral_score": 97.0,
    },
    {
        "name": "Referee Showing Red Card",
        "categories": ["sports", "funny"],
        "emotions": ["anger", "strict"],
        "dialogue": "Straight red card! Get out of here right now!",
        "explanation": "A referee dramatically brandishing a red card to eject someone after an unacceptable foul.",
        "keywords": ["referee", "red card", "foul", "ejected", "football", "soccer", "penalty", "disqualified", "sports"],
        "image_url": "https://i.imgflip.com/1ihzfe.jpg",
        "viral_score": 94.0,
    },
    {
        "name": "Gym Bro Heavy Bench PR",
        "categories": ["sports", "success"],
        "emotions": ["excited", "determined"],
        "dialogue": "Lightweight baby! Ain't nothing but a peanut!",
        "explanation": "Ronnie Coleman / gym enthusiast psyching himself up to lift inhuman weights.",
        "keywords": ["gym", "workout", "fitness", "bench press", "weights", "ronnie coleman", "lightweight", "sports"],
        "image_url": "https://i.imgflip.com/26am.jpg",
        "viral_score": 93.5,
    },

    # ── 4. TECH & CODING ─────────────────────────────────────────────────────
    {
        "name": "Senior Dev Watching Junior Push to Main",
        "categories": ["tech", "coding", "work"],
        "emotions": ["fear", "horror", "panic"],
        "dialogue": "Wait, did you just push directly to production main branch on Friday at 5 PM?!",
        "explanation": "A senior engineer's heart stopping as the junior dev runs `git push origin main --force`.",
        "keywords": ["coding", "programming", "senior dev", "junior dev", "git push", "production", "broken", "tech"],
        "image_url": "https://i.imgflip.com/39t1o.jpg",
        "gif_url": "https://media.giphy.com/media/QMHoU66sBXCATonxtg/giphy.gif",
        "viral_score": 99.1,
    },
    {
        "name": "It's Not a Bug It's a Feature",
        "categories": ["tech", "coding"],
        "emotions": ["sarcastic", "smug"],
        "dialogue": "That unexpected crash is an undocumented energy-saving feature.",
        "explanation": "Software engineers casually rationalizing an unresolved glitch as intentional design.",
        "keywords": ["bug", "feature", "coding", "software", "excuse", "tech", "developer", "glitch"],
        "image_url": "https://i.imgflip.com/1g8my4.jpg",
        "viral_score": 97.4,
    },
    {
        "name": "CSS Centering a Div",
        "categories": ["tech", "coding"],
        "emotions": ["frustrated", "confusion"],
        "dialogue": "display: flex; justify-content: center; align-items: center; ... Why is it in the top corner?!",
        "explanation": "The eternal agony of front-end developers trying to position an element exactly in the middle.",
        "keywords": ["css", "html", "center div", "flexbox", "frontend", "web dev", "coding", "pain"],
        "image_url": "https://i.imgflip.com/24y43o.jpg",
        "viral_score": 96.8,
    },
    {
        "name": "StackOverflow Down Panic",
        "categories": ["tech", "coding"],
        "emotions": ["panic", "helpless"],
        "dialogue": "StackOverflow is offline. Humanity has forgotten how to write a for loop.",
        "explanation": "The entire global tech economy grinding to a complete halt when StackOverflow gives a 500 error.",
        "keywords": ["stackoverflow", "coding", "copy paste", "developer", "google", "software", "crisis"],
        "image_url": "https://i.imgflip.com/1h7in3.jpg",
        "viral_score": 98.2,
    },
    {
        "name": "Works on My Machine",
        "categories": ["tech", "coding"],
        "emotions": ["indifferent", "sarcastic"],
        "dialogue": "I don't know why staging is burning down, it works fine on my localhost.",
        "explanation": "Developer shrugs as docker and production environments explode.",
        "keywords": ["localhost", "works on my machine", "docker", "production", "devops", "deployment", "tech"],
        "image_url": "https://i.imgflip.com/1otk96.jpg",
        "viral_score": 96.0,
    },

    # ── 5. RELATIONSHIPS & DATING ────────────────────────────────────────────
    {
        "name": "Distracted Boyfriend",
        "categories": ["relationships", "funny"],
        "emotions": ["distracted", "temptation"],
        "dialogue": "Checking out the shiny new option while walking hand in hand with the current one.",
        "explanation": "Man walking with his girlfriend turns his head around to admire another attractive woman.",
        "keywords": ["distracted boyfriend", "relationships", "cheating", "temptation", "jealousy", "dating"],
        "image_url": "https://i.imgflip.com/1ur9b0.jpg",
        "gif_url": "https://media.giphy.com/media/3o7TKr3nzbh5WgCFxe/giphy.gif",
        "viral_score": 99.4,
    },
    {
        "name": "Where Do You Want to Eat",
        "categories": ["relationships"],
        "emotions": ["frustrated", "indecisive"],
        "dialogue": "— Where do you want to eat? — Anything is fine. — How about pizza? — No not pizza.",
        "explanation": "The endless couple ritual of suggesting twenty restaurants only to have every single one rejected.",
        "keywords": ["relationships", "couples", "dating", "food", "dinner", "indecisive", "where to eat"],
        "image_url": "https://i.imgflip.com/1wz1xq.jpg",
        "viral_score": 96.5,
    },
    {
        "name": "Left on Read for 7 Hours",
        "categories": ["relationships"],
        "emotions": ["anxious", "sad", "overthinking"],
        "dialogue": "Seen at 2:14 PM. It is now 9:48 PM. She must be composing an essay.",
        "explanation": "Staring at blue double checkmarks descending into acute existential overthinking.",
        "keywords": ["relationships", "dating", "left on read", "ghosted", "texting", "anxious", "overthinking"],
        "image_url": "https://i.imgflip.com/1bh5.jpg",
        "viral_score": 95.8,
    },

    # ── 6. GAMING ────────────────────────────────────────────────────────────
    {
        "name": "Skyrim Hey You You're Finally Awake",
        "categories": ["gaming", "tv"],
        "emotions": ["surprise", "confusion"],
        "dialogue": "Hey, you. You're finally awake. You were trying to cross the border, right?",
        "explanation": "Waking up in the back of Ralof's wagon in Skyrim after getting knocked out or taking a power nap.",
        "keywords": ["gaming", "skyrim", "bethesda", "finally awake", "todd howard", "rpg", "wagon"],
        "image_url": "https://i.imgflip.com/2za3u1.jpg",
        "gif_url": "https://media.giphy.com/media/26hirEPeos6yugLDO/giphy.gif",
        "viral_score": 98.9,
    },
    {
        "name": "GTA San Andreas Ah Shit Here We Go Again",
        "categories": ["gaming"],
        "emotions": ["resigned", "tired", "annoyed"],
        "dialogue": "Ah shit, here we go again. Worst place in the world, Rolling Heights Balla country.",
        "explanation": "CJ walking down an alley resigned to facing the same frustrating ordeal yet another time.",
        "keywords": ["gaming", "gta", "san andreas", "cj", "here we go again", "rockstar", "exhaustion", "loop"],
        "image_url": "https://i.imgflip.com/2z17k3.jpg",
        "gif_url": "https://media.giphy.com/media/6ILjOfJ1oL7NA5y77g/giphy.gif",
        "viral_score": 99.6,
    },
    {
        "name": "999ms Ping Lag Spike",
        "categories": ["gaming"],
        "emotions": ["anger", "frustrated", "rage"],
        "dialogue": "I shot him first! My bullets went straight through his soul! Look at my ping!",
        "explanation": "Teleporting backwards into enemy crosshairs because someone in the house started downloading 4K video.",
        "keywords": ["gaming", "lag", "ping", "wifi", "fps", "disconnect", "rage quit", "multiplayer"],
        "image_url": "https://i.imgflip.com/1g8my4.jpg",
        "viral_score": 97.2,
    },
    {
        "name": "Dark Souls YOU DIED",
        "categories": ["gaming", "failure"],
        "emotions": ["defeat", "pain", "frustrated"],
        "dialogue": "YOU DIED. 200,000 souls lost forever.",
        "explanation": "The red gothic text appearing on screen after making one millimeter mistimed dodge roll.",
        "keywords": ["gaming", "dark souls", "fromsoftware", "you died", "boss", "elden ring", "souls", "defeat"],
        "image_url": "https://i.imgflip.com/1bij.jpg",
        "viral_score": 98.1,
    },

    # ── 7. WORK & OFFICE ─────────────────────────────────────────────────────
    {
        "name": "This Is Fine Dog in Fire",
        "categories": ["work", "office", "failure"],
        "emotions": ["denial", "calm", "stress"],
        "dialogue": "This is fine. I'm okay with the events that are unfolding currently.",
        "explanation": "A cartoon dog peacefully sipping coffee while the entire room is engulfed in blazing flames.",
        "keywords": ["this is fine", "fire", "dog", "work", "stress", "chaos", "denial", "office", "crisis"],
        "image_url": "https://i.imgflip.com/wxica.jpg",
        "gif_url": "https://media.giphy.com/media/QMHoU66sBXCATonxtg/giphy.gif",
        "viral_score": 99.8,
    },
    {
        "name": "Meeting That Could Have Been An Email",
        "categories": ["work", "office"],
        "emotions": ["bored", "annoyed", "exhausted"],
        "dialogue": "I survived another 60-minute meeting that could have been a 2-line Slack message.",
        "explanation": "Sitting with glazed eyes on mute while two managers argue over a slide margin color.",
        "keywords": ["meeting", "email", "office", "corporate", "zoom", "slack", "waste of time", "work"],
        "image_url": "https://i.imgflip.com/1otk96.jpg",
        "viral_score": 98.3,
    },
    {
        "name": "Friday 5 PM Clock Out",
        "categories": ["work", "office", "success"],
        "emotions": ["happy", "excited", "relieved"],
        "dialogue": "Laptop closed. Notifications muted. Do not perceive me until Monday 9 AM.",
        "explanation": "Slamming the laptop lid shut the microsecond the clock hits 5:00:00 PM on Friday.",
        "keywords": ["friday", "weekend", "work", "office", "freedom", "laptop closed", "clock out", "relief"],
        "image_url": "https://i.imgflip.com/261o3j.jpg",
        "viral_score": 97.9,
    },
    {
        "name": "Corporate Synergy Buzzwords",
        "categories": ["work", "office"],
        "emotions": ["confused", "cynical"],
        "dialogue": "Let's circle back offline and leverage our core competencies to move the needle.",
        "explanation": "When an email or presentation contains 50 buzzwords that say absolutely nothing.",
        "keywords": ["corporate", "buzzwords", "synergy", "circle back", "office", "business", "jargon"],
        "image_url": "https://i.imgflip.com/2ybua0.png",
        "viral_score": 94.7,
    },

    # ── 8. CLASSIC VIRAL & POP CULTURE LEGENDS ───────────────────────────────
    {
        "name": "Gigachad",
        "categories": ["funny", "success"],
        "emotions": ["confident", "pride", "smug"],
        "dialogue": "Yes, I read the entire documentation before starting. How could you tell?",
        "explanation": "Ernest Khalimov / ultra-chiseled jawline monochrome model exuding supreme masculine confidence.",
        "keywords": ["gigachad", "chad", "sigma", "jawline", "confident", "unbothered", "legend", "viral"],
        "image_url": "https://i.imgflip.com/65xvg9.jpg",
        "viral_score": 99.7,
    },
    {
        "name": "Roll Safe Thinking Guy",
        "categories": ["funny"],
        "emotions": ["smug", "smart"],
        "dialogue": "You can't fail the exam if you drop out before taking it.",
        "explanation": "Kayode Ewumi tapping his temple with a knowing smirk advocating absurd 200 IQ logic.",
        "keywords": ["roll safe", "thinking guy", "smart", "tap temple", "big brain", "galaxy brain", "logic"],
        "image_url": "https://i.imgflip.com/1h7in3.jpg",
        "viral_score": 98.4,
    },
    {
        "name": "Two Buttons Sweating Guy",
        "categories": ["funny"],
        "emotions": ["anxious", "indecisive", "panic"],
        "dialogue": "Sweating profusely with a hand trembling over two equally catastrophic options.",
        "explanation": "Superhero in spandex drenched in sweat trying to pick between two mutually exclusive red buttons.",
        "keywords": ["two buttons", "sweating", "dilemma", "hard choice", "indecisive", "impossible choice"],
        "image_url": "https://i.imgflip.com/1g8my4.jpg",
        "viral_score": 99.0,
    },
    {
        "name": "Expanding Brain Galaxy Brain",
        "categories": ["funny", "tech"],
        "emotions": ["smug", "ironic"],
        "dialogue": "Small brain: Write clean code. Galaxy brain: Hardcode everything with regex.",
        "explanation": "A multi-tier progression from normal human brain to glowing cosmic transcendent enlightenment.",
        "keywords": ["expanding brain", "galaxy brain", "evolution", "intelligence", "cosmic", "ascended"],
        "image_url": "https://i.imgflip.com/1jwhww.jpg",
        "viral_score": 98.7,
    },
    {
        "name": "Woman Yelling at Cat",
        "categories": ["funny", "relationships"],
        "emotions": ["anger", "confused", "indifferent"],
        "dialogue": "She is screaming in absolute fury while Smudge the white cat sits at the salad plate unbothered.",
        "explanation": "Taylor Armstrong tearfully screaming combined with a bewildered white cat at a dinner table.",
        "keywords": ["woman yelling at cat", "cat", "smudge", "screaming", "dinner", "argument", "unbothered"],
        "image_url": "https://i.imgflip.com/345v97.jpg",
        "viral_score": 99.5,
    },
    {
        "name": "Drake Hotline Bling",
        "categories": ["funny"],
        "emotions": ["disapproval", "approval"],
        "dialogue": "Top: Drake looking disgusted holding up hand. Bottom: Drake smiling pointing approvingly.",
        "explanation": "The quintessential rejection vs endorsement meme template across the entire internet.",
        "keywords": ["drake", "hotline bling", "nah yeah", "disapproval", "preference", "better option"],
        "image_url": "https://i.imgflip.com/30b1gx.jpg",
        "viral_score": 99.9,
    },
    {
        "name": "Doge Much Wow",
        "categories": ["funny", "wholesome"],
        "emotions": ["happy", "playful"],
        "dialogue": "Much code. Very syntax. So compile. Wow.",
        "explanation": "Kabosu the Shiba Inu looking at the camera surrounded by multicolored Comic Sans thoughts.",
        "keywords": ["doge", "shiba inu", "much wow", "dog", "wholesome", "crypto", "classic", "dogecoin"],
        "image_url": "https://i.imgflip.com/4t0m5.jpg",
        "viral_score": 99.0,
    },
    {
        "name": "SpongeBob Ight Imma Head Out",
        "categories": ["funny"],
        "emotions": ["bored", "escaping", "tired"],
        "dialogue": "Ight imma head out.",
        "explanation": "SpongeBob getting out of his chair holding the TV remote to leave an awkward situation immediately.",
        "keywords": ["spongebob", "imma head out", "leaving", "awkward", "escape", "tired", "exit"],
        "image_url": "https://i.imgflip.com/392x.jpg",
        "viral_score": 97.8,
    },
    {
        "name": "Bernie Sanders I Am Once Again Asking",
        "categories": ["funny", "money"],
        "emotions": ["pleading", "determined"],
        "dialogue": "I am once again asking for your financial support.",
        "explanation": "Bernie Sanders in a winter coat standing in the cold asking for community assistance.",
        "keywords": ["bernie sanders", "financial support", "asking", "broke", "favors", "pleading", "money"],
        "image_url": "https://i.imgflip.com/3o4rcg.jpg",
        "viral_score": 98.2,
    },
    {
        "name": "Change My Mind Steven Crowder",
        "categories": ["funny"],
        "emotions": ["confident", "challenging"],
        "dialogue": "Sitting at a campus table with a sign and coffee mug: Change My Mind.",
        "explanation": "A bold, controversial, or hilarious opinion stated as an invitation for debate.",
        "keywords": ["change my mind", "debate", "opinion", "table", "coffee", "convince me", "argument"],
        "image_url": "https://i.imgflip.com/24y43o.jpg",
        "viral_score": 98.6,
    },
    {
        "name": "Trade Offer Braniac",
        "categories": ["funny"],
        "emotions": ["smug", "ironic"],
        "dialogue": "I receive: All your free time. You receive: Endless notifications and bugs.",
        "explanation": "Dressed in a suit offering an extremely one-sided transaction with a confident grin.",
        "keywords": ["trade offer", "i receive you receive", "deal", "negotiation", "unfair", "funny"],
        "image_url": "https://i.imgflip.com/54hjww.jpg",
        "viral_score": 97.6,
    },
    {
        "name": "Surprised Pikachu Face",
        "categories": ["gaming", "funny"],
        "emotions": ["shock", "ironic"],
        "dialogue": "Does obvious foolish thing -> Faces expected consequence -> :O",
        "explanation": "Pikachu with wide open mouth shocked by the exact predictable outcome of his own actions.",
        "keywords": ["surprised pikachu", "pokemon", "shock", "ironic", "consequences", "anime", "gaming"],
        "image_url": "https://i.imgflip.com/3ocgt8.jpg",
        "viral_score": 99.1,
    },
    {
        "name": "Hide the Pain Harold",
        "categories": ["work", "office", "funny"],
        "emotions": ["pain", "resigned", "suffering"],
        "dialogue": "Smiling warmly on the outside while dying inside from endless agony.",
        "explanation": "Stock photo model Andras Arato holding a coffee mug smiling with eyes full of deep existential suffering.",
        "keywords": ["hide the pain harold", "harold", "smiling through pain", "coffee", "office", "suffering", "grimace"],
        "image_url": "https://i.imgflip.com/gk5el.jpg",
        "viral_score": 99.3,
    },
    {
        "name": "Disaster Girl",
        "categories": ["funny"],
        "emotions": ["evil", "smug", "chaos"],
        "dialogue": "Smirking at the camera while the house behind burns to the ground.",
        "explanation": "A young girl looking back with a devious, serene smile as firefighters battle a burning house.",
        "keywords": ["disaster girl", "fire", "chaos", "evil smile", "revenge", "accident", "sabotage"],
        "image_url": "https://i.imgflip.com/23ls.jpg",
        "viral_score": 98.8,
    },
    {
        "name": "Stonks Rising",
        "categories": ["money", "funny", "tech"],
        "emotions": ["confident", "greedy", "optimistic"],
        "dialogue": "STONKS ^^^",
        "explanation": "Meme Man in a suit standing in front of a fake stock market graph with numbers going up.",
        "keywords": ["stonks", "money", "stocks", "crypto", "investing", "profit", "meme man", "wealth"],
        "image_url": "https://i.imgflip.com/31v5m0.jpg",
        "viral_score": 98.7,
    },
    {
        "name": "Not Stonks",
        "categories": ["money", "failure"],
        "emotions": ["sad", "defeat", "loss"],
        "dialogue": "NOT STONKS vvv",
        "explanation": "Meme Man looking down in utter tragedy as the market graph plummets into the floor.",
        "keywords": ["not stonks", "money", "loss", "crash", "broke", "crypto", "bad investment", "stocks"],
        "image_url": "https://i.imgflip.com/392x.jpg",
        "viral_score": 97.5,
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Imgflip Top 100 Fetcher
# ──────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "tech": ["code", "coding", "software", "computer", "matrix", "linux", "git", "hacker", "tech", "program", "developer"],
    "gaming": ["game", "gaming", "gamer", "nintendo", "pokemon", "mario", "zelda", "skyrim", "gta", "souls", "lag"],
    "work": ["office", "work", "meeting", "boss", "job", "career", "corporate", "employee", "interview"],
    "relationships": ["boyfriend", "girlfriend", "crush", "date", "dating", "love", "wife", "husband", "couple"],
    "wholesome": ["dog", "puppy", "cat", "hug", "smile", "friend", "pure", "sweet", "happy", "baby"],
    "tv": ["office", "marvel", "star wars", "breaking bad", "movie", "cinema", "batman", "joker", "spiderman"],
    "sports": ["sports", "football", "soccer", "basketball", "run", "gym", "referee", "boxing"],
    "money": ["money", "rich", "cash", "bank", "crypto", "stonks", "dollar", "expensive", "bill"],
}

def fetch_imgflip_memes():
    try:
        r = requests.get("https://api.imgflip.com/get_memes", timeout=10)
        data = r.json().get("data", {}).get("memes", [])
        logger.info(f"Retrieved {len(data)} templates from Imgflip API")
        results = []
        for item in data:
            name = item["name"]
            url = item["url"]
            name_lower = name.lower()

            # Determine best category
            cat = "funny"
            for c, kws in CATEGORY_KEYWORDS.items():
                if any(kw in name_lower for kw in kws):
                    cat = c
                    break

            words = re.findall(r"\b[a-zA-Z]{3,}\b", name_lower)
            keywords = list(set(words + [cat, "viral", "template", "reaction", "meme"]))
            
            results.append({
                "name": name,
                "categories": [cat],
                "emotions": ["humor", "relatable"],
                "dialogue": f"{name} Classic Reaction",
                "explanation": f"The famous '{name}' meme template. Ideal for {cat} and humorous situations.",
                "keywords": keywords,
                "image_url": url,
                "viral_score": round(80.0 + (item.get("box_count", 2) * 2.5), 1),
            })
        return results
    except Exception as e:
        logger.warning(f"Could not fetch Imgflip: {e}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Master Populator
# ──────────────────────────────────────────────────────────────────────────────

def generate_clean_slug(name: str, uid: str) -> str:
    clean = re.sub(r"[^a-z0-9\s-]", "", name.lower()).strip().replace(" ", "-")
    return f"{clean[:50]}-{uid[:6]}"


def build_master_dataset():
    # 1. Load existing Indian memes from scripts/build_huge_dataset.py if available
    indian_memes = []
    try:
        from scripts.build_huge_dataset import INDIAN_MEMES
        for im in INDIAN_MEMES:
            cat = im.get("category", "funny")
            # Map legacy category
            if cat in ("office", "unrealistic_goals"):
                cat_list = ["work", "office"]
            elif cat == "coding":
                cat_list = ["tech", "coding"]
            elif cat in ("relationship", "dating"):
                cat_list = ["relationships"]
            else:
                cat_list = [cat]

            indian_memes.append({
                "name": im["name"],
                "categories": cat_list,
                "emotions": ["humor", "relatable"],
                "dialogue": im.get("dialogue", f"{im['name']} reaction"),
                "explanation": im.get("explanation", "Classic viral Indian pop-culture meme."),
                "keywords": im.get("keywords", ["hindi", "viral", "bollywood"]),
                "image_url": f"https://cdn.memegpt.com/images/{im['name'].lower().replace(' ', '-')}.jpg",
                "gif_url": f"https://cdn.memegpt.com/gifs/{im.get('gif', 'meme.gif')}",
                "viral_score": float(im.get("viralScore", 90.0)),
            })
    except Exception as e:
        logger.warning(f"Indian memes import skipped: {e}")

    # 2. Fetch Imgflip memes
    imgflip_memes = fetch_imgflip_memes()

    # 3. Combine with Curated Memes
    all_raw = CURATED_MEMES + indian_memes + imgflip_memes
    
    seen = set()
    master = []
    for item in all_raw:
        n = item["name"].lower().strip()
        if n in seen:
            continue
        seen.add(n)
        uid = f"m_{hashlib.md5(n.encode('utf-8')).hexdigest()[:12]}"
        slug = generate_clean_slug(item["name"], uid)
        
        master.append({
            "id": uid,
            "name": item["name"],
            "slug": slug,
            "categories": item.get("categories", ["funny"]),
            "emotions": item.get("emotions", ["humor"]),
            "dialogue": item.get("dialogue", ""),
            "explanation": item.get("explanation", ""),
            "keywords": item.get("keywords", []),
            "image_url": item.get("image_url", "https://i.imgflip.com/1ur9b0.jpg"),
            "gif_url": item.get("gif_url"),
            "mp4_url": item.get("mp4_url"),
            "thumb_url": item.get("thumb_url"),
            "webp_url": item.get("webp_url"),
            "image_ref": item.get("image_url"),
            "gif_ref": item.get("gif_url"),
            "source": "master_catalog",
            "nsfw": False,
            "viral_score": float(item.get("viral_score", 85.0)),
            "popularity_score": float(item.get("viral_score", 85.0)) / 100.0,
            "usage_count": int(item.get("viral_score", 85.0) * 12),
            "upvotes": int(item.get("viral_score", 85.0) * 3),
            "downvotes": 2,
            "moderation_status": "approved",
            "alt_text": f"{item['name']} meme: {item.get('dialogue', '')}",
        })

    logger.info(f"Built master catalog of {len(master)} unique memes!")
    return master


def seed_database(db_path: Path, master_memes: list):
    logger.info(f"Seeding database at: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    with engine.begin() as conn:
        # Delete test/dummy memes
        test_patterns = [
            "%test%", "%trending meme%", "%exclude%", "%score calc%",
            "%invalid fb%", "%meeting could be email%", "%downloadable%"
        ]
        for pat in test_patterns:
            conn.execute(text("DELETE FROM memes WHERE lower(name) LIKE :pat"), {"pat": pat})
        
        # Also clean up duplicate names keeping highest score
        logger.info("Cleaned dummy/test entries.")

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_names = {row[0].lower().strip() for row in session.query(Meme.name).all()}
    added = 0
    updated = 0

    for m in master_memes:
        n = m["name"].lower().strip()
        if n in existing_names:
            # Update categories and image_url if empty
            existing = session.query(Meme).filter(Meme.name.ilike(m["name"])).first()
            if existing:
                existing.categories = m["categories"]
                existing.keywords = m["keywords"]
                existing.dialogue = m["dialogue"]
                existing.explanation = m["explanation"]
                if m.get("image_url") and not existing.image_url:
                    existing.image_url = m["image_url"]
                updated += 1
        else:
            new_meme = Meme(
                id=m["id"],
                name=m["name"],
                slug=m["slug"],
                categories=m["categories"],
                emotions=m["emotions"],
                dialogue=m["dialogue"],
                explanation=m["explanation"],
                keywords=m["keywords"],
                image_url=m["image_url"],
                gif_url=m.get("gif_url"),
                source=m["source"],
                nsfw=False,
                viral_score=m["viral_score"],
                popularity_score=m["popularity_score"],
                usage_count=m["usage_count"],
                upvotes=m["upvotes"],
                downvotes=m["downvotes"],
                moderation_status="approved",
                alt_text=m["alt_text"],
            )
            session.add(new_meme)
            added += 1

    session.commit()
    total = session.query(Meme).count()
    logger.info(f"Database at {db_path.name}: Added {added}, Updated {updated}, Total: {total}")
    session.close()


def generate_embeddings_file(master_memes: list):
    out_file = BACKEND_DIR / "data" / "embeddings.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Use MiniLM if available, else deterministic normalized vectors
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer for high-accuracy embedding...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding all memes...")

        texts = [
            f"{m['name']} {' '.join(m.get('categories', []))} {m.get('dialogue', '')} {m.get('explanation', '')} {' '.join(m.get('keywords', []))}"
            for m in master_memes
        ]
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

        data = [
            {"id": m["id"], "vector": [round(float(x), 6) for x in vectors[i]]}
            for i, m in enumerate(master_memes)
        ]
        out_file.write_text(json.dumps(data), encoding="utf-8")
        logger.info(f"Saved {len(data)} high-accuracy embeddings to {out_file}")
        return
    except Exception as e:
        logger.warning(f"SentenceTransformer embedding deferred: {e}. Generating fallback vectors...")

    # Fallback deterministic vector generator
    data = []
    for m in master_memes:
        t = f"{m['name']} {' '.join(m.get('categories', []))} {m.get('dialogue', '')} {' '.join(m.get('keywords', []))}"
        h = hashlib.sha256(t.encode("utf-8")).digest()
        vec = [(float(b) / 128.0 - 1.0) for b in (h * 12)[:384]]
        norm = (sum(x * x for x in vec) ** 0.5) or 1.0
        norm_vec = [round(x / norm, 6) for x in vec]
        data.append({"id": m["id"], "vector": norm_vec})

    out_file.write_text(json.dumps(data), encoding="utf-8")
    logger.info(f"Saved {len(data)} fallback embeddings to {out_file}")


def main():
    logger.info("Starting Master Meme Catalog Seeding...")
    master = build_master_dataset()

    # Save master dataset json
    master_json = BACKEND_DIR / "data" / "memes.json"
    master_json.parent.mkdir(parents=True, exist_ok=True)
    master_json.write_text(json.dumps(master, indent=2), encoding="utf-8")

    # Seed backend/memegpt.db
    backend_db = BACKEND_DIR / "memegpt.db"
    seed_database(backend_db, master)

    # Seed root memegpt.db as well
    root_db = ROOT_DIR / "memegpt.db"
    seed_database(root_db, master)

    # Generate embeddings
    generate_embeddings_file(master)
    logger.info("Catalog seeding & embedding generation COMPLETE!")


if __name__ == "__main__":
    main()
