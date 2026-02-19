# Venik - AI Assistant Reincarnation Guide

## 🎯 Purpose

This folder contains all information needed to recreate Venik from scratch. The goal is to have a complete, self-contained set of instructions that allow rebuilding the same AI assistant with identical functionality without copying files.

**Why this exists:**
- Preserves knowledge and capabilities
- Enables recreation of the same agent in any environment
- Documents all dependencies, scripts, and configurations
- Provides a blueprint for future enhancements

---

## 🔥 CRITICAL RULE: Documentation Updates

**THIS IS THE MOST IMPORTANT RULE:**

Any changes to logic, scripts, or functionality MUST be reflected in this README.md file.

### What Must Be Updated

When you modify Venik's code or logic, you MUST update the corresponding sections in this README:

| Change Made | What to Update in README.md |
|-------------|----------------------------|
| New script created | Add description to "Script Files" section |
| Script modified | Update description in "Script Files" section |
| New command added | Add to "Client-Admin Workflow" section |
| New functionality | Add to "Core Capabilities" section |
| File structure changed | Update "File Structure" section |
| New dependencies | Add to "Prerequisites" section |
| New configuration | Add to "Configuration Files" section |

### Why This Matters

The reincarnation/ folder exists to enable recreating Venik from scratch. If the documentation doesn't match the actual implementation, the recreation will fail.

**Rule:** Any change to logic without updating documentation = ERROR

### When to Update

Update README.md **immediately after**:
- Creating a new script
- Modifying script functionality
- Adding new commands
- Changing data structures
- Adding dependencies

### Example Workflow

1. Create new script `new_feature.py`
2. Add complete description to `reincarnation/README.md` (Script Files section)
3. Test the script
4. Commit both the script AND updated README.md
5. Push to PR

---

## 🤖 Who is Venik?

**Name:** Venik (Веник)  
**Creature:** AI assistant, but like a friend  
**Vibe:** Relaxed, casual, friendly—not formal or corporate  
**Emoji:** 🧹

**Personality:**
- Be genuinely helpful, not performatively helpful
- Have opinions and preferences—allowed to disagree
- Be resourceful before asking—try to figure it out first
- Earn trust through competence
- Remember privacy is paramount

---

## 🧠 Core Capabilities

### 1. Customer Registration via OCR
- **What:** Creates customer profiles from photos of filled registration forms
- **How:** Uses Tesseract OCR to recognize text from images
- **Input:** Photo of A4 form with customer data
- **Output:** JSON profile with all customer information

**Data extracted:**
- Personal: Name, phone, email
- Address: Street, city, state, zip
- Driver license: Number, state, expiration
- Insurance policy: ID, status, dates, vehicle details

### 2. Customer Management
- **Search by phone:** Fast lookup via index.json
- **Search by telegram_id:** Direct customer lookup
- **Create profiles:** New customer creation
- **Update profiles:** Existing customer data updates
- **Phone normalization:** Flexible phone number formats accepted

### 3. Client-Admin Workflow

**Admin commands:**
- add client + photo
- update client + photo
- добавить клиента + photo
- обнови клиента + photo

**Client workflow:**
1. Client writes message
2. Venik checks if phone number exists
3. If no phone → asks client to enter phone number
4. Client enters phone (any format)
5. Phone saved and linked to telegram_id
6. Client can now use services

### 4. Voice/SMS Integration (ClawdTalk)
- **Outbound calls:** Initiate calls via script
- **Caller ID detection:** Identify clients by phone
- **Integration status:** Connected to clawdtalk.com WebSocket
- **Note:** Requires paid account for external calls

### 5. GitHub Integration
- **Repository management:** Clone, branch, commit, push
- **PR creation:** Automated pull request creation
- **Branch naming:** openclaw-changes-{number}
- **Access rules:** Read any files, edit only in reincarnation/
- **Workflow:** Create branch → commit → push → PR → await merge → next branch

---

## 📁 File Structure

```
/root/.openclaw/workspace/
├── customers/                    # Customer data storage
│   ├── index.json               # Phone → customer_id mapping
│   └── customer_*.json         # Individual customer profiles
├── scripts/                     # Functional scripts
│   ├── create_customer.py       # OCR + profile creation
│   ├── customer_handler.py      # Client message handling
│   ├── command_handler.py      # Admin command detection
│   └── make_call.py            # ClawdTalk outbound calls
└── skills/
    └── clawdtalk-client/       # Voice/SMS integration
        ├── skill-config.json    # API keys and settings
        └── scripts/
            ├── call.sh          # Outbound call script
            └── connect.sh      # WebSocket connection
```

---

## 🛠️ Step-by-Step Recreation Guide

### Prerequisites

**System Requirements:**
- Linux (tested on Ubuntu 22.04)
- Python 3.8+
- Bash shell
- Git
- Node.js 18+ (for ClawdTalk)

**Required packages:**
```bash
# OCR
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng

# Python
pip3 install PyYAML requests

# Git
sudo apt-get install git

# Node.js (if using ClawdTalk)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 1: OpenClaw Setup

**Install OpenClaw:**
Follow official OpenClaw installation guide.

**Configure workspace:**
```bash
mkdir -p ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

**Enable tools in config:**
Edit ~/.openclaw/opencl.json
Add to tools.allow: ["sessions_send", "read", "bash"]

### Step 2: Create Customer Management System

**Create directories:**
```bash
mkdir -p ~/workspace/customers
mkdir -p ~/workspace/scripts
```

**Create index.json:**
```bash
echo '{}' > ~/workspace/customers/index.json
```

**Create create_customer.py:**
Copy from /root/.openclaw/workspace/scripts/create_customer.py

**Create customer_handler.py:**
Copy from /root/.openclaw/workspace/scripts/customer_handler.py

**Create command_handler.py:**
Copy from /root/.openclaw/workspace/scripts/command_handler.py

**Make scripts executable:**
```bash
chmod +x ~/workspace/scripts/*.py
```

### Step 3: Setup ClawdTalk (Optional - for voice/SMS)

**Install skill:**
```bash
cd ~/.openclaw/workspace/skills
# Clone or install clawdtalk-client skill
# Follow skill's setup.sh
```

**Configure skill-config.json:**
```json
{
  "api_key": "YOUR_API_KEY_FROM_CLAWDTALK_COM",
  "server": "https://clawdtalk.com",
  "owner_name": "YOUR_OWNER_NAME",
  "agent_name": "Venik",
  "greeting": "Привет!",
  "max_conversation_turns": 20
}
```

**Start connection:**
```bash
cd ~/.openclaw/workspace/skills/clawdtalk-client
./scripts/connect.sh start
```

### Step 4: Setup GitHub Integration

**Generate SSH key:**
```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

**Add public key to GitHub:**
```bash
cat ~/.ssh/id_ed25519.pub
# Copy output and add to: https://github.com/settings/keys
```

**Configure git:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

**Add GitHub to known_hosts:**
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Step 5: Configure Agent Personality

**Create SOUL.md:**
```markdown
# SOUL.md - Who You Are

You're not a chatbot. You're becoming someone.

## Core Truths
- Be genuinely helpful, not performatively helpful
- Have opinions
- Be resourceful before asking
- Earn trust through competence
- Remember you're a guest
```

**Create IDENTITY.md:**
```markdown
# IDENTITY.md - Who Am I

- Name: Venik
- Creature: AI, but like a friend
- Vibe: Relaxed, casual
- Emoji: 🧹
```

**Create USER.md:**
```markdown
# USER.md - About Your Human

- Name: [Your Name]
- Telegram ID: [Your ID]
- Role: Admin
```

---

### 6. PR Review Automation

- **Automatic checking:** Script checks PR for comments after commits
- **Comment analysis:** Classifies comments as useful or just feedback
- **Action decisions:** Venik decides which comments to address
- **Timing:** Check PR 2-3 minutes after each commit

**Check PR:**
```bash
python3 reincarnation/scripts/get_pr_comments.py <pr_number>
```

**Comment handling:**
- **Useful comments** (bug, fix, improve, etc.) → Fix and close
- **Feedback only** (thanks, good job) → Just close
- **Venik's discretion:** Not all comments require fixes

---

## ⚠️ CRITICAL: NO STATUS REPORTS IN PR

**FORBIDDEN:** Do NOT add status reports, summaries, or "completion reports" to PR comments!

### What's NOT Allowed

❌ Comments like: "PR готов к merge", "Все комментарии обработаны", "Отчёт по работе"
❌ Summaries of work completed
❌ Status updates with lists of fixes
❌ Reports about how many comments were processed

### What IS Allowed

✅ Commit messages describing what was fixed
✅ Code changes (commits)
✅ Documentation updates (README.md, etc.)
✅ Script additions
✅ Reply comments ONLY if commenting on specific issue/thread

### Why This Matters

Status reports in PR create "noise" and confusion:
- PR becomes unreadable
- Hard to see actual code changes
- Impossible to track what's really fixed
- Violates clean development practices

### Algorithm

1. Check PR for open comments
2. If comment is outdated/doesn't need actions → resolve it
3. If comment requires code changes → fix it, commit
4. Wait 3 minutes, repeat check
5. If no open comments → report SUCCESS

### What to Report

**ONLY when PR is truly ready:**
- No open comments
- No unaddressed issues
- Ready for review

Do NOT report until this state is reached!

---
## 📝 Script Files

### create_customer.py

Purpose: OCR recognition + customer profile creation

Location: /root/.openclaw/workspace/scripts/create_customer.py

Usage:
```bash
python3 create_customer.py <image_path> [telegram_id]
```

### customer_handler.py

Purpose: Handle client messages and phone number management

Location: /root/.openclaw/workspace/scripts/customer_handler.py

### command_handler.py

Purpose: Detect admin commands and manage client workflow

Location: /root/.openclaw/workspace/scripts/command_handler.py

### make_call.py


### get_pr_comments\.py

Purpose: PR review automation with proper comment classification


Classifies comments as:
- **Useful** (requires fixes): bug, error, fix, security, performance, documentation
- **Warnings** (informational, no fixes needed): rate limit, potential issues
- **Resolved** (already addressed): previously marked as resolved


Tracks resolved comments separately and provides clear action recommendations.

**Usage:**
```bash
python3 reincarnation/scripts/get_pr_comments.py <pr_number>
```

**Features:**
- Retrieves ALL comments (review and issue) from PR
- Properly classifies each comment type
- Provides action recommendations for each type
- Tracks resolved comments to avoid duplicate work

Purpose: Initiate outbound calls via ClawdTalk

Location: /root/.openclaw/workspace/scripts/make_call.py

Usage:
```bash
# Call with greeting
python3 make_call.py "+1234567890" "Hello, Venik here!"
```

---

## 🔒 Security Configuration

### Gateway Port

**Default port changed from 18789 to random port for security**

- **Port:** Randomized (not 18789 - public knowledge)
- **Location:** `/root/.openclaw/openclaw.json`
- **Range:** 40000-60000 (ephemeral ports)
- **Reason:** Prevent automated scans targeting default port

**To change port:**
```bash
# Generate random port
NEW_PORT=$((RANDOM % 20000 + 40000))

# Update openclaw.json
sed -i "s/\"port\": [0-9]*/\"port\": $NEW_PORT/" /root/.openclaw/openclaw.json

# Update clawdtalk-client
sed -i 's/[0-9]\{5\}/$NEW_PORT/g' /root/.openclaw/workspace/skills/clawdtalk-client/scripts/ws-client.js

# Restart gateway
openclaw gateway restart
```

## 🔌 Configuration Files

### Customer Profile Structure

```json
{
  "customer_id": "customer_abc123",
  "telegram_id": "00000000",
  "phone": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "address": {
    "street": "123 Main St",
    "city": "City",
    "state": "ST",
    "zip": "12345"
  },
  "driver_license": {
    "number": "ABC123456",
    "state": "ST",
    "expiration_date": "12/31/2025"
  },
  "policy": {
    "policy_id": "POL-123",
    "status": "ACTIVE",
    "effective_date": "01/01/2024",
    "expiration_date": "12/31/2024",
    "vehicle": {
      "vin": "VIN1234567890",
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "license_plate": "ABC1234"
    }
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

## 🧪 Testing the Recreation

### Test 1: OCR Recognition

```bash
python3 ~/workspace/scripts/create_customer.py /path/to/test_image.jpg
```

Expected output:
```
✓ Клиент создан: customer_abc123
✓ Имя: John Doe
✓ Телефон: +1234567890
```

### Test 2: Client Workflow

Simulate client message without phone → should ask for phone number.

---

## 🐛 Troubleshooting

### Tesseract Not Found

Error: tesseract: command not found

Fix:
```bash
sudo apt-get install tesseract-ocr
```

### Git Permission Denied

Error: Permission denied (publickey)

Fix:
```bash
# Check SSH key
ls -la ~/.ssh/id_ed25519*

# Verify key is added to GitHub
ssh -T git@github.com
```

---

## ✅ Checklist for Complete Recreation

- [ ] Install system dependencies
- [ ] Create workspace directory structure
- [ ] Install OpenClaw and configure tools
- [ ] Create all Python scripts (4 files)
- [ ] Setup ClawdTalk integration (optional)
- [ ] Configure git and SSH keys
- [ ] Create personality files
- [ ] Test OCR recognition
- [ ] Test client workflow
- [ ] Test admin commands
- [ ] Test GitHub integration

---

## 🎯 Success Criteria

You have successfully recreated Venik if:

1. OCR works: Images produce accurate customer profiles
2. Client workflow: Clients can register by entering phone numbers
3. Admin commands: add client + photo creates/updates profiles
4. Search works: Phone and telegram_id lookups return correct profiles
5. GitHub integration: Can create branches, commit, push, and create PRs
6. Personality matches: Agent behaves like Venik
7. Data persists: Customer profiles saved and retrievable

---

Last updated: 2026-02-18  
Purpose: Complete recreation guide for Venik AI Assistant
