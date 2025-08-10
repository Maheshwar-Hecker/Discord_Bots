# 🤖 Discord_Bots
*Python-powered bots that understand desi slang, emote like humans, and keep your server lively.*

---

## 1) Puneet Superstar Bot ✨

> “Are kaisa hai yaar, masti karein?” – Puneet Superstar

### 🚀 Why Use This Bot?
| 🌟 Feature | What It Does |
|-----------|--------------|
| 🧠 **Emotion Engine** | Switches moods (peaceful 😌 ➜ angry 😡 ➜ chaotic 🤪) for varied replies |
| 🔥 **/roast Command** | Hilarious, India-centric burns at one slash |
| 🇮🇳 **Colloquial Chat** | Understands Hinglish & regional slang for *relatable* banter |
| 🕵️ **Message-Delete Sniper** | Responds when someone stealth-deletes a message |

---

### 🏗️ How It Works
1. **Mood Scheduler** – Background task flips `current_mood` every few minutes.  
2. **Slash Commands** – Built with *discord.py 2.x* interactions.  
3. **Event Listeners** – `on_member_join`, `on_message`, `on_message_delete`.  
4. **Response Templates** – Localized arrays for each mood to keep code DRY.

---

### 🛠️ Getting Started

#### Prerequisites
- Python 3.8+
- A Discord server & bot token

#### Installation
```

git clone https://github.com/Maheshwar-Hecker/Discord_Bots.git
cd Discord_Bots
pip install -r requirements.txt
export DISCORDTOKEN2="your_bot_token_here"
python discord_BOT.py

```

---

### 📝 Commands
| Slash | Purpose | Example |
|-------|---------|---------|
| `/roast` | Throw shade at a user | `/roast @username` |
| `/mood`  | Show bot’s current mood | `/mood` |
| `/peace` | Force peaceful mode | `/peace` |

---

### 💬 Example Interaction
```

User : Hello Puneet!
Bot  : Oye! Kya haal chaal? 😄

User : /roast @Mahesh
Bot  : @Mahesh, tu software update jaise hai—sab dekh ke kehte “Not now” 😂

```

---

### 🤝 Contributing
1. Fork the repo & create a feature branch.  
2. Commit your changes with conventional commits.  
3. Open a PR—screenshots/gif demos welcome!

---

### 📄 License
MIT – see [`LICENSE`](LICENSE).

---

**Thanks for trying Puneet Superstar!** Drop issues, ideas, or just *“Aur roast chahiye”* in the repo discussions. Let’s make Discord more *paisa-vasool* together! 🇮🇳🎉
```


