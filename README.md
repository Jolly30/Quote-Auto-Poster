# 🚀 24/7 Free TikTok Motivational Quotes Auto-Poster

Welcome! This is a **100% free, zero-code, zero-n8n** automation that generates high-quality motivational videos and posts them to your TikTok channel automatically **24/7 in the cloud**.

---

## 🛠️ Step-by-Step Setup Guide (Takes Under 5 Minutes)

You do **not** need to write any code. Just follow these simple steps to set up your free accounts and launch your auto-poster!

### Step 1: Create a Free Buffer Account
Buffer is a free tool that publishes videos to TikTok.
1. Sign up for a free account at [buffer.com](https://buffer.com/).
2. Connect your **TikTok channel** (Buffer's free plan allows connecting up to 3 channels for free).
3. Open a new browser tab and go to [publish.buffer.com/apps](https://publish.buffer.com/apps) (Buffer's developer apps page).
4. Click **Create an App** (fill in any name/description, e.g., "TikTok Auto Poster").
5. Copy the **Access Token** generated for your app. (Keep this token safe!)

---

### Step 2: Get a Free Pexels API Key (OPTIONAL 💡)
By default, the script includes a library of beautiful vertical landscape videos that download automatically with **zero keys**. 
* **If you want to use our keyless library:** You can skip this step entirely!
* **If you want custom search terms later:** 
  1. Go to [pexels.com/api/](https://www.pexels.com/api/) and sign up for a free developer account.
  2. Click **Your API Key** $\rightarrow$ Request API Key.
  3. Copy your **API Key**.

---

### Step 3: Create your Free GitHub Repository
We will host and run the automation inside a private, free GitHub repository so it runs 24/7.
1. Go to [github.com](https://github.com/) and log in (or create a free account).
2. Click the **`+`** icon in the top-right corner and select **New repository**.
3. Set your settings:
   * **Repository name:** `tiktok-auto-poster`
   * **Public/Private:** Select **Private** (so your API keys stay completely private and hidden).
   * Do **not** check "Add a README file" (we already have one in this folder).
4. Click **Create repository**.
5. Upload these folder files (`.github/`, `video_generator.py`, `quotes.json`, `requirements.txt`, `README.md`) to your new repository!
   * *If you are using GitHub on your browser:* Simply click **"uploading an existing file"** on your blank repository page, drag and drop all the files from this local desktop folder, and click **Commit changes**.

---

### Step 4: Add Your Keys to GitHub (Secrets)
This keeps your API tokens secure.
1. In your new GitHub repository, click the **Settings** tab in the top navigation bar.
2. In the left sidebar, expand **Secrets and variables** and click **Actions**.
3. Click the green **New repository secret** button.
4. Add the following secrets:
   * **Name:** `BUFFER_ACCESS_TOKEN` $\rightarrow$ **Value:** Paste your Buffer Access Token.
   * **Name:** `PEXELS_API_KEY` (OPTIONAL) $\rightarrow$ **Value:** Paste your Pexels API key (only if you completed Step 2).
5. Click **Add secret** for each.

---

### Step 5: Enable Workflows & Run a Test Post!
1. In your GitHub repository, click the **Actions** tab in the top navigation bar.
2. If prompted, click the green button that says **"I understand my workflows, go ahead and enable them"**.
3. Under the list on the left, click **`24/7 TikTok Auto-Posting Quotes Generator`**.
4. Click the **Run workflow** dropdown button on the right, and then click the green **Run workflow** button!
5. GitHub will spin up a free virtual machine, download the b-roll, generate the professional voiceover, overlay the styled caption, host the video, and send it directly to your Buffer/TikTok account.

---

## 🌟 How the Automated Pipeline Works For You
* **Automatic Posts:** By default, it will trigger **automatically once a day** at 9:00 AM UTC (3:30 PM Myanmar time). You don't have to keep your computer open or click anything!
* **100% Free Hosting:** The script hosts your finished `.mp4` video inside your GitHub repository's **Releases** tab automatically. It generates a high-speed direct stream link for Buffer to feed directly to TikTok, keeping everything $0/month.
* **100% Fresh Quotes:** The script pulls from the curated `quotes.json` containing 100+ viral motivational quotes!
