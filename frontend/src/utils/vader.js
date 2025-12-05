// FRONTEND VADER-LIKE SENTIMENT ENGINE (UPGRADED)

const lexicon = {
  "excellent": 3,
  "awesome": 4,
  "fabulous": 4,
  "love": 3,
  "perfect": 3,
  "amazing": 4,
  "super": 2,
  "great": 2,
  "nice": 1,
  "wow": 3,
  "smooth": 1,
  "fast": 2,
  "mind-blowing": 4,

  // neutral
  "good": 1,
  "ok": 0,
  "fine": 0,
  "decent": 0,

  // negative
  "bad": -2,
  "poor": -2,
  "terrible": -3,
  "worst": -4,
  "awful": -3,
  "slow": -2,
  "disappointed": -3,
  "trash": -4,

  // emoji interpretation
  "😡": -3, "🤬": -4,
  "😢": -2, "😭": -3,
  "😍": 3,  "❤️": 3,
  "🔥": 2,  "💯": 3,
  "👍": 2,  "👎": -2
};

// Booster words (+/- intensifiers)
const boosters = {
  "very": 1.2,
  "extremely": 1.5,
  "super": 1.3,
  "really": 1.1,
  "slightly": 0.7,
  "barely": 0.6
};

export function vaderSentiment(text = "") {
  const words = text.toLowerCase().split(/\s+/);
  let score = 0;

  for (let i = 0; i < words.length; i++) {
    const w = words[i];

    if (lexicon[w] !== undefined) {
      let val = lexicon[w];

      // check boosters
      const prev = words[i - 1];
      if (prev && boosters[prev] !== undefined) {
        val *= boosters[prev];
      }

      score += val;
    }
  }

  // Classification
  if (score > 2) return "positive";
  if (score < -1) return "negative";
  return "neutral";
}
