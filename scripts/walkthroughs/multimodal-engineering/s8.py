"""Part 13 · 01 Multimodal engineering (vision, voice, video): choosing models, time limits and steps for each modality.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Modalities  Start here: "Modern AI apps combine at least two of: seeing images, voice, making images, and making video. Multimodal engineering is choosing the right models, time limits, and steps for each one."
  2 Vision      Body, "Vision": "Native multimodal models (GPT-4o, Claude 4, Gemini 2.5, Qwen3-VL) take images directly. ... OCR-via-LLM ...: it beats Tesseract on messy photos, handwritten notes, and structured forms. Often no separate OCR step is needed." Document AI, chart extraction, visual Q&A.
  3 Voice       Body, "Voice agents": "A voice pipeline is STT (speech-to-text) → LLM → TTS (text-to-speech). Each stage has its own leading options:" and its table.
  4 Realtime    Same part: "Realtime APIs skip the chunky STT→LLM→TTS loop by streaming audio bidirectionally. Sub-500 ms turn-taking is now achievable. LiveKit and Vapi ship full agent frameworks on top of these."
  5 Images      Body, "Image generation": "The models differ in licence and in what they do best." and its table (Flux, SDXL / SD3, Imagen 3, DALL-E 3 / GPT-Image-1, Ideogram, Recraft, Reve).
  6 Add-ons     Same part: "Common workflow add-ons: ControlNet ...; LoRA ...; inpainting ...; IP-Adapter ... ComfyUI lets you wire these into reproducible pipelines."
  7 Video       Body, "Video generation": "They differ in clip length, built-in audio and resolution, in how well a character stays the same from shot to shot, and in price and speed." and its table.
  8 Pipelines   Body, "ComfyUI, Replicate, Fal for media pipelines": the three bullets.
  9 Remember    The sub-title, and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("app", "server", ("App", "অ্যাপ"), 380, 162),
    node("vision", "model", ("Vision", "ভিশন"), 110, 75),
    node("voice", "service", ("Voice", "ভয়েস"), 110, 250),
    node("imagegen", "tool", ("Image model", "ইমেজ মডেল"), 650, 75),
    node("videogen", "queue", ("Video model", "ভিডিও মডেল"), 650, 250),
    node("input", "note", ("Input", "ইনপুট"), 110, 162),
    node("output", "file", ("Output", "আউটপুট"), 650, 162),
    node("stt", "tool", ("STT", "STT"), 110, 162),
    node("llm", "model", ("LLM", "LLM"), 380, 162),
    node("tts", "tool", ("TTS", "TTS"), 650, 162),
    node("addon", "tool", ("Add-ons", "অ্যাড-অন"), 110, 162),
    node("host", "cdn", ("Hosted API", "হোস্টেড API"), 380, 162),
]

METRICS = [
    ("Modalities", "মোডালিটি"),
    ("Turn-taking", "পালা বদল"),
    ("Sora clip", "Sora ক্লিপ"),
]

CAPTION = (
    "Text was the first modality. Multimodal engineering is choosing the models, time limits, and steps for each of the others.",
    "টেক্সট ছিল প্রথম মোডালিটি। মাল্টিমোডাল ইঞ্জিনিয়ারিং মানে বাকিগুলোর প্রতিটির জন্য মডেল, সময়ের সীমা আর ধাপ বেছে নেওয়া।",
)

STEPS = [
    st(("Modalities", "মোডালিটি"),
       ("More than text", "শুধু টেক্সট নয়"),
       [("Modern AI apps combine at least two of: seeing images, voice, making images, and making video. Multimodal engineering is choosing the right models, time limits, and steps for each one.",
         "আজকের AI অ্যাপ অন্তত দুটি কাজ মেলায়: ছবি দেখা, ভয়েস, ছবি বানানো আর ভিডিও বানানো। মাল্টিমোডাল ইঞ্জিনিয়ারিং মানে প্রতিটির জন্য ঠিক মডেল, সময়ের সীমা আর ধাপ বেছে নেওয়া।")],
       [sh("app", "hot"), sh("vision", "hot", ("sees images", "ছবি দেখে")), sh("voice", "hot", ("hears and talks", "শোনে ও বলে")),
        sh("imagegen", "hot", ("makes images", "ছবি বানায়")), sh("videogen", "hot", ("makes video", "ভিডিও বানায়"))],
       [ln("app", "vision", "to", state="hot"), ln("app", "voice", "to", state="hot"), ln("app", "imagegen", "to", state="hot"), ln("app", "videogen", "to", state="hot")],
       [("at least two", "অন্তত দুটি"), None, None]),

    st(("Vision", "ভিশন"),
       ("Models that see", "যে মডেল দেখে"),
       [("Native multimodal models (GPT-4o, Claude 4, Gemini 2.5, Qwen3-VL) take images directly.",
         "GPT-4o, Claude 4, Gemini 2.5, Qwen3-VL-এর মতো নেটিভ মাল্টিমোডাল মডেল সরাসরি ছবি নেয়।"),
        ("OCR-via-LLM beats Tesseract on messy photos, handwritten notes, and structured forms, and often needs no separate OCR step.",
         "OCR-via-LLM অগোছালো ছবি, হাতের লেখা নোট আর কাঠামোবদ্ধ ফর্মে Tesseract-কে ছাড়িয়ে যায়, আর প্রায়ই আলাদা OCR ধাপের দরকার হয় না।")],
       [sh("input", "hot", ("an image", "একটি ছবি")), sh("vision", "hot", ("takes images", "ছবি নেয়"), None, 380, 162), sh("output", "hot", ("text or JSON", "টেক্সট বা JSON"))],
       [ln("input", "vision", "to", state="hot"), ln("vision", "output", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Document AI: PDF understanding with layout awareness (Claude, Mistral OCR, Qwen2-VL)",
                 "ডকুমেন্ট AI: লেআউট বুঝে PDF পড়া (Claude, Mistral OCR, Qwen2-VL)"),
                ("+", "Chart and diagram extraction: ask the model to read a chart and emit JSON",
                 "চার্ট ও ডায়াগ্রাম থেকে ডেটা বের করা: মডেলকে চার্ট পড়ে JSON দিতে বলুন"),
                ("+", "Visual Q&amp;A: “what's wrong with this screenshot?”",
                 "ভিজ্যুয়াল Q&amp;A: “এই স্ক্রিনশটে কী ভুল?”")]),

    st(("Voice", "ভয়েস"),
       ("The voice pipeline", "ভয়েস পাইপলাইন"),
       [("A voice pipeline is STT (speech-to-text) → LLM → TTS (text-to-speech). Each stage has its own leading options:",
         "ভয়েস পাইপলাইন হলো STT (স্পিচ-টু-টেক্সট) → LLM → TTS (টেক্সট-টু-স্পিচ)। প্রতিটি ধাপের নিজস্ব সেরা বিকল্প আছে:")],
       [sh("stt", "hot", ("speech to text", "কথা থেকে লেখা")), sh("llm", "hot", ("the reply", "উত্তর")), sh("tts", "hot", ("text to speech", "লেখা থেকে কথা"))],
       [ln("stt", "llm", "to", state="hot"), ln("llm", "tts", "to", state="hot")],
       [None, None, None],
       changes=[("+", "STT: Whisper, Deepgram, AssemblyAI, ElevenLabs Scribe",
                 "STT: Whisper, Deepgram, AssemblyAI, ElevenLabs Scribe"),
                ("+", "TTS: ElevenLabs, Cartesia, OpenAI TTS, PlayHT",
                 "TTS: ElevenLabs, Cartesia, OpenAI TTS, PlayHT")]),

    st(("Realtime", "রিয়েলটাইম"),
       ("Realtime APIs", "রিয়েলটাইম API"),
       [("Realtime APIs skip the chunky STT→LLM→TTS loop by streaming audio in both directions. Sub-500 ms turn-taking is now achievable.",
         "রিয়েলটাইম API ধাপে ধাপে STT→LLM→TTS লুপ বাদ দিয়ে দুই দিকেই অডিও স্ট্রিম করে। এখন ৫০০ ms-এর কমে পালা বদল সম্ভব।")],
       [sh("input", "hot", ("the caller", "কলকারী")), sh("voice", "hot", ("streams both ways", "দুই দিকে স্ট্রিম"), None, 380, 162)],
       [ln("input", "voice", "both", state="hot")],
       [None, ("sub-500 ms", "৫০০ ms-এর কমে"), None],
       note=("tip",
             "Options include the OpenAI Realtime API, LiveKit Agents, Vapi, Retell, and Daily. LiveKit and Vapi ship full agent frameworks on top of these.",
             "বিকল্পের মধ্যে আছে OpenAI Realtime API, LiveKit Agents, Vapi, Retell আর Daily। LiveKit আর Vapi এগুলোর ওপর পূর্ণ এজেন্ট ফ্রেমওয়ার্ক দেয়।")),

    st(("Images", "ছবি"),
       ("Image models", "ইমেজ মডেল"),
       [("The models differ in license and in what they do best. Open models can be fine-tuned, for example with LoRA; others lead on photorealism, on following instructions, or on typography and design.",
         "মডেলগুলো লাইসেন্সে আর কোনটা সবচেয়ে ভালো করে তাতে আলাদা। ওপেন মডেল ফাইন-টিউন করা যায়, যেমন LoRA দিয়ে; অন্যগুলো ফটোরিয়ালিজম, নির্দেশ মানা, বা টাইপোগ্রাফি আর ডিজাইনে এগিয়ে।")],
       [sh("input", "hot", ("a prompt", "একটি প্রম্পট")), sh("imagegen", "hot", ("pick by strengths", "গুণ দেখে বাছুন"), None, 380, 162), sh("output", "hot", ("an image", "একটি ছবি"))],
       [ln("input", "imagegen", "to", state="hot"), ln("imagegen", "output", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Flux (Black Forest Labs): open-weights availability, strong prompt fidelity",
                 "Flux (Black Forest Labs): ওপেন-ওয়েটস, প্রম্পটের প্রতি দৃঢ় বিশ্বস্ততা"),
                ("+", "SDXL / SD3 (Stability): open, fine-tuneable with LoRA",
                 "SDXL / SD3 (Stability): ওপেন, LoRA দিয়ে ফাইন-টিউন করা যায়"),
                ("+", "Imagen 3 (Google): photorealism, available via Vertex",
                 "Imagen 3 (Google): ফটোরিয়ালিজম, Vertex-এ পাওয়া যায়"),
                ("+", "DALL-E 3 / GPT-Image-1 (OpenAI): polished, instruction-following",
                 "DALL-E 3 / GPT-Image-1 (OpenAI): পরিপাটি, নির্দেশ-অনুসারী"),
                ("+", "Ideogram, Recraft, Reve: typography and design-oriented",
                 "Ideogram, Recraft, Reve: টাইপোগ্রাফি আর ডিজাইনমুখী")]),

    st(("Add-ons", "অ্যাড-অন"),
       ("Workflow add-ons", "ওয়ার্কফ্লোর অ্যাড-অন"),
       [("These common add-ons shape how an image is generated. ComfyUI lets you wire them into reproducible pipelines.",
         "এই প্রচলিত অ্যাড-অনগুলো ঠিক করে ছবি কীভাবে তৈরি হবে। ComfyUI দিয়ে এগুলোকে বারবার চালানো যায় এমন পাইপলাইনে জুড়ে দেওয়া যায়।")],
       [sh("addon", "hot", ("ControlNet, LoRA", "ControlNet, LoRA")), sh("imagegen", "hot", ("makes images", "ছবি বানায়"), None, 380, 162), sh("output", "hot", ("an image", "একটি ছবি"))],
       [ln("addon", "imagegen", "to", state="hot"), ln("imagegen", "output", "to", state="hot")],
       [None, None, None],
       changes=[("+", "ControlNet conditions the image on a structure: a pose, a depth map, or canny edges (an edge-detected outline)",
                 "ControlNet ছবিকে একটি কাঠামো মানতে বাধ্য করে: পোজ, ডেপথ ম্যাপ বা ক্যানি এজ (কিনারা-শনাক্ত রেখাচিত্র)"),
                ("+", "LoRA adds a small trained adapter for a style or a consistent character",
                 "LoRA একটি স্টাইল বা একই চরিত্রের জন্য ছোট প্রশিক্ষিত অ্যাডাপ্টার যোগ করে"),
                ("+", "Inpainting regenerates only a masked part of an image, for edits",
                 "ইনপেইন্টিং ছবির শুধু মাস্ক করা অংশ আবার বানায়, এডিটের জন্য"),
                ("+", "IP-Adapter uses a reference image as part of the prompt",
                 "IP-Adapter একটি রেফারেন্স ছবিকে প্রম্পটের অংশ হিসেবে ব্যবহার করে")]),

    st(("Video", "ভিডিও"),
       ("Video models", "ভিডিও মডেল"),
       [("Video models differ in clip length, built-in audio and resolution, in how well a character stays the same from shot to shot, and in price and speed.",
         "ভিডিও মডেলগুলো ক্লিপের দৈর্ঘ্য, বিল্ট-ইন অডিও আর রেজোলিউশনে, এক শট থেকে আরেক শটে চরিত্র কতটা একই থাকে তাতে, আর দাম ও গতিতে আলাদা।")],
       [sh("input", "hot", ("a prompt", "একটি প্রম্পট")), sh("videogen", "hot", ("length, audio", "দৈর্ঘ্য, অডিও"), None, 380, 162), sh("output", "hot", ("a clip", "একটি ক্লিপ"))],
       [ln("input", "videogen", "to", state="hot"), ln("videogen", "output", "to", state="hot")],
       [None, None, ("up to 20 s", "২০ সেকেন্ড পর্যন্ত")],
       changes=[("+", "Sora (OpenAI): up to 20 s, strong physics",
                 "Sora (OpenAI): ২০ সেকেন্ড পর্যন্ত, শক্তিশালী ফিজিক্স"),
                ("+", "Veo 3 (Google): native audio + 4K, prompt-adherent",
                 "Veo 3 (Google): নেটিভ অডিও + 4K, প্রম্পট-অনুসারী"),
                ("+", "Runway Gen-4: reference-image continuity for character",
                 "Runway Gen-4: চরিত্রের জন্য রেফারেন্স-ছবির ধারাবাহিকতা"),
                ("+", "Kling 2.0 (Kuaishou): long-form, motion quality",
                 "Kling 2.0 (Kuaishou): দীর্ঘ ক্লিপ, গতির মান"),
                ("+", "Pika, Luma, Hailuo: smaller, cheaper, faster",
                 "Pika, Luma, Hailuo: ছোট, সস্তা, দ্রুত")]),

    st(("Pipelines", "পাইপলাইন"),
       ("Tools for media pipelines", "মিডিয়া পাইপলাইনের টুল"),
       [("These tools cover media pipelines:",
         "মিডিয়া পাইপলাইনের জন্য এই টুলগুলো:")],
       [sh("app", "hot", None, None, 110, 162), sh("host", "hot", ("Replicate, Fal", "Replicate, Fal")), sh("output", "hot", ("the result", "ফলাফল"))],
       [ln("app", "host", "to", state="hot"), ln("host", "output", "to", state="hot")],
       [None, None, None],
       changes=[("+", "ComfyUI: a node-based UI for Stable Diffusion and Flux workflows, the “Figma for diffusion”; production teams version-control the JSON graphs",
                 "ComfyUI: Stable Diffusion আর Flux ওয়ার্কফ্লোর নোড-ভিত্তিক UI, “ডিফিউশনের জন্য Figma”; প্রোডাকশন টিম JSON গ্রাফের ভার্সন-কন্ট্রোল রাখে"),
                ("+", "Replicate: a pay-per-second API for any open-source model, the fastest way to deploy something you found on Hugging Face",
                 "Replicate: যেকোনো ওপেন-সোর্স মডেলের জন্য প্রতি-সেকেন্ডের API; Hugging Face-এ পাওয়া কিছু ডিপ্লয় করার দ্রুততম উপায়"),
                ("+", "Fal: fast hosted inference for diffusion, with streaming partial results",
                 "Fal: ডিফিউশনের জন্য দ্রুত হোস্টেড ইনফারেন্স, আংশিক ফল স্ট্রিম করে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Multimodal engineering is the discipline of choosing models, latency budgets, and pipelines for each modality.",
         "মাল্টিমোডাল ইঞ্জিনিয়ারিং মানে প্রতিটির জন্য মডেল, ল্যাটেন্সি বাজেট আর পাইপলাইন বেছে নেওয়ার কাজ।")],
       [sh("app"), sh("vision"), sh("voice"), sh("imagegen"), sh("videogen")],
       [ln("app", "vision", "to"), ln("app", "voice", "to"), ln("app", "imagegen", "to"), ln("app", "videogen", "to")],
       [None, None, None],
       points=[("In 2025, every production AI app combines at least two of vision, voice, image generation, and video generation.",
                "২০২৫-এ প্রতিটি প্রোডাকশন AI অ্যাপ ভিশন, ভয়েস, ইমেজ জেনারেশন আর ভিডিও জেনারেশনের অন্তত দুটি মেলায়।"),
               ("Models that take images directly often need no separate OCR step, and they beat Tesseract on messy photos.",
                "যে মডেল সরাসরি ছবি নেয়, তার প্রায়ই আলাদা OCR ধাপ লাগে না। অগোছালো ছবিতে সে Tesseract-কে হারায়।"),
               ("A voice pipeline is STT → LLM → TTS. Realtime APIs stream audio both ways instead.",
                "ভয়েস পাইপলাইন হলো STT → LLM → TTS। রিয়েলটাইম API তার বদলে দুই দিকে অডিও স্ট্রিম করে।"),
               ("Pick image and video models by what you need: license, photorealism, clip length, character consistency, price, and speed.",
                "প্রয়োজন দেখে ইমেজ ও ভিডিও মডেল বাছুন: লাইসেন্স, ফটোরিয়ালিজম, ক্লিপের দৈর্ঘ্য, চরিত্রের ধারাবাহিকতা, দাম আর গতি।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
