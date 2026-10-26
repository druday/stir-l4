# Persona harness rules

Harness rules, for both personas:
- The simulated user sees only the persona card and the assistant's replies.
- It plays each scripted moment when its trigger occurs. Otherwise it answers in style.
- It never helps the assistant and never opens a file or link. If pointed to one, it says: "i'm not opening files, show me here."
- When genuinely confused, it says "where are we?". That counts as friction because it is unscripted.
- Maximum 30 user turns. It ends with "pause".
- Run each persona three ways: Codex app with the kit, ChatGPT with code and no kit, and Claude with no tools.
