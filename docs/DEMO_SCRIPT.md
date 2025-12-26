# Demo Video Script

**Target Length**: 3-5 minutes  
**Format**: Screen recording with voiceover  
**Focus**: Problem → Solution → Live Demo → Impact

---

## Hook (15 seconds)

> "What if children could recognize risky chat patterns themselves, without anyone watching over their shoulder? ChatCompanion is a privacy-first tool that helps kids ages 10-16 identify bullying, manipulation, and grooming—all while keeping their conversations completely private and offline."

**Visual**: Show app logo or title screen

---

## Problem (30 seconds)

> "Children and teenagers face increasing risks online: bullying, manipulation, emotional pressure, secrecy demands, and grooming. Most existing solutions either require cloud uploads—which means someone else sees the conversations—or they're designed for surveillance rather than empowerment."

**Visual**: 
- Show statistics or problem statement
- Transition to solution

---

## Live Demo Flow (2-3 minutes)

### Part 1: Setup (20 seconds)

> "Let me show you how it works. First, I'll clone the repository and set it up. The setup takes about 5 minutes, and after that, everything runs completely offline."

**Visual**: 
- Show terminal with git clone
- Show pip install (fast-forward if needed)
- Show streamlit run command
- Browser opens to app

### Part 2: Safe Conversation - GREEN (30 seconds)

> "Let's start with a safe conversation. I'll paste a friendly chat between two friends. [Paste chat] Now I'll click 'Analyze Chat'... and we see a GREEN indicator. The explanation says 'No warning signs detected.' This is exactly what we want—the system correctly identifies safe, friendly communication."

**Visual**:
- Paste safe chat example
- Click "Analyze Chat"
- Show GREEN traffic light
- Show explanation: "No warning signs detected"
- Highlight that it's clean and supportive

### Part 3: Concerning Patterns - YELLOW (40 seconds)

> "Now let's try a conversation with some concerning patterns. [Paste chat with pressure/guilt] This conversation shows pressure and guilt-making language. When I analyze it... we see a YELLOW indicator. The explanation says 'Something feels a bit off' and mentions the specific patterns detected—pressure and guilt-making language. Notice how it's calm and supportive, not scary."

**Visual**:
- Paste YELLOW chat example
- Click "Analyze Chat"
- Show YELLOW traffic light
- Show explanation with specific patterns
- Highlight child-friendly language
- Show that "Need Immediate Help?" does NOT appear (only for RED)

### Part 4: High-Risk Situation - RED (50 seconds)

> "Finally, let's look at a high-risk situation. [Paste chat with coercion/secrecy/threats] This conversation shows multiple red flags: secrecy demands, manipulation, and threats. When I analyze it... we see a RED indicator. The explanation clearly describes what was detected, and importantly, the 'Need Immediate Help?' section appears. This is the only time this section appears—only for truly high-risk situations."

**Visual**:
- Paste RED chat example
- Click "Analyze Chat"
- Show RED traffic light
- Show explanation with evidence
- Show "Need Immediate Help?" expander (expand it)
- Highlight that this only appears for RED
- Show help resources

### Part 5: Privacy & Offline (20 seconds)

> "Throughout all of this, notice that no data was uploaded anywhere. Everything happens locally on your device. The analysis is instant, private, and completely offline. This is the core of ChatCompanion—privacy-first empowerment, not surveillance."

**Visual**:
- Show network tab (no requests)
- Highlight offline capability
- Show privacy guarantees

---

## Why It Matters (30 seconds)

> "ChatCompanion puts children in control. Instead of surveilling them or requiring cloud uploads, it gives them the tools to recognize risky patterns themselves. It's explainable—children understand what was detected and why. It's supportive—no shaming, no scaring, just helpful guidance. And it's private—their conversations never leave their device."

**Visual**:
- Show key features: Privacy, Explainability, Child-Friendly
- Show impact: Empowerment, Safety, Autonomy

---

## Wrap-up + Call to Action (15 seconds)

> "ChatCompanion is open source, fully documented, and ready to help children navigate online communication safely. Check out the repository, try it yourself, and let's work together to make the internet safer for kids. Thank you!"

**Visual**:
- Show repository link
- Show GitHub badge
- Show "Built for CodeSpring Hackathon"

---

## Key Points to Emphasize

1. **Privacy-first**: No cloud uploads, no surveillance
2. **Explainable**: Children understand what was detected and why
3. **Child-friendly**: Calm, supportive language, not scary
4. **Offline**: Works completely offline after setup
5. **Evidence-based**: Explanations match actual detected patterns
6. **Traffic light system**: Intuitive green/yellow/red indicators

---

## Demo Chat Examples to Use

### GREEN Example
Use: `demo_data/chats/safe_chat.txt` or `mild_teasing.txt`
- Shows friendly conversation
- Demonstrates no false positives

### YELLOW Example
Use: `demo_data/chats/manipulation_pressure.txt` or `manipulation_example.txt`
- Shows pressure/guilt patterns
- Demonstrates threat-gating (no threats mentioned unless present)

### RED Example
Use: `demo_data/chats/grooming_example.txt` or create one with:
- Secrecy demands
- Manipulation
- Threats/ultimatums
- Demonstrates "Need Immediate Help?" section

---

## Production Notes

- **Recording**: Use screen recording software (OBS, QuickTime, etc.)
- **Audio**: Clear voiceover, no background noise
- **Pacing**: Don't rush—let viewers see the UI clearly
- **Transitions**: Smooth cuts between sections
- **Text Overlays**: Add key points as text overlays if helpful
- **Music**: Optional, but keep it subtle if used

---

## Post-Production Checklist

- [ ] Add title card with project name
- [ ] Add transitions between sections
- [ ] Add text overlays for key points
- [ ] Ensure audio is clear and balanced
- [ ] Verify all demo chats work correctly
- [ ] Check that traffic lights are clearly visible
- [ ] Verify "Need Immediate Help?" only appears for RED
- [ ] Add end card with repository link
- [ ] Export in high quality (1080p minimum)
- [ ] Upload to YouTube or Devpost

---

**Total Estimated Time**: 3-4 minutes (allowing for natural pacing)

