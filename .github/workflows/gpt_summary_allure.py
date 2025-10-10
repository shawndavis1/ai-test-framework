import os
import json
from openai import OpenAI

def load_allure_results(report_dir="reports"):
    """Parse Allure JSON result files into a simple summary."""
    results = []
    summary = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}

    if not os.path.exists(report_dir):
        print(f"⚠️ Allure results directory not found: {report_dir}")
        return summary, results

    for filename in os.listdir(report_dir):
        if filename.endswith("-result.json"):
            try:
                with open(os.path.join(report_dir, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    status = data.get("status", "unknown").lower()
                    name = data.get("name", "Unnamed Test")
                    summary[status] = summary.get(status, 0) + 1
                    results.append({"name": name, "status": status})
            except Exception as e:
                print(f"⚠️ Could not read {filename}: {e}")

    return summary, results


def generate_summary_text(summary, results):
    """Generate a concise plain-text summary for OpenAI context."""
    total = sum(summary.values())
    text = (
        f"Total tests: {total}\n"
        f"Passed: {summary['passed']}\n"
        f"Failed: {summary['failed']}\n"
        f"Broken: {summary['broken']}\n"
        f"Skipped: {summary['skipped']}\n\n"
        f"Here are the first few failed tests:\n"
    )

    failed_tests = [r for r in results if r["status"] in ("failed", "broken")]
    for t in failed_tests[:5]:
        text += f"- {t['name']} ({t['status']})\n"

    return text


def get_ai_summary(summary_text):
    """Call OpenAI GPT model to generate a natural language summary."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ Missing OPENAI_API_KEY environment variable.")

    client = OpenAI(api_key=api_key)

    prompt = (
        "You are a QA assistant. Summarize the following test run results clearly and concisely. "
        "Highlight key findings, patterns, and possible areas to investigate:\n\n"
        f"{summary_text}"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful QA report summarizer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    return completion.choices[0].message.content.strip()


def main():
    summary, results = load_allure_results()
    summary_text = generate_summary_text(summary, results)
    ai_summary = get_ai_summary(summary_text)

    print("\n===== 🧠 AI Test Summary =====\n")
    print(ai_summary)

    with open("ai_summary.txt", "w", encoding="utf-8") as f:
        f.write(ai_summary)

    print("\n✅ AI summary written to ai_summary.txt")


if __name__ == "__main__":
    main()