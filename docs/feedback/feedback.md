# User Feedback — Quote Auto Poster

* **How collected:** Discord Direct Messages (DMs) with user Wint Theingi Aung
* **When:** July 4, 2026

## Raw feedback

1. **Voice Customization:** The user asked if it's possible to change the voice style and wondered if they could choose between male and female voice options ("voice က တစ်မျိုးပဲ ရတာလား အစ်မ၊ male, female voice ကော choice လို့ရလား အစ်မ").
2. **Content Generation Variety / Multi-Content:** The user asked if the system could handle multi-content or different genres of content rather than just a single stream ("multi content ရနိုင်မလား အစ်မ၊ ကဏ္ဍအစုံပေါ့နော်").
3. **Localized/Burmese Language Support:** As an extension of the content variety request, the user specifically suggested adding support for Burmese language content and Burmese quotes ("ဥပမာ - မြန်မာစာကား၊ မြန်မာ quote တွေကော").

## Themes (what keeps coming up)

* **Hardcoded Media Generation Parameters:** The automated pipeline successfully picks random video backgrounds and overlays quotes with voiceovers, but the voice selection is currently rigid. The code needs parameters to cleanly switch between voice types.
* **Single-Niche Limitation:** The script is optimized for a singular type of content. It needs a structural refactor to support multiple categories, tags, or folders so it can cycle through or target different content niches programmatically.

## Top 3 things to fix

- [ ] **Parameterize TTS Voice Selection:** Update the TTS engine module (e.g., `edge-tts` configuration) to accept a dynamic voice ID parameter so you can switch between male and female voice tokens via your code's config or environment variables.
- [ ] **Implement Multi-Content Array / Folder Structure:** Refactor the codebase to support an array of content categories or separate directories for asset sourcing. This will allow the script to cycle through or accept arguments for different content genres ("ကဏ္ဍအစုံ").
- [ ] **Add Burmese Script & Font Rendering Support:** Ensure the video processing engine (like MoviePy) is configured with a Unicode-compliant font (such as Pyidaungsu) to cleanly render Burmese text overlays without breaking, and add a module to parse Burmese text datasets.
