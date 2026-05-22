import os
import sys
import json
import random
import requests
import subprocess
import textwrap
import asyncio
import edge_tts
from datetime import datetime

# ==========================================
# CONFIGURATION & API KEYS FROM ENVIRONMENT
# ==========================================
# Unique compliant User-Agent to bypass Wikimedia and public CDN bot throttling (429/403)
HEADERS = {
    "User-Agent": "TikTokQuotesAutoPoster/1.0 (https://github.com/Jolly30/Tiktok-Auto-Poster; contact@example.com) PythonRequests/2.31"
}

# Buffer Access Token (required to post to TikTok)
BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN")

# GitHub details (provided automatically by GitHub Actions)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")  # e.g., "username/repo"

# Pexels API Key is now 100% OPTIONAL!
# If you don't provide it, the script will use Mixkit's free direct CDN portrait videos below.
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# ==========================================
# CALM & CINEMATIC VOICEOVER OPTIONS
# ==========================================
# Choose your voice style! Simply swap the default below or set VOICE_SELECTOR in env.
# Highly Recommended Calm/Narrative Voices:
# - "en-GB-RyanNeural"    (British Male - Calm, deep, documentary narrator style - DEFAULT)
# - "en-US-BrianNeural"   (American Male - Warm, sincere, conversational and calm)
# - "en-US-JennyNeural"   (American Female - Very soft, comforting, considerate)
# - "en-US-AvaNeural"     (American Female - Warm, expressive, caring)
# - "en-GB-SoniaNeural"   (British Female - Soothing, sophisticated)
VOICE_SELECTOR = os.environ.get("VOICE_SELECTOR", "en-GB-RyanNeural")

# Speaking speed rate (e.g. "-8%" makes it slightly slower, deeper, and calmer)
VOICE_RATE = os.environ.get("VOICE_RATE", "-8%")

# Voiceover speaking volume (e.g. "0.7" for softer, down from default "1.0")
VOICE_VOLUME = float(os.environ.get("VOICE_VOLUME", "0.7"))

# Background music volume (e.g. "0.05" for very soft, down from default "0.12")
MUSIC_VOLUME = float(os.environ.get("MUSIC_VOLUME", "0.1"))

# ==========================================
# 100% FREE, DIRECT, UNLIMITED VERTICAL VIDEOS
# ==========================================
# Direct high-quality stock portrait MP4 CDN URLs from Mixkit.
# Requires ZERO API keys, ZERO registrations, and has absolutely NO download limits!
DIRECT_VIDEO_URLS = [
    "https://assets.mixkit.co/videos/preview/mixkit-starry-night-sky-over-a-silent-river-portrait-42861-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-forest-stream-in-the-sunlight-portrait-42903-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-waves-crashing-on-rocks-from-above-portrait-43026-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-vertical-shot-of-a-beautiful-waterfall-in-a-forest-42817-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-clouds-and-blue-sky-time-lapse-portrait-42898-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-foggy-pine-forest-in-mountains-portrait-42814-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-vertical-shot-of-the-sun-rising-over-the-mountains-42880-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-rain-falling-on-a-window-portrait-42921-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-driving-on-a-forest-road-in-autumn-portrait-42878-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-slow-motion-of-a-desert-sunset-portrait-42886-large.mp4"
]

# ==========================================
# 100% FREE, DIRECT, UNLIMITED BACKGROUND MUSIC
# ==========================================
# Direct high-quality stock/royalty-free background classical ambient music in Ogg format
# from Wikimedia Commons (high-speed, keyless, and completely free of bot-blocking protections).
DIRECT_MUSIC_URLS = [
    # Gymnopédie No. 1 by Erik Satie (performed by Kevin MacLeod) - Beautiful, slow ambient piano
    "https://upload.wikimedia.org/wikipedia/commons/6/68/Kevin_MacLeod_-_Erik_Satie_Gymnopedie_No_1.ogg",
    # Gymnopédie No. 2 by Erik Satie (performed by Kevin MacLeod) - Peaceful, relaxing ambient piano
    "https://upload.wikimedia.org/wikipedia/commons/8/80/Kevin_MacLeod_-_Erik_Satie_Gymnopedie_No_2.ogg"
]

def download_file(url, output_path, headers=None, use_curl=True):
    """
    Downloads a file from a URL using curl via subprocess as the primary, highly robust method
    (to bypass requests/TLS-JA3 fingerprint blocks on CDNs like Wikimedia Commons and Mixkit),
    and falls back to Python requests if curl is not available.
    """
    # Try curl first (most robust against bot-blocking CDN configurations)
    if use_curl:
        try:
            # Build curl command with -f to fail on HTTP errors (e.g., 403 Forbidden)
            cmd = ["curl", "-L", "-f", "-s", "-o", output_path]
            # Use standard desktop browser User-Agent to ensure highest compatibility
            cmd.extend(["-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"])
            if headers:
                for k, v in headers.items():
                    cmd.extend(["-H", f"{k}: {v}"])
            cmd.append(url)
            
            subprocess.run(cmd, check=True)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
        except Exception as e:
            log(f"WARNING: curl download failed for {url} ({e}). Trying python requests fallback...")

    # Fallback to requests
    try:
        req_headers = HEADERS.copy()
        if headers:
            req_headers.update(headers)
        res = requests.get(url, headers=req_headers, timeout=60, stream=True)
        res.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        log(f"ERROR: Download failed for {url} ({e})")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

# Alternate search terms if Pexels API key is supplied
PEXELS_SEARCH_TERMS = [
    "foggy forest", "mountain drone", "ocean waves portrait", "starry sky vertical",
    "peaceful river portrait", "vertical desert sunset", "aesthetic waterfall vertical"
]

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def check_requirements():
    log("Checking prerequisites...")
    if not BUFFER_ACCESS_TOKEN:
        log("ERROR: BUFFER_ACCESS_TOKEN environment variable is missing!")
        log("Please add your Buffer token to your GitHub Repository Secrets.")
        sys.exit(1)
    
    # Verify FFmpeg is available in the runner environment
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("FFmpeg is available.")
    except FileNotFoundError:
        log("ERROR: FFmpeg is not installed or not in system PATH! Please install FFmpeg.")
        sys.exit(1)

def get_random_quote():
    log("Selecting motivational quote...")
    try:
        with open("quotes.json", "r") as f:
            quotes = json.load(f)
        selected = random.choice(quotes)
        quote_text = f"\"{selected['quote']}\""
        if selected.get("author"):
            quote_text += f"\n\n— {selected['author']}"
        log(f"Selected Quote: {selected['quote']}")
        return quote_text
    except Exception as e:
        log(f"ERROR reading quotes.json: {e}")
        # Bulletproof fallback quote
        return "\"Success is not final, failure is not fatal: it is the courage to continue that counts.\"\n\n— Winston Churchill"

def download_font():
    font_path = "font.ttf"
    if os.path.exists(font_path):
        return font_path
    
    log("Downloading premium modern font (Montserrat)...")
    url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"
    if download_file(url, font_path):
        log("Font downloaded successfully.")
        return font_path
    else:
        log("WARNING: Could not download Montserrat font. Falling back to system default.")
        return "Arial"

def generate_voiceover(text, output_file="voiceover.mp3"):
    log(f"Synthesizing neural voiceover via edge-tts (Voice: '{VOICE_SELECTOR}', Rate: '{VOICE_RATE}')...")
    clean_text = text.replace("\n", " ").replace("\"", "").replace("—", "by")
    
    async def _synthesize():
        try:
            communicate = edge_tts.Communicate(clean_text, VOICE_SELECTOR, rate=VOICE_RATE)
            await communicate.save(output_file)
            log("Voiceover generated successfully.")
        except Exception as e:
            log(f"CRITICAL ERROR inside edge-tts Communicate: {type(e).__name__}: {e}")
            raise e

    try:
        asyncio.run(_synthesize())
    except Exception as e:
        log(f"ERROR: edge-tts voiceover synthesis failed! Details: {e}")
        log(f"Attempted text: '{clean_text}'")
        log(f"Selected voice: '{VOICE_SELECTOR}'")
        sys.exit(1)

def get_audio_duration(file_path="voiceover.mp3"):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            capture_output=True, text=True, check=True
        )
        duration = float(result.stdout.strip())
        log(f"Voiceover duration: {duration:.2f} seconds.")
        return duration
    except Exception as e:
        log(f"WARNING: Could not read duration with ffprobe ({e}). Defaulting to 15 seconds.")
        return 15.0

def download_background_video(output_file="background.mp4"):
    # If Pexels key is provided, search Pexels. Otherwise, download a direct vertical video from Mixkit.
    if PEXELS_API_KEY:
        log("PEXELS_API_KEY detected. Searching Pexels for a portrait video...")
        headers = {"Authorization": PEXELS_API_KEY}
        search_term = random.choice(PEXELS_SEARCH_TERMS)
        url = f"https://api.pexels.com/videos/search?query={search_term}&per_page=15&orientation=portrait"
        
        try:
            res = requests.get(url, headers=headers, timeout=30)
            res.raise_for_status()
            videos = res.json().get("videos", [])
            if videos:
                selected_video = random.choice(videos)
                video_files = selected_video.get("video_files", [])
                download_url = None
                for f in sorted(video_files, key=lambda x: int(x.get("width", 0) or 0), reverse=True):
                    if f.get("width") and f.get("height") and f.get("width") < f.get("height"):
                        download_url = f.get("link")
                        break
                if not download_url and video_files:
                    download_url = video_files[0].get("link")
                
                if download_url:
                    log("Downloading background from Pexels CDN...")
                    if download_file(download_url, output_file, headers=headers):
                        log("Pexels background video downloaded successfully.")
                        return output_file
        except Exception as e:
            log(f"Pexels API download failed ({e}). Falling back to free direct Mixkit CDN...")

    # Primary or Fallback Option: Mixkit Direct CDN URLs (100% Free, Unlimited, Keyless)
    log("Accessing 100% Free Direct Mixkit vertical video CDN...")
    download_url = random.choice(DIRECT_VIDEO_URLS)
    
    if download_file(download_url, output_file):
        log("Mixkit background video downloaded successfully with ZERO keys!")
        return output_file
    else:
        log("Creating vertical gradient background as final safety fallback...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:d=30",
            "-vf", "noise=alls=10:allf=t+u", "-pix_fmt", "yuv420p", output_file
        ], check=True)
        log("Safety vertical background generated.")
        return output_file

def download_background_music(output_file="music.ogg"):
    """
    Downloads a random royalty-free background track from the curated direct CDN list
    if there is no local 'music.mp3' or 'music.ogg' file provided by the user.
    Returns True if music was auto-downloaded, False otherwise.
    """
    if os.path.exists("music.mp3") or os.path.exists("music.ogg"):
        log("Local background music file detected. Skipping download.")
        return False
        
    log("No local music file found. Attempting to download a beautiful default royalty-free track...")
    download_url = random.choice(DIRECT_MUSIC_URLS)
    
    if download_file(download_url, output_file):
        log("Default background music track successfully downloaded!")
        return True
    else:
        log("WARNING: Default music track download failed. Gracefully falling back to voiceover-only...")
        if os.path.exists(output_file):
            os.remove(output_file)
        return False

def render_final_video(quote_text, font_path, voice_duration, video_file="background.mp4", audio_file="voiceover.mp3", output_file="final_post.mp4"):
    log("Compiling final video with stylized centered captions using FFmpeg...")
    
    # Word wrap lines for clean vertical framing on phone screens
    wrapped_lines = []
    paragraphs = quote_text.split('\n\n')
    for p in paragraphs:
        if p.startswith("—"):
            wrapped_lines.append(p)
        else:
            wrapped_lines.extend(textwrap.wrap(p, width=28))
    wrapped_quote = "\n".join(wrapped_lines)
    
    # Write quote text to a temporary file to bypass all FFmpeg escaping bugs
    quote_file = "quote_text.txt"
    try:
        with open(quote_file, "w", encoding="utf-8") as f:
            f.write(wrapped_quote)
    except Exception as e:
        log(f"ERROR writing temporary quote file: {e}")
        # fallback to standard escaped text if file writing fails
        escaped_text = wrapped_quote.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
        font_filter = f"fontfile='{font_path}':text='{escaped_text}'"
    else:
        font_filter = f"fontfile='{font_path}':textfile='{quote_file}'"
    
    style_filter = "fontsize=46:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=12:expansion=none"
    
    if ":" in font_path:
        font_path_escaped = font_path.replace(":", "\\:")
        if os.path.exists(quote_file):
            font_filter = f"fontfile='{font_path_escaped}':textfile='{quote_file}'"
        else:
            font_filter = f"fontfile='{font_path_escaped}':text='{escaped_text}'"

    music_file = None
    if os.path.exists("music.mp3"):
        music_file = "music.mp3"
    elif os.path.exists("music.ogg"):
        music_file = "music.ogg"
        
    has_music = music_file is not None
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", video_file,
        "-i", audio_file
    ]
    if has_music:
        log(f"Optional background music ({music_file}) detected. Mixing into final video...")
        cmd.extend(["-stream_loop", "-1", "-i", music_file])
        
    cmd.extend([
        "-t", f"{voice_duration + 1.0:.2f}",
        "-vf", f"drawtext={font_filter}:{style_filter},scale=1080:1920"
    ])
    if has_music:
        # Mix voiceover (input 1) and background music (input 2)
        # Voiceover volume and music volume dynamically configured
        # amix inputs=2:duration=first makes it end when the voiceover ends
        cmd.extend([
            "-filter_complex", f"[1:a]volume={VOICE_VOLUME}[v_audio];[2:a]volume={MUSIC_VOLUME}[bg_audio];[v_audio][bg_audio]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "0:v",
            "-map", "[a]"
        ])
        
    cmd.extend([
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_file
    ])
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Final TikTok video successfully rendered!")
        return output_file
    except Exception as e:
        log(f"ERROR rendering video with drawtext: {e}")
        try:
            log("Attempting simple fallback rendering...")
            fallback_text_filter = f"textfile='{quote_file}'" if os.path.exists(quote_file) else f"text='{escaped_text}'"
            fallback_cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1", "-i", video_file,
                "-i", audio_file
            ]
            if has_music:
                fallback_cmd.extend(["-stream_loop", "-1", "-i", music_file])
                
            fallback_cmd.extend([
                "-t", f"{voice_duration + 1.0:.2f}",
                "-vf", f"drawtext={fallback_text_filter}:fontsize=40:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:expansion=none,scale=1080:1920"
            ])
            if has_music:
                fallback_cmd.extend([
                    "-filter_complex", f"[1:a]volume={VOICE_VOLUME}[v_audio];[2:a]volume={MUSIC_VOLUME}[bg_audio];[v_audio][bg_audio]amix=inputs=2:duration=first:dropout_transition=2[a]",
                    "-map", "0:v",
                    "-map", "[a]"
                ])
                
            fallback_cmd.extend([
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                output_file
            ])
            subprocess.run(fallback_cmd, check=True)
            log("Fallback video successfully rendered.")
            return output_file
        except Exception as ex:
            log(f"WARNING: Fallback text rendering failed ({ex}).")
            log("Attempting final fallback (no captions, audio + video only)...")
            try:
                no_caption_cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "-1", "-i", video_file,
                    "-i", audio_file
                ]
                if has_music:
                    no_caption_cmd.extend(["-stream_loop", "-1", "-i", music_file])
                    
                no_caption_cmd.extend([
                    "-t", f"{voice_duration + 1.0:.2f}",
                    "-vf", "scale=1080:1920"
                ])
                if has_music:
                    no_caption_cmd.extend([
                        "-filter_complex", f"[1:a]volume={VOICE_VOLUME}[v_audio];[2:a]volume={MUSIC_VOLUME}[bg_audio];[v_audio][bg_audio]amix=inputs=2:duration=first:dropout_transition=2[a]",
                        "-map", "0:v",
                        "-map", "[a]"
                    ])
                    
                no_caption_cmd.extend([
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    output_file
                ])
                subprocess.run(no_caption_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log("Fallback video (no captions) successfully rendered!")
                return output_file
            except Exception as final_ex:
                log(f"CRITICAL ERROR: Render pipeline completely failed: {final_ex}")
                sys.exit(1)

def upload_to_github_releases(file_path):
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        log("Running locally (skipping cloud release hosting). Output saved as 'final_post.mp4'.")
        return None
        
    log("Hosting video on GitHub Releases (100% Free CDN)...")
    tag_name = datetime.now().strftime("video-%Y-%m-%d-%H%M%S")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    release_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases"
    payload = {
        "tag_name": tag_name,
        "name": f"TikTok Video - {datetime.now().strftime('%Y-%m-%d')}",
        "body": "Automated motivational quotes posting.",
        "draft": False,
        "prerelease": False
    }
    
    try:
        res = requests.post(release_url, headers=headers, json=payload)
        res.raise_for_status()
        release_id = res.json().get("id")
        
        upload_url = f"https://uploads.github.com/repos/{GITHUB_REPOSITORY}/releases/{release_id}/assets?name=video.mp4"
        headers["Content-Type"] = "video/mp4"
        with open(file_path, "rb") as video_file:
            upload_res = requests.post(upload_url, headers=headers, data=video_file)
            upload_res.raise_for_status()
            
        direct_url = f"https://github.com/{GITHUB_REPOSITORY}/releases/download/{tag_name}/video.mp4"
        log(f"Direct high-speed stream link generated:\n{direct_url}")
        return direct_url
    except Exception as e:
        log(f"ERROR uploading to GitHub Releases: {e}")
        return None

def get_repository_visibility():
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        return "local"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        repo_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}"
        res = requests.get(repo_url, headers=headers, timeout=15)
        if res.status_code == 200:
            is_private = res.json().get("private", False)
            return "private" if is_private else "public"
    except Exception as e:
        log(f"WARNING: Could not determine repo visibility ({e}). Assuming private.")
    return "private"

def upload_to_free_cdn(file_path):
    log("Uploading compiled video to Tmpfiles.org (100% Free Public CDN)...")
    url = "https://tmpfiles.org/api/v1/upload"
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            res = requests.post(url, files=files, timeout=90)
        res.raise_for_status()
        data = res.json()
        if data.get("status") == "success":
            upload_url = data["data"]["url"]
            # Convert standard URL to direct download URL
            direct_url = upload_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
            log(f"Direct public stream link generated successfully:\n{direct_url}")
            return direct_url
        else:
            raise Exception(f"Tmpfiles returned error status: {data}")
    except Exception as e:
        log(f"WARNING: Tmpfiles.org upload failed ({e}). Trying Catbox.moe fallback...")
        
        # Fallback 1: Catbox.moe
        url_catbox = "https://catbox.moe/user/api.php"
        payload = {"reqtype": "fileupload"}
        try:
            with open(file_path, "rb") as f:
                files = {"fileToUpload": f}
                res = requests.post(url_catbox, data=payload, files=files, timeout=90)
            res.raise_for_status()
            direct_url = res.text.strip()
            if direct_url.startswith("https://"):
                log(f"Direct public stream link generated successfully via Catbox:\n{direct_url}")
                return direct_url
            else:
                raise Exception(f"Catbox returned unexpected response: {direct_url}")
        except Exception as e_cat:
            log(f"WARNING: Catbox.moe upload failed ({e_cat}). Trying Litterbox fallback...")
            
            # Fallback 2: Litterbox
            litter_url = "https://litterbox.catbox.moe/resources/internals/api.php"
            payload_litter = {
                "reqtype": "fileupload",
                "time": "24h"
            }
            try:
                with open(file_path, "rb") as f:
                    files = {"fileToUpload": f}
                    res = requests.post(litter_url, data=payload_litter, files=files, timeout=90)
                res.raise_for_status()
                direct_url = res.text.strip()
                if direct_url.startswith("https://"):
                    log(f"Direct temporary Litterbox stream link generated:\n{direct_url}")
                    return direct_url
                else:
                    raise Exception(f"Litterbox returned unexpected response: {direct_url}")
            except Exception as ex:
                log(f"ERROR: All public CDN uploads failed ({ex}).")
                return None

def post_to_tiktok_via_buffer(video_url, quote_text):
    log("Connecting to Buffer API to post to TikTok...")
    
    raw_caption = quote_text.split("\n\n")[0].replace("\"", "")
    social_caption = f"\"{raw_caption}\" 💡✨ #motivation #inspiration #mindset #quotes #success #growth #fyp"
    
    # Try Modern GraphQL API First (Mandatory for new accounts in 2026)
    try:
        log("Attempting to connect via Buffer's modern GraphQL API...")
        graphql_url = "https://api.buffer.com"
        gql_headers = {
            "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Get Organization ID
        org_query = {
            "query": """
            query GetOrganizations {
              account {
                organizations {
                  id
                  name
                }
              }
            }
            """
        }
        org_res = requests.post(graphql_url, headers=gql_headers, json=org_query, timeout=20)
        
        # Check if GraphQL endpoint succeeded and recognized the token
        if org_res.status_code == 200:
            org_data = org_res.json()
            if "errors" not in org_data and "data" in org_data and org_data["data"].get("account"):
                log("Successfully authenticated with GraphQL API.")
                orgs = org_data["data"]["account"].get("organizations", [])
                if not orgs:
                    raise Exception("No organizations found connected to this Buffer account!")
                org_id = orgs[0]["id"]
                log(f"Found Organization: {orgs[0]['name']} (ID: {org_id})")
                
                # Step 2: Fetch connected social channels
                channels_query = {
                    "query": f"""
                    query GetChannels {{
                      channels(input: {{ organizationId: "{org_id}" }}) {{
                        id
                        name
                        service
                        displayName
                      }}
                    }}
                    """
                }
                c_res = requests.post(graphql_url, headers=gql_headers, json=channels_query, timeout=20)
                c_res.raise_for_status()
                channels = c_res.json()["data"]["channels"]
                
                tiktok_channel_id = None
                for c in channels:
                    service = c.get("service", "").lower()
                    if service == "tiktok":
                        tiktok_channel_id = c.get("id")
                        log(f"Found connected TikTok account: @{c.get('displayName')} (ID: {tiktok_channel_id})")
                        break
                
                if not tiktok_channel_id:
                    log("WARNING: No TikTok channel found. Checking for fallback channels (Instagram/YouTube)...")
                    for c in channels:
                        if c.get("service", "").lower() in ["instagram", "youtube"]:
                            tiktok_channel_id = c.get("id")
                            log(f"Using fallback profile: {c.get('service')} (ID: {tiktok_channel_id})")
                            break
                            
                if not tiktok_channel_id:
                    raise Exception("No TikTok, Instagram, or YouTube channel is connected to your Buffer account!")
                
                # Step 3: Create and schedule the post mutation
                create_post_mutation = {
                    "query": f"""
                    mutation CreatePost {{
                      createPost(input: {{
                        text: {json.dumps(social_caption)},
                        channelId: "{tiktok_channel_id}",
                        schedulingType: automatic,
                        mode: addToQueue,
                        assets: [
                          {{
                            video: {{
                              url: "{video_url}"
                            }}
                          }}
                        ]
                      }}) {{
                        ... on PostActionSuccess {{
                          post {{
                            id
                          }}
                        }}
                        ... on MutationError {{
                          message
                        }}
                      }}
                    }}
                    """
                }
                
                p_res = requests.post(graphql_url, headers=gql_headers, json=create_post_mutation, timeout=30)
                if p_res.status_code != 200:
                    log(f"GraphQL post mutation failed with status code {p_res.status_code}. Response: {p_res.text}")
                p_res.raise_for_status()
                p_data = p_res.json()
                
                if "errors" in p_data or (p_data.get("data") and p_data["data"].get("createPost", {}).get("message")):
                    msg = p_data.get("errors", [{}])[0].get("message") or p_data["data"]["createPost"]["message"]
                    raise Exception(f"GraphQL post mutation error: {msg}")
                    
                log("SUCCESS! Video successfully scheduled in Buffer queue via modern GraphQL API!")
                return True
            else:
                log("GraphQL authentication skipped or not supported for this token format.")
    except Exception as gql_err:
        log(f"GraphQL API attempt failed or returned error: {gql_err}")
        log("Switching to legacy REST API fallback...")

    # Fallback Option: Legacy REST API (For older registered Buffer developer accounts)
    try:
        rest_headers = {"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"}
        profiles_res = requests.get("https://api.bufferapp.com/1/profiles.json", headers=rest_headers, timeout=20)
        profiles_res.raise_for_status()
        profiles = profiles_res.json()
        
        tiktok_profile_id = None
        for p in profiles:
            service = p.get("service", "").lower()
            if service == "tiktok":
                tiktok_profile_id = p.get("id")
                profile_name = p.get("formatted_username")
                log(f"Found connected TikTok account: @{profile_name} (ID: {tiktok_profile_id})")
                break
                
        if not tiktok_profile_id:
            log("WARNING: No TikTok channel found. Checking for fallbacks (Instagram/YouTube)...")
            for p in profiles:
                if p.get("service", "").lower() in ["instagram", "youtube"]:
                    tiktok_profile_id = p.get("id")
                    log(f"Using fallback profile: {p.get('service')} (ID: {tiktok_profile_id})")
                    break
                    
        if not tiktok_profile_id:
            raise Exception("No TikTok profile was found connected to this Buffer account. Please add your TikTok account to Buffer!")
            
        post_payload = {
            "text": social_caption,
            "profile_ids[]": [tiktok_profile_id],
            "media[video]": video_url,
            "as_ap": True
        }
        
        log("Sending payload to Buffer REST API...")
        post_res = requests.post("https://api.bufferapp.com/1/updates/create.json", headers=rest_headers, data=post_payload, timeout=30)
        post_res.raise_for_status()
        
        log("SUCCESS! Video added to Buffer queue via legacy REST API!")
        return True
    except Exception as e:
        log(f"ERROR posting to Buffer API: {e}")
        return False

def clean_temp_files(delete_music=False):
    log("Cleaning up local temporary files...")
    temp_files = ["voiceover.mp3", "background.mp4", "quote_text.txt"]
    if delete_music:
        temp_files.append("music.ogg")
    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)
            log(f"Deleted: {f}")

# ==========================================
# MAIN EXECUTIVE PIPELINE EXECUTION
# ==========================================
if __name__ == "__main__":
    log("Starting TikTok Quotes Auto-Post Pipeline...")
    check_requirements()
    
    # 1. Select Quote
    quote = get_random_quote()
    
    # 2. Setup font
    font = download_font()
    
    # 3. Generate speech voice file
    generate_voiceover(quote, "voiceover.mp3")
    audio_dur = get_audio_duration("voiceover.mp3")
    
    # 4. Download background video (Mixkit Direct CDN or Pexels)
    download_background_video("background.mp4")
    
    # 4.5 Download default background music if not present
    music_downloaded = download_background_music("music.ogg")
    
    # 5. Render video locally via FFmpeg
    final_video = render_final_video(quote, font, audio_dur, "background.mp4", "voiceover.mp3", "final_post.mp4")
    
    # 6. Upload compiled video to free cloud hosting (GitHub Releases for public repos, public CDN for private/local)
    visibility = get_repository_visibility()
    direct_link = None
    
    if visibility == "public":
        direct_link = upload_to_github_releases(final_video)
        if not direct_link:
            log("GitHub Release upload failed. Trying public CDN fallback...")
            direct_link = upload_to_free_cdn(final_video)
    elif visibility == "private":
        log("GitHub Repository is PRIVATE. Release assets will NOT be accessible to Buffer.")
        log("Uploading video to public CDN instead...")
        direct_link = upload_to_free_cdn(final_video)
    else:
        # Local run
        if BUFFER_ACCESS_TOKEN and BUFFER_ACCESS_TOKEN != "dummy":
            log("Running locally with active Buffer token. Uploading to public CDN to post...")
            direct_link = upload_to_free_cdn(final_video)
        else:
            log("Running locally (skipping cloud hosting). Output saved as 'final_post.mp4'.")
    
    if direct_link:
        # 7. Post via Buffer API
        post_to_tiktok_via_buffer(direct_link, quote)
        
        # Clean up temporary work files
        clean_temp_files(delete_music=music_downloaded)
    else:
        log("Skipping automated post because direct public cloud link was not generated. Output video saved locally as 'final_post.mp4'.")
        # Clean up temporary files if they were downloaded during a skipped post run
        clean_temp_files(delete_music=music_downloaded)
    
    log("Pipeline successfully executed.")
