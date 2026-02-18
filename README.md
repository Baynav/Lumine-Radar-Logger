🌙 Lumine Radar Logger
Lightweight OCR Event Logger for Lumine Proxy (Minecraft Bedrock)
<p align="center"> <img src="pixel_cat.ico" width="120" alt="Pixel Cat Logo"> </p> <p align="center"> <b>Session-based radar logging • Spatial dedupe • Low CPU • Standalone EXE</b> </p>
🚀 Overview

Lumine Radar Logger is a lightweight Windows utility that reads Lumine Proxy radar output directly from your Minecraft Bedrock chat.

The logger creates clean, filtered session logs while keeping your main gameplay unaffected.

⚠️ IMPORTANT – READ BEFORE USING

This logger is intended for an idling alt account.

It works by reading Lumine’s radar output directly from your Minecraft chat window.

❗ The chat window MUST remain open at all times.
❗ It will NOT work if chat is closed.

Because Lumine Radar continuously outputs events to chat, running this on your main account while playing is not recommended.

🔮 Future update may support background logging without chat open.

⚙️ Required Minecraft Settings

For coordinate accuracy, the following settings are mandatory.

📝 Chat Settings

Open Chat

Click the ⚙️ (Cogwheel)

Set:
Font	Noto Sans
Size	12
Line Spacing	x1.0
♿ Accessibility Settings

Open Minecraft Settings

Go to Accessibility

Scroll down

Set:
GUI Scale Modifier	-1

These values ensure consistent pixel rendering for coordinate accuracy.

🛠 How To Use

Create a secondary Windows user and log in

Launch Minecraft through the Lumine Proxy on your Alt Account

Join your server

Make sure /.radar is enabled

Open chat and KEEP IT OPEN

Run Lumine Radar Logger

Select the Chat View Area

Then click "Start"

While Chat is open use "Windows Key + L"

Log back into your main Windows user profile

Play normally on your Main account

**This prevents chat spam from affecting gameplay.**

📁 Logs

Logs are created per session.

A logs/ folder is automatically generated in the same directory as the .exe.

Each session creates:

logs/session_YYYY-MM-DD_HH-MM-SS.log

❌ It Will NOT Work If

Chat is closed

Font is not Noto Sans

GUI scale is not -1

Chat size differs from required values

Radar is not enabled

The Chat View Area is incorrect

🛡 Security Note

This application:

Does NOT inject into Minecraft

Does NOT modify memory

Does NOT hook processes

Only reads screen pixels

🧠 How It Works

The logger:

🧾 Extracts event type + coordinates from chat

🔍 Uses Spatial deduplication for the output

📍 Applies spatial filtering to prevent spam

🗂 Creates clean session-based log files

All processing is:

✅ 100% Local

✅ No network transmission

✅ No Minecraft modification

📦 Distribution

The distributed ZIP contains:

LumineRadarLogger.exe

**No additional installs required.**

🔮 Planned Features

Background logging without chat open

CSV export

Event-type filtering

Heatmap generation

📜 License

Personal use tool built for Lumine Proxy radar users.

🌙 Final Notes

If logging appears inaccurate:

Re-check Minecraft settings

Re-select capture region

Ensure chat is fully visible

Confirm radar is enabled

<p align="center"> <b>Created by Baynav with Love <3</b> </p>
