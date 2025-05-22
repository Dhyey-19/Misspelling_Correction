import os
import concurrent.futures
from rapidfuzz import process, fuzz
import language_tool_python

# Initialize LanguageTool for grammar and spelling correction
tool = language_tool_python.LanguageTool('en-US')

# Define file paths
BASE_DIR = os.path.dirname(__file__)
PROBLEMS_PATH = os.path.join(BASE_DIR, "Problems.txt")
TGT_PATH = os.path.join(BASE_DIR, "artificial.train.tgt")
SOLUTION_PATH = os.path.join(BASE_DIR, "english_eval.corrected.txt")

# Load sentences from file
def load_sentences(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

# Use LanguageTool AI correction
def correct_with_language_tool(sentence):
    matches = tool.check(sentence)
    return language_tool_python.utils.correct(sentence, matches)

# Try to match with RapidFuzz, fallback to LanguageTool if no good match
def correct_sentence(sentence, correct_sentences):
    match = process.extractOne(sentence, correct_sentences, scorer=fuzz.ratio, score_cutoff=70)
    if match:
        return match[0]
    else:
        return correct_with_language_tool(sentence)

def main():
    # Load sentences
    if not os.path.exists(PROBLEMS_PATH) or not os.path.exists(TGT_PATH):
        print("Error: Required input files not found.")
        return

    misspelled_sentences = load_sentences(PROBLEMS_PATH)
    correct_sentences = load_sentences(TGT_PATH)

    # Apply corrections
    with concurrent.futures.ThreadPoolExecutor() as executor:
        corrected_output = list(executor.map(lambda s: correct_sentence(s, correct_sentences), misspelled_sentences))

    # Save output
    with open(SOLUTION_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(corrected_output) + "\n")

    print("✅ Correction complete!")
    print(f"📄 Corrected output saved at: {SOLUTION_PATH}")

if __name__ == "__main__":
    main()
