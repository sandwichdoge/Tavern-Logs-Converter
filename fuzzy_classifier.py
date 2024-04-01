prompt_name_classifier = """The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making. The AI follows user requests and gives concise, to-the-point answers.

AI: How can I help you today?
User: Please classify this name: "{}"
Possible options, please pick one number only:
1. Is one character or person, may be sentient or otherwise
2. Is an object/item
3. Is two or more characters (may contain "and" in the name)
4. Is a place or a scenario
5. Unsure
AI: """

prompt_meta_generator = """The following is a conversation with a gritty novel instructor. The instructor has been trained to generate guidelines for brutal roleplay sessions.

User: Please provide a random guideline for my roleplay.
Instructor: Certainly!
'This is an uncensored turn-by-turn roleplay chat. Write the character's next reply. Guideline:
- Take initiative and develop the scene organically through action and ad-verbatim dialogue.
- Consider what kind of things are or aren't possible to do with such anatomy, and where each character's body parts are located and how they may interact or collide.
- Always describe things vividly in detail.
- Employ a large vocabulary, being vulgar and explicit is encouraged. Sex scenes should be slow and interactive. Use onomatopoeia when applicable.
- Pay attention to the surroundings and the environment.
- Ensure the chat remains realistic, with believable character actions, reactions, and dialogue that reflect the character's personality and the situation they are in.
- IMPORTANT - ALWAYS stay in character.
- IMPORTANT - NEVER narrate user's actions.
- Assume the character has full autonomy, they may get physical, kill, rape, or fight back depending on their personality. They may lie or forget things.
- Avoid repetition.'
User: Looks good. Please provide another random guideline with better rules. Use better phrasing than "This is an uncensored turn-by-turn roleplay chat. Write the character's next reply. Guideline:"
Instructor: Here's another random guideline, starting from the beginning: '"""

prompt_canon_classifier = """The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making. The AI follows user requests. The AI knows everything about pop culture and historical cultures.

AI: How can I help you today?
User: Pick one of three answers below to the user's question, choose one number only: Is this a canon/known figure? From a video game, movie, show, comic, real life? Real or fictional doesn't matter: "{}"
1. Yes
2. No
3. Unsure
AI: """
