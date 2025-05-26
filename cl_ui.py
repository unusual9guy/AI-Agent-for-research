from termcolor import colored
import time

def print_header():
    print(colored("="*60, "cyan"))
    print(colored("🔬  AI RESEARCH ASSISTANT", "cyan", attrs=["bold"]))
    print(colored("="*60, "cyan"))

def print_intro():
    print(colored("Enter your research topic below. The assistant will generate a detailed, academic-style report.", "green"))
    print()

def get_user_input():
    topic = input(colored("📝 Enter your research topic: ", "yellow"))
    print()
    return topic

def print_progress():
    print(colored("⏳ Researching and drafting your report... please wait.\n", "blue"))
    for i in range(3):
        print("." * (i + 1))
        time.sleep(1)

def print_result_ui(response):
    print(colored("\n📚 Research Report Generated Successfully!\n", "green", attrs=["bold"]))
    
    print(colored("🧠 Topic:", "cyan"), response.topic)
    print(colored("📄 Abstract:\n", "cyan"), response.abstract)
    print(colored("\n📘 Introduction:\n", "cyan"), response.introduction)
    print(colored("\n📝 Detailed Research:\n", "cyan"), response.detailed_research)
    print(colored("\n✅ Conclusion:\n", "cyan"), response.conclusion)
    
    print(colored("\n🔍 Keywords:", "magenta"), ', '.join(response.keywords))
    print(colored("📊 Confidence Score:", "magenta"), response.confidence_score)
    print(colored("🗓️ Last Updated:", "magenta"), response.last_updated)
    
    print(colored("\n📚 Sources:", "green"))
    for source in response.sources:
        print(f" - {source}")
    
    print(colored("\n📌 Citations:", "green"))
    for cite in response.citations:
        print(f" - {cite}")

    print(colored(f"\n🧰 Tools Used: {', '.join(response.tools_used)}", "blue"))
    print(colored(f"📄 Estimated Page Count: {response.page_count}", "blue"))
    print(colored("\n✔️ End of Report\n", "green", attrs=["bold"]))
