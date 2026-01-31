import time
import urllib.parse
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

# --- CONFIG ---
USER_DATA_DIR = Path(__file__).resolve().parent / "automation_session"
TARGET_TITLES = "Automation Engineer", "Sr Automation QA", "Sr Web Development", "Full Stack Developer"
TARGET_LOCATIONS = "Chicago, Lombard, USA"
RESUME_PATH = str(Path(__file__).resolve().parent / "Ahmed_Automation_Resume.docx")

# Company Blacklist (Add companies you want to skip here)
BLACKLIST_COMPANIES = ["Staffing Agency X", "Bad Company Inc"]

# Salary Filters
MIN_SALARY_YEAR = 90000
MIN_SALARY_HOUR = 45

# Advanced Filtering
IT_KEYWORDS = ["automation", "java", "python", "software", "test", "playwright", "selenium", "qa", "aws", "devops", "HTML", "WEB", "JS", "CSS"]
FORBIDDEN_TITLES = [
    "electrical engineer", "mechanical", "civil", "construction", "nurse",
    "hardware", "technician", "telecommunication", "voice", "communications",
    "phone", "support", "help desk", "manufacturing", "industrial, warehouse","robotic","sortation"
]


def log_application(job_title):
    with open("applied_jobs.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Applied: {job_title}\n")


def run_engine():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0]

        # A list of titles you like
        titles_list = ["Automation Engineer", "QA Automation", "SDET"]

        # Join them with 'OR' for a better LinkedIn search
        TARGET_TITLES = " OR ".join(f'"{t}"' for t in titles_list)

        query = urllib.parse.quote(TARGET_TITLES)

        print(f"Encoded Query: {query}")

        location = urllib.parse.quote(TARGET_LOCATIONS)
        # Past 7 Days
        search_url = f"https://www.linkedin.com/jobs/search/?f_AL=true&f_TPR=r604800&keywords={query}&location={location}"

        print(f"🌐 Navigating to IT results...")
        page.goto(search_url, wait_until="load")
        time.sleep(5)

        job_cards = page.locator(".job-card-container, .jobs-search-results-list__item").all()
        print(f"📊 Scanning {len(job_cards)} potential matches...")

        for card in job_cards:
            try:
                card.scroll_into_view_if_needed()

                # Check Company Blacklist
                company_name = card.locator(".job-card-container__primary-description").first.inner_text().strip()
                if any(black in company_name for black in BLACKLIST_COMPANIES):
                    print(f"⏭️ Skipping Blacklisted Company: {company_name}")
                    continue

                title_link = card.locator("a[href*='/jobs/view/']").first
                job_title = title_link.inner_text().lower()

                # 1. Title Filter
                if any(bad in job_title for bad in FORBIDDEN_TITLES):
                    print(f"⏭️ Skipping: {job_title.strip()}")
                    continue

                print(f"🧐 Inspecting: {job_title.title().strip()}")
                title_link.click(force=True)

                desc_container = page.locator(".jobs-description")
                desc_container.wait_for(state="visible", timeout=7000)
                full_text = desc_container.inner_text().lower()

                # 2. Salary Intelligence
                salary_matches = re.findall(r'\$(\d{2,3}(?:,\d{3})?)', full_text)
                should_skip_salary = False
                for val in salary_matches:
                    num = int(val.replace(',', ''))
                    if (num < MIN_SALARY_HOUR and num > 10) or (num < MIN_SALARY_YEAR and num > 1000):
                        should_skip_salary = True

                if should_skip_salary:
                    print(f"💰 Skipping: Low salary mentioned.")
                    continue

                # 3. Skill verification
                if "automation" not in job_title and not any(word in full_text for word in IT_KEYWORDS):
                    print(f"⏭️ Skipping: No relevant IT context.")
                    continue

                apply_btn = page.locator("button.jobs-apply-button").first
                if apply_btn.is_visible():
                    print("🚀 Match Found! Applying...")
                    apply_btn.click()
                    time.sleep(2)

                    # 4. Smart Form Handling
                    for _ in range(10):
                        # --- ADD THIS INSIDE YOUR FORM LOOP ---
                        file_input = page.locator("input[type='file']").first
                        if file_input.is_visible():
                            # Check if the label mentions 'resume' or 'cv'
                            label_el = page.locator(f"label[for='{file_input.get_attribute('id')}']")
                            label_text = label_el.inner_text().lower() if label_el.count() > 0 else ""

                            if "resume" in label_text or "cv" in label_text or file_input.count() > 0:
                                print(f"📤 Uploading resume: {RESUME_PATH}")
                                file_input.set_input_files(RESUME_PATH)
                                time.sleep(2)  # Give it a moment to process the upload
                        # Handle Inputs
                        for i in page.locator("input[type='text'], input[type='number'], textarea").all():
                            if i.is_visible():
                                label_el = page.locator(f"label[for='{i.get_attribute('id')}']")
                                label = label_el.inner_text().lower() if label_el.count() > 0 else ""

                                # Logic for specific questions
                                if any(x in label for x in
                                       ["experience", "years", "java", "python", "selenium", "playwright"]):
                                    i.fill("5")  # Upped to 5 for Senior roles
                                elif any(x in label for x in ["communication", "team", "collaborat", "skills"]):
                                    i.fill("Excellent")
                                elif "authorized" in label or "visa" in label:
                                    i.fill("Yes")
                                else:
                                    # Default answer for unknown text boxes to prevent stalling
                                    i.fill("3")

                        # Radio/Dropdown
                        for r in page.locator("label:has-text('Yes'), label:has-text('Authorized')").all():
                            if r.is_visible(): r.click()

                        for dd in page.locator("select").all():
                            if dd.is_visible():
                                content = dd.inner_text()
                                if "Yes" in content:
                                    dd.select_option(label="Yes")
                                elif "Full-time" in content:
                                    dd.select_option(label="Full-time")
                                else:
                                    dd.select_option(index=1)

                        btn = page.locator(
                            "button:has-text('Next'), button:has-text('Review'), button:has-text('Submit application')").first
                        if btn.is_visible():
                            txt = btn.inner_text()
                            btn.click()
                            time.sleep(2)
                            if "Submit application" in txt:
                                print(f"✅ SUBMITTED: {job_title.title().strip()}")
                                log_application(job_title.strip())
                                time.sleep(2)
                                done_btn = page.locator("button:has-text('Done')").first
                                if done_btn.is_visible(): done_btn.click()
                                break
                        else:
                            break

                page.keyboard.press("Escape")
                time.sleep(1)
                discard = page.get_by_role("button", name="Discard").first
                if discard.is_visible(): discard.click()

            except Exception:
                page.keyboard.press("Escape")
                continue

        context.close()


if __name__ == "__main__":
    run_engine()