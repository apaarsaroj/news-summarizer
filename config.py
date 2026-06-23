# Number of articles to fetch from NewsAPI
NUM_ARTICLES = 10

# Number of top articles to summarize after relevance scoring
TOP_N = 3

# Max characters to send to Claude per article
MAX_CHARS = 3000

# Minimum characters for an article to be considered valid
MIN_CHARS = 200

# Summarizer temperature — slight creativity
SUMMARIZER_TEMPERATURE = 0.0

# Judge temperature — fully deterministic
JUDGE_TEMPERATURE = 0

# Maximum graph iterations before forcing exit
MAX_ITERATIONS = 3

# Minimum average quality score (faithfulness + conciseness) to accept results
# Score is 0–100; below this threshold the graph loops and re-scrapes
QUALITY_THRESHOLD = 60