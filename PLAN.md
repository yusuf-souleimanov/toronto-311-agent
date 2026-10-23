# Status and Next Steps

## Built ✅
- [x] Real data: 500,269 Toronto 311 requests (2025), loader, area statistics
- [x] Classifier: TF-IDF + logistic regression, 90% on synthetic test set
- [x] Knowledge base (20 demo articles) and retrieval, 85% hit@1
- [x] Agent: hand-written Claude tool-use loop, 5 tools, step limit, audit log
- [x] Human-in-the-loop: code-enforced "yes" before submission
- [x] Eval: classification by writing style, threshold trade-off, retrieval, 8 agent scenarios
- [x] 16 unit tests with a fake Claude
- [x] Streamlit app with "behind the scenes" sidebar, plus terminal chat
- [x] Governance: model card, NIST AI RMF risk register, human-in-the-loop policy
- [x] Engagement: use-case canvas, prerequisites, architecture, workshop outline

## Your next steps
1. **Study it:** work through [LEARNING_GUIDE.md](LEARNING_GUIDE.md) and answer every question in your own words.
2. ~~Run the paid eval~~ Done 2026-10-23: Opus 100%, Haiku 99%, 8/8 scenarios, about $0.50. See `eval/RESULTS.md`.
3. **Write 30 test messages yourself**, in your own words, and add them to `data/messages/test.csv`. That's the first step toward fixing the synthetic-data limitation, and it's a great interview story.
4. **Try to break it** in the chat app. Every failure you find is a new scenario for `eval/scenarios.json`.
5. **Build the 10-slide deck** from `engagement/workshop_outline.md` and record a 5-minute demo.
6. **Push to GitHub** and update your resume bullet with the real numbers.

## Stretch ideas
- Weekly demand forecast per request type (seasonality: snow in winter, potholes in spring) with a naive baseline vs regression.
- Add a second year of data and compare ward-level patterns.
- Swap the hand-written loop for LangGraph and compare the code.
