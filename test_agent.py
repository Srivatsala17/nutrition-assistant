from core.agent import build_agent, chat

USER_ID = 1  # change to your id

agent = build_agent(USER_ID)

questions = [
    "I had 2 rotis and dal for lunch",
    "Suggest a high protein dinner under 300 calories",
    "How was my week so far?",
]

for q in questions:
    print("\nYOU:", q)
    print("BOT:", chat(agent, USER_ID, q))