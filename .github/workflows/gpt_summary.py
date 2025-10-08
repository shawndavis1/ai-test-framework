import os
import sys
import json
from openai import OpenAI

def summarize_test_results(report_dir):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    summary_file = "ai_summary.txt"

    # Step 1: Collect pytest or Allure JSON results
    report_path = os.path.join(report_dir, "summary.json")
    if not os.path.exists(report_path):
        # fallback: summarize based on simple folder stats
        summary_text = f"No structured JSON report found in {report_dir}. Summarizing based on folder contents."
        report_data = {"summary": summary_text}
    else:
        with open(report_path, "r") as f:
            report_data = json.load(f)

    # Step 2: Prepare summary prompt
    prompt = f"""
    You are an expert QA lead. Summarize the following test results briefly and clearly
    for management and engineers. Highlight failures, flaky tests, and overall stability.

    Test report:
    {json.dumps(report_data, indent=2)}
    """

    # Step 3: Generate summary with GPT
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=400
    )

    summary = response.choices[0].message.content

    # Step 4: Write summary to file for posting
    with open(summary_file, "w") as f:
        f.write(summary)

    print("✅ AI Summary generated and saved to ai_summary.txt")


if __name__ == "__main__":
    report_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    summarize_test_results(report_dir)