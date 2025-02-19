
import openai
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Set OpenAI API Key
openai.api_key = "your-api-key"  # Replace with your actual API key


# --------------------- STEP 1: Extract Public LinkedIn Profiles ---------------------
def google_search_extract_bio(query, num_results=10):
    """
    Searches Google for LinkedIn public profiles and extracts bio snippets.
    """
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for g in soup.find_all("div", class_="tF2Cxc"):
        profile_url = g.find("a")["href"]
        snippet = g.find("span", class_="aCOpRe")

        if "linkedin.com/in/" in profile_url and snippet:
            results.append({"profile_url": profile_url, "bio_snippet": snippet.text})

    return results[:num_results]


# --------------------- STEP 2: Extract Profile Details Using GPT-4 ---------------------
def extract_profile_data(profile_url, bio_text):
    """
    Uses GPT-4 to extract structured profile details from a given LinkedIn bio text.
    """
    prompt = f"""
    The following text is a public LinkedIn bio for a professional. Extract and format the key details.

    LinkedIn Profile URL: {profile_url}

    Bio Text:
    {bio_text}

    Please extract:
    - Full Name (if available)
    - Current Job Title
    - Company Name
    - Industry (if mentioned)
    - Key Skills and Interests (from bio text)
    - Recent Activity Summary (if any posts or engagements are visible)

    Provide the extracted details in a structured JSON format.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response["choices"][0]["message"]["content"]


# --------------------- STEP 3: Generate Personalized Outreach Messages ---------------------
def generate_message(profile_data):
    """
    Uses GPT-4 to generate a LinkedIn outreach message based on extracted profile details.
    """
    name = profile_data.get("Full Name", "there")
    job_title = profile_data.get("Current Job Title", "a professional")
    company = profile_data.get("Company Name", "your company")
    interests = profile_data.get("Key Skills and Interests", "marketing and branding")
    activity = profile_data.get("Recent Activity Summary", "a recent LinkedIn post")

    prompt = f"""
    Write a short, engaging, and professional LinkedIn networking message.

    - Recipient: {name}, {job_title} at {company}
    - Interests: {interests}
    - Recent Activity: {activity}

    Message should be friendly and professional.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    return response["choices"][0]["message"]["content"]


# --------------------- STEP 4: Run Full Process ---------------------
def run_full_process():
    """
    Runs the full AI-driven LinkedIn search, profile extraction, and message generation process.
    """
    # Define search query
    query = 'site:linkedin.com/in/ "Marketing" AND "Shanghai" AND "Fortune 500"'

    # Step 1: Get Public LinkedIn Profiles from Google Search
    profiles = google_search_extract_bio(query)

    # Step 2: Extract Profile Details using GPT-4
    extracted_profiles = []
    for profile in profiles:
        profile_url = profile["profile_url"]
        bio_snippet = profile["bio_snippet"]
        structured_data = extract_profile_data(profile_url, bio_snippet)
        extracted_profiles.append(structured_data)

    # Step 3: Generate Outreach Messages
    final_profiles = []
    for profile_data in extracted_profiles:
        profile_data["message"] = generate_message(profile_data)
        final_profiles.append(profile_data)

    return final_profiles


# --------------------- STEP 5: Web App Interface ---------------------
st.title("AI-Powered LinkedIn Networking Agent")

# Run AI Process & Display Results
if st.button("Find Marketers in Shanghai (Public Profiles)"):
    st.write("🔍 Searching for public LinkedIn profiles...")
    profiles = run_full_process()

    for profile in profiles:
        st.subheader(
            f"{profile.get('Full Name', 'Unknown')} - {profile.get('Current Job Title', 'N/A')} at {profile.get('Company Name', 'N/A')}")
        st.write(f"🔗 [LinkedIn Profile]({profile.get('profile_url', '#')})")
        st.write(f"**Industry:** {profile.get('Industry', 'N/A')}")
        st.write(f"**Key Interests:** {profile.get('Key Skills and Interests', 'N/A')}")
        st.write(f"**Recent Activity:** {profile.get('Recent Activity Summary', 'N/A')}")

        # Display AI-generated outreach message
        st.text_area("Personalized Outreach Message", profile["message"], height=100)

st.write("🚀 Click the button above to extract new profiles and generate messages!")