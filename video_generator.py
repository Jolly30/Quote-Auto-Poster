import os
import sys
import json
import random
import requests
import subprocess
import textwrap
from datetime import datetime
import db_utils

# ==========================================
# CONFIGURATION & API KEYS FROM ENVIRONMENT
# ==========================================
# Unique compliant User-Agent to bypass Wikimedia and public CDN bot throttling (429/403)
HEADERS = {
    "User-Agent": "TikTokQuotesAutoPoster/1.0 (https://github.com/Jolly30/quote-auto-poster; contact@example.com) PythonRequests/2.31"
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
# VIDEO DURATION & MUSIC OPTIONS
# ==========================================
# Video duration in seconds (10 seconds is aesthetic and optimal for TikTok quote videos)
VIDEO_DURATION = int(os.environ.get("VIDEO_DURATION", "10"))

# Background music volume (e.g. "0.8" for clean, full background music sound)
MUSIC_VOLUME = float(os.environ.get("MUSIC_VOLUME", "0.8"))

# ==========================================
# TEXT CAPTIONS & STYLING OPTIONS
# ==========================================
# Default base font size (automatically scales down for long quotes to prevent crowding)
FONT_SIZE = int(os.environ.get("FONT_SIZE", "58"))

# Aesthetic font color (warm golden yellow: 0xFFDE59 or yellow)
FONT_COLOR = os.environ.get("FONT_COLOR", "0xFFDE59")

# Max character width per line before wrapping (24-26 is optimal for clean mobile viewing)
TEXT_WRAP_WIDTH = int(os.environ.get("TEXT_WRAP_WIDTH", "25"))

# ==========================================
# 100% FREE, DIRECT, UNLIMITED VERTICAL VIDEOS
# ==========================================
# Direct high-quality stock portrait MP4 CDN URLs from Mixkit.
# Requires ZERO API keys, ZERO registrations, and has absolutely NO download limits!
# Direct high-quality stock portrait MP4 CDN URLs (peaceful nature, serene rivers, rain, starry nights)
DIRECT_VIDEO_URLS = [
    "https://assets.mixkit.co/videos/preview/mixkit-starry-night-sky-over-a-silent-river-portrait-42861-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-vertical-shot-of-the-night-sky-with-stars-and-clouds-42934-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-rain-falling-on-a-window-at-night-portrait-42999-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-night-sky-with-shining-stars-portrait-42862-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-calm-river-with-green-trees-portrait-42930-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-raindrops-on-green-leaves-portrait-43243-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-fog-over-a-green-mountain-landscape-portrait-43224-large.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-sun-setting-over-the-ocean-horizon-portrait-42928-large.mp4"
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
            # Build curl command with fast connection and download timeouts
            cmd = ["curl", "-L", "-f", "-s", "--connect-timeout", "15", "--max-time", "60", "-o", output_path]
            # Use standard desktop browser User-Agent to ensure highest compatibility
            cmd.extend(["-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"])
            if headers:
                for k, v in headers.items():
                    cmd.extend(["-H", f"{k}: {v}"])
            cmd.append(url)
            
            subprocess.run(cmd, check=True, timeout=65)
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

# Curated cinematic search terms focused on Myanmar culture, environment, and high-aesthetic landscapes
PEXELS_SEARCH_TERMS = [
    "Bagan pagoda sunrise vertical aesthetic",
    "Myanmar golden hour temple vertical",
    "Inle lake fishermen sunset cinematic vertical",
    "Buddhist temple candles aesthetic vertical",
    "Southeast Asia misty mountains morning vertical",
    "Asian rain on green leaves cinematic vertical",
    "Bagan hot air balloons sunrise portrait 4k",
    "Monk walking ancient pagoda vertical cinematic",
    "Mandalay bridge sunset reflection vertical",
    "peaceful Asian countryside river foggy vertical",
    "ancient temple ruins nature vertical aesthetic",
    "tropical rainforest waterfall vertical aesthetic"
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

# Audio extensions supported for background music
AUDIO_EXTENSIONS = ('.mp3', '.m4a', '.ogg', '.wav', '.aac', '.flac')

def is_burmese_text(text):
    """Detect if text contains Myanmar (Burmese) Unicode characters."""
    for char in text:
        if '\u1000' <= char <= '\u109F':
            return True
    return False

def get_random_quote(category=None):
    log("Selecting quote from SQLite database...")
    try:
        quote_data = db_utils.get_least_used_quote(category=category)
        if not quote_data:
            raise Exception("No quotes found in database.")
        
        quote_text = quote_data["quote"]
        quote_id = quote_data["id"]
        quote_category = quote_data.get("category", "general")
        
        # In the video, only show the pure quote text (no quotation marks, clean and direct)
        display_text = quote_text.strip()
        log(f"Selected Quote [{quote_category}]: {display_text}")
        
        # Mark as used
        db_utils.mark_quote_used(quote_id)
        
        return display_text, quote_id, quote_category
    except Exception as e:
        log(f"ERROR reading from database: {e}")
        fallback_text = "Bananas are curved because they grow towards the sun against gravity."
        return fallback_text, None, "general"

def download_font():
    # 1. Prioritize local custom font files (fonts/ folder or root)
    custom_fonts = [
        os.path.join("fonts", "font.ttf"),
        "font.ttf",
        "ရိုးရာ_Regular (2).ttf"
    ]
    for font_path in custom_fonts:
        if os.path.exists(font_path):
            log(f"Custom font detected: {font_path}")
            return font_path
    
    log("Downloading premium modern font (Montserrat)...")
    font_path = os.path.join("fonts", "font.ttf") if os.path.isdir("fonts") else "font.ttf"
    url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"
    if download_file(url, font_path):
        log("Font downloaded successfully.")
        return font_path
    else:
        log("WARNING: Could not download Montserrat font. Falling back to system default.")
        return "Arial"

def download_background_video(output_file="background.mp4", category=None):
    """
    Selects or downloads a background video focused on Myanmar culture/environment:
    1. Checks local 'videos/' folder (or 'videos/<category>/') for user-provided Myanmar clips.
    2. Searches Pexels for Myanmar, Bagan, pagodas, Asian nature & culture.
    3. Falls back to curated peaceful nature/river direct CDN clips.
    """
    import shutil
    video_extensions = ('.mp4', '.mov', '.m4v', '.webm')
    local_candidates = []

    # Check category subfolder (e.g. videos/romance, videos/sad)
    if category:
        cat_folder = os.path.join("videos", category)
        if os.path.isdir(cat_folder):
            local_candidates.extend([
                os.path.join(cat_folder, f) for f in os.listdir(cat_folder)
                if f.lower().endswith(video_extensions) and not f.startswith(".")
            ])

    # Check root videos folder
    if os.path.isdir("videos"):
        local_candidates.extend([
            os.path.join("videos", f) for f in os.listdir("videos")
            if f.lower().endswith(video_extensions) and not f.startswith(".")
        ])

    if local_candidates:
        chosen = random.choice(local_candidates)
        log(f"Using local Myanmar background video: {chosen}")
        shutil.copy2(chosen, output_file)
        return output_file

    # If Pexels key is provided, search Pexels for Myanmar / pagoda / Asian nature
    if PEXELS_API_KEY:
        search_term = random.choice(PEXELS_SEARCH_TERMS)
        log(f"PEXELS_API_KEY detected. Searching Pexels for '{search_term}'...")
        headers = {"Authorization": PEXELS_API_KEY}
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
                    log(f"Downloading Myanmar-themed background from Pexels ({search_term})...")
                    if download_file(download_url, output_file, headers=headers):
                        log("Pexels background video downloaded successfully.")
                        return output_file
        except Exception as e:
            log(f"Pexels API download failed ({e}). Falling back to free direct serene CDN...")

    # Primary or Fallback Option: Mixkit Direct CDN URLs (100% Free, Unlimited, Keyless)
    log("Accessing 100% Free Direct serene nature vertical video CDN...")
    download_url = random.choice(DIRECT_VIDEO_URLS)
    
    if download_file(download_url, output_file):
        log("Background video downloaded successfully with ZERO keys!")
        return output_file
    else:
        log("Creating vertical gradient background as final safety fallback...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:d=30",
            "-vf", "noise=alls=10:allf=t+u", "-pix_fmt", "yuv420p", output_file
        ], check=True)
        log("Safety vertical background generated.")
        return output_file

def get_category_music(category=None):
    """
    Finds a random music track from the corresponding category folder
    (e.g., 'music/romance', 'romance', 'music/sad', 'sad', etc.).
    Falls back to any local music in music/ or root or any category folder.
    """
    category_folders = []
    if category:
        cat_lower = category.lower().strip()
        category_folders.extend([
            os.path.join("music", cat_lower),
            cat_lower
        ])
        if cat_lower == "motivation":
            category_folders.extend([os.path.join("music", "motivate"), "motivate"])
        elif cat_lower == "motivate":
            category_folders.extend([os.path.join("music", "motivation"), "motivation"])
            
    for folder in category_folders:
        if os.path.isdir(folder):
            tracks = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if f.lower().endswith(AUDIO_EXTENSIONS) and not f.startswith(".")
            ]
            if tracks:
                chosen = random.choice(tracks)
                log(f"Selected category background music from [{folder}]: {chosen}")
                return chosen

    # Check music/ root or project root for music files
    for base_dir in ["music", "."]:
        if os.path.isdir(base_dir):
            for f in os.listdir(base_dir):
                if f.lower().startswith("music.") and f.lower().endswith(AUDIO_EXTENSIONS):
                    chosen = os.path.join(base_dir, f) if base_dir != "." else f
                    log(f"Using general music file: {chosen}")
                    return chosen

    # Fallback to any track from any category folder
    all_tracks = []
    for base_dir in ["music", "."]:
        for d in ["romance", "sad", "motivate", "motivation", "neutral"]:
            target_dir = os.path.join(base_dir, d) if base_dir != "." else d
            if os.path.isdir(target_dir):
                all_tracks.extend([
                    os.path.join(target_dir, f) for f in os.listdir(target_dir)
                    if f.lower().endswith(AUDIO_EXTENSIONS) and not f.startswith(".")
                ])
            
    if all_tracks:
        chosen = random.choice(all_tracks)
        log(f"Selected fallback background music: {chosen}")
        return chosen

    return None

def download_background_music(output_file="music.ogg"):
    """
    Downloads a random royalty-free background track from the curated direct CDN list
    if there is no local music file found.
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

def render_final_video(quote_text, font_path, video_file="background.mp4", output_file="final_post.mp4", music_file=None, duration=VIDEO_DURATION):
    log(f"Compiling final video ({duration}s) with stylized centered captions using FFmpeg...")
    
    # Word wrap lines for clean vertical framing on phone screens
    wrapped_lines = []
    paragraphs = quote_text.split('\n\n')
    for p in paragraphs:
        if p.startswith("—"):
            wrapped_lines.append(p)
        else:
            wrapped_lines.extend(textwrap.wrap(p, width=TEXT_WRAP_WIDTH))
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
    
    # Auto-scale font size based on the number of wrapped lines to keep the layout perfectly balanced
    num_lines = len(wrapped_lines)
    dynamic_font_size = FONT_SIZE
    if num_lines >= 6:
        dynamic_font_size = max(38, int(FONT_SIZE * 0.65))  # scale down by 35% for very long quotes
    elif num_lines >= 4:
        dynamic_font_size = max(44, int(FONT_SIZE * 0.82))  # scale down by 18% for medium-long quotes
        
    # High-aesthetic typography styling:
    # 1. Warm aesthetic yellow font color with soft drop shadow + subtle outline
    # 2. line_spacing=22 gives Myanmar vowels and tone diacritics ample breathing room without clipping
    # 3. y=(h-text_h)/2-50 safely positions the quote above TikTok's bottom captions/music bar
    style_filter = f"fontsize={dynamic_font_size}:fontcolor={FONT_COLOR}:shadowcolor=black@0.85:shadowx=3:shadowy=4:borderw=2:bordercolor=black@0.6:x=(w-text_w)/2:y=(h-text_h)/2-50:line_spacing=22:expansion=none"
    
    if ":" in font_path:
        font_path_escaped = font_path.replace(":", "\\:")
        if os.path.exists(quote_file):
            font_filter = f"fontfile='{font_path_escaped}':textfile='{quote_file}'"
        else:
            font_filter = f"fontfile='{font_path_escaped}':text='{escaped_text}'"

    if not music_file:
        if os.path.exists("music.mp3"):
            music_file = "music.mp3"
        elif os.path.exists("music.ogg"):
            music_file = "music.ogg"
        
    has_music = music_file is not None

    # Cinematic video pipeline:
    # 1. scale & crop to perfect 1080x1920 vertical format without distortion
    # 2. eq: subtle moody contrast & rich saturation boost so text pops like a movie frame
    # 3. drawtext: elegant styled typography overlay
    video_filter = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.10:contrast=1.12:saturation=1.15,drawtext={font_filter}:{style_filter}"
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", video_file
    ]
    if has_music:
        log(f"Aesthetic background music ({music_file}) selected. Mixing into final video...")
        cmd.extend(["-stream_loop", "-1", "-i", music_file])
        
    cmd.extend([
        "-t", str(duration),
        "-vf", video_filter
    ])
    if has_music:
        # Smooth cinematic audio fade-in (1.0s) and fade-out (2.0s)
        fade_start = max(1.0, duration - 2.0)
        cmd.extend([
            "-filter_complex", f"[1:a]volume={MUSIC_VOLUME},afade=t=in:ss=0:d=1.0,afade=t=out:st={fade_start:.1f}:d=2.0[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_file
        ])
    else:
        cmd.extend([
            "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
            "-pix_fmt", "yuv420p",
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
                "-stream_loop", "-1", "-i", video_file
            ]
            if has_music:
                fallback_cmd.extend(["-stream_loop", "-1", "-i", music_file])
                
            fallback_video_filter = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.10:contrast=1.12:saturation=1.15,drawtext={fallback_text_filter}:fontsize={dynamic_font_size - 4}:fontcolor={FONT_COLOR}:shadowcolor=black@0.85:shadowx=3:shadowy=4:borderw=2:bordercolor=black@0.6:x=(w-text_w)/2:y=(h-text_h)/2-50:line_spacing=22:expansion=none"
            fallback_cmd.extend([
                "-t", str(duration),
                "-vf", fallback_video_filter
            ])
            if has_music:
                fade_start = max(1.0, duration - 2.0)
                fallback_cmd.extend([
                    "-filter_complex", f"[1:a]volume={MUSIC_VOLUME},afade=t=in:ss=0:d=1.0,afade=t=out:st={fade_start:.1f}:d=2.0[a]",
                    "-map", "0:v",
                    "-map", "[a]",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    output_file
                ])
            else:
                fallback_cmd.extend([
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    output_file
                ])
            subprocess.run(fallback_cmd, check=True)
            log("Fallback video successfully rendered.")
            return output_file
        except Exception as ex:
            log(f"WARNING: Fallback text rendering failed ({ex}).")
            log("Attempting final fallback (no captions, background video + music)...")
            try:
                no_caption_cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "-1", "-i", video_file
                ]
                if has_music:
                    no_caption_cmd.extend(["-stream_loop", "-1", "-i", music_file])
                    
                no_caption_cmd.extend([
                    "-t", str(duration),
                    "-vf", "scale=1080:1920"
                ])
                if has_music:
                    fade_start = max(1.0, duration - 1.5)
                    no_caption_cmd.extend([
                        "-filter_complex", f"[1:a]volume={MUSIC_VOLUME},afade=t=out:st={fade_start:.1f}:d=1.5[a]",
                        "-map", "0:v",
                        "-map", "[a]",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                        output_file
                    ])
                else:
                    no_caption_cmd.extend([
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
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
    log("Uploading compiled video to Catbox.moe (100% Free Permanent Public CDN)...")
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
        log(f"WARNING: Catbox.moe upload failed ({e_cat}). Trying Tmpfiles.org fallback...")
        
        # Fallback 1: Tmpfiles.org with 48h expiration (maximum)
        log("Uploading compiled video to Tmpfiles.org (48-Hour Fallback CDN)...")
        url_tmpfiles = "https://tmpfiles.org/api/v1/upload"
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {"expire": "172800"}  # 48 hours in seconds (maximum allowed)
                res = requests.post(url_tmpfiles, files=files, data=data, timeout=90)
            res.raise_for_status()
            data = res.json()
            if data.get("status") == "success":
                upload_url = data["data"]["url"]
                # Convert standard URL to direct download URL
                direct_url = upload_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                log(f"Direct public stream link generated successfully via Tmpfiles (expires in 48h):\n{direct_url}")
                return direct_url
            else:
                raise Exception(f"Tmpfiles returned error status: {data}")
        except Exception as e_tmp:
            log(f"WARNING: Tmpfiles.org upload failed ({e_tmp}). Trying Litterbox fallback...")
            
            # Fallback 2: Litterbox (Temporary 24h upload)
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
                    log(f"Direct temporary Litterbox stream link generated (expires in 24h):\n{direct_url}")
                    return direct_url
                else:
                    raise Exception(f"Litterbox returned unexpected response: {direct_url}")
            except Exception as ex:
                log(f"ERROR: All public CDN uploads failed ({ex}).")
                return None


def generate_caption_and_hashtags(category="general"):
    """
    Generates TikTok post caption containing ONLY hashtags (user's #fyp #စာတို + viral tags).
    """
    # Base core hashtags (including user specified #fyp and #စာတို)
    base_tags = ["#fyp", "#စာတို", "#foryou", "#foryoupage", "#tiktokmyanmar", "#myanmar", "#aesthetic", "#quotes"]
    
    cat = (category or "").lower().strip()
    if cat == "romance":
        cat_tags = ["#အချစ်", "#crush", "#lovequotes", "#romance", "#feelings"]
    elif cat == "sad":
        cat_tags = ["#sad", "#ဝမ်းနည်းခြင်း", "#နာကျင်မှု", "#brokenheart", "#lonely", "#ခံစားချက်"]
    elif cat in ("motivate", "motivation"):
        cat_tags = ["#motivation", "#ခွန်အား", "#အောင်မြင်မှု", "#ကြိုးစားမှု", "#mindset", "#success"]
    elif cat == "neutral":
        cat_tags = ["#peaceful", "#အေးချမ်းမှု", "#chill", "#life", "#relax", "#စိတ်အေးချမ်းမှု"]
    else:
        cat_tags = ["#စာပေ", "#trending"]

    all_tags = base_tags + cat_tags
    return " ".join(all_tags)

def post_to_tiktok_via_buffer(video_url, quote_text, category="general"):
    log("Connecting to Buffer API to post to TikTok...")
    
    social_caption = generate_caption_and_hashtags(category=category)
    log(f"Generated TikTok Caption & Hashtags:\n{social_caption}")
    
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
    temp_files = ["background.mp4", "quote_text.txt"]
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
    
    # 1. Select Quote (with category)
    quote_display, quote_id, quote_category = get_random_quote()
    
    # 2. Setup font
    font = download_font()
    
    # 3. Select background video (local Myanmar video, or Pexels Myanmar culture search)
    download_background_video("background.mp4", category=quote_category)
    
    # 4. Select matching category background music (or download default if none exists)
    selected_music = get_category_music(quote_category)
    music_downloaded = False
    if not selected_music:
        music_downloaded = download_background_music("music.ogg")
        if os.path.exists("music.ogg"):
            selected_music = "music.ogg"
    
    # 5. Render video locally via FFmpeg with custom font, background video & music
    final_video = render_final_video(quote_display, font, video_file="background.mp4", output_file="final_post.mp4", music_file=selected_music, duration=VIDEO_DURATION)
    
    # 6. Upload compiled video to free cloud hosting
    direct_link = None
    
    if BUFFER_ACCESS_TOKEN and BUFFER_ACCESS_TOKEN != "dummy":
        is_public_repo = False
        if GITHUB_TOKEN and GITHUB_REPOSITORY:
            visibility = get_repository_visibility()
            if visibility == "public":
                is_public_repo = True
                log("GitHub Repository is PUBLIC. Attempting to host video on GitHub Releases (Premium stable CDN)...")
                try:
                    direct_link = upload_to_github_releases(final_video)
                    if direct_link:
                        log(f"Using high-speed GitHub Release URL for Buffer: {direct_link}")
                except Exception as e:
                    log(f"WARNING: GitHub Release upload failed ({e}). Falling back to public CDN...")
        
        # Fallback to public CDN if not running on GitHub, or if repo is private, or if Release upload failed
        if not direct_link:
            log("Uploading video to public CDN (Catbox/Tmpfiles) for Buffer compatibility...")
            direct_link = upload_to_free_cdn(final_video)
            
            # Archive a copy on GitHub Releases as backup if we haven't uploaded it there yet
            if GITHUB_TOKEN and GITHUB_REPOSITORY and not is_public_repo:
                try:
                    log("Archiving a copy of the video in GitHub Releases...")
                    upload_to_github_releases(final_video)
                except Exception as archive_err:
                    log(f"WARNING: Could not archive video in GitHub Releases: {archive_err}")
    else:
        log("Running locally (skipping cloud hosting). Output saved as 'final_post.mp4'.")
    
    if direct_link:
        # 7. Post via Buffer API with aesthetic category hashtags
        post_to_tiktok_via_buffer(direct_link, quote_display, category=quote_category)
        
        if quote_id:
            db_utils.record_post(quote_id, video_path="final_post.mp4", cdn_url=direct_link, status="posted")
            
        # Clean up temporary work files
        clean_temp_files(delete_music=music_downloaded)
    else:
        log("Skipping automated post because direct public cloud link was not generated. Output video saved locally as 'final_post.mp4'.")
        # Clean up temporary files if they were downloaded during a skipped post run
        clean_temp_files(delete_music=music_downloaded)
    
    log("Pipeline successfully executed.")
