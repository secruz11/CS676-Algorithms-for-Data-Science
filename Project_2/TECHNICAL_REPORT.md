# Project 2: PersonaForge

**CS676**

## 1. Introduction

PersonaForge is an application built from a Python package. It allows users to create characters and have them talk to each other to see what comes of it. Large language models (LLMs) are used to create the responses from the given character traits. These personas are then saved as Markdown files with information on the characters' backgrounds. The original application was given as a working skeleton that required code modifications to improve its functionality. A limitation of this skeleton was its dependence on regex-based routing to analyze user requests. In Project #2, Claude's tool-calling functionality was implemented to assist in this limitation. This allowed models to choose the correct action based on what the user asked.

## 2. Design and Implementation

Since the original orchestrator.py used regular expressions (regex) to interpret requests through specific patterns, it was limited when requests did not follow the expected format. One suggested improvement from the assignment was to replace this routing approach with real tool calling. Rather than searching for specific keywords, the updated orchestrator provides Claude with available tools, allowing the model to determine which action best matches the user's request.

Three tool definitions were added to orchestrator.py for Claude to choose from based on what the user is requesting. The first addition was create_persona, which creates and saves a new persona based on a description provided by the user. The second addition was list_personas, which retrieves a list of personas that have previously been created. The final addition was start_conversation, which begins a conversation between the selected personas about a topic of the user's choice. The conversation tool also supports optional shared context and a specified number of turns. This functionality was implemented by adding the create_message() method to llm.py to enable Claude's tool calling. Once Claude selects a tool, the orchestrator executes the requested action. The result is then returned to Claude, which can generate a response or request another action. The tool-execution loop has a maximum of 10 iterations to prevent unlimited tool calls.

The original regex-based router was not removed completely but was instead kept as a fallback option. If the language model does not support the create_message() method, the application uses the original routing approach. This allows the application to continue supporting offline testing through ScriptedLLM. Error handling was also added to address potential problems with Claude API communication and tool execution. Instead of the application crashing, it returns an error message if these operations fail. Additionally, improvements were made to persona management by preventing saved conversation transcripts from appearing in the persona list. There was also an issue with longer persona names being shortened, which was corrected to preserve the full names of the generated personas.

## 3. Beta Testing and Saved Transcript

The testing scenario included testing PersonaForge with two AI-generated personas. The first persona was Elena Rivera, a neurologist specializing in Alzheimer's disease. The second persona was Maya Thompson, a daughter caring for her mother with advanced Alzheimer's disease. The conversation centered on advanced dementia, reduced food intake, feeding tubes, comfort feeding, and hospice care. An eight-turn conversation between the two characters was generated. What worked well was that both personas actively participated in the conversation. The dialogue remained centered on the intended topic of Alzheimer's disease. As the conversation evolved, related issues were discussed rather than repeating the same questions. The neurologist responded from a medical perspective, while the caregiver raised practical and emotional concerns. This conversation was saved in a Markdown file. This demonstrated that the application could generate a complete multi-agent conversation and that both personas maintained distinct roles throughout the discussion. Additionally, the complete eight-turn conversation is provided in Appendix A.

## 4. Honest Failure Analysis

Although the updated PersonaForge application had the ability to generate conversations between personas, some issues did arise during development and testing. One issue was that saved conversation transcripts appeared in the persona list because both were stored as Markdown files. This was corrected so that only actual persona files would appear. Another issue involved longer persona names being shortened, which was also fixed. Additionally, while the final conversation remained consistent with the personas' roles, some of the medical information was presented with too much certainty, which was inappropriate given the medical context. For example, Elena made definitive statements about feeding tubes and their effects on survival without fully acknowledging individual differences or uncertainty. This demonstrates that even when AI-generated conversations appear realistic, the information may not always be completely accurate or appropriately qualified. Another limitation is that the application depends on Claude's API for live tool calling, which requires an internet connection and may involve usage costs. Future improvements could focus on monitoring generated responses for appropriate content safety and API usage.

## 5. Test Coverage

Throughout the development of the application, testing was continuously conducted to ensure it worked correctly. Pytest was used to run automated tests, with a total of 60 tests passing. The three tools mentioned above, create_persona, list_personas, and start_conversation, were added for tool-calling functionality. The application was tested to verify that it could execute requests through the updated system. Additional tests were added to ensure that conversation transcripts did not appear in the persona list and that longer persona names were preserved correctly. These tests helped confirm that the changes made to the application did not interfere with existing functionality. Offline compatibility was also confirmed using ScriptedLLM, allowing testing without live Claude API calls. The application was tested from a clean checkout using uv sync and uv run main.py --offline, confirming that it could install and run successfully. It was also tested with Claude's API. One remaining testing limitation is that even if an automated test passes, it does not guarantee that every AI-generated response includes accurate information. Future testing could focus on evaluating the accuracy of generated responses.

## Appendix A: Generated Conversation Transcript

**Application:** PersonaForge\
**Personas:** Elena Rivera (Neurologist) and Maya Thompson (Family Caregiver)\
**Conversation Length:** 8 turns

## Conversation: Advanced Alzheimer's Disease and Comfort-Focused Care

**Original Conversation Topic:** Maya's mother has advanced Alzheimer's disease and has recently stopped eating. Maya wants to understand why this is happening, whether a feeding tube would help or harm, and how to make decisions that prioritize her mother's comfort. Elena responds with medical accuracy, compassion, and realistic explanations about late-stage dementia, aspiration risk, hand feeding, and comfort-focused care.

Participants: Elena Rivera, Maya Thompson

> **Simulation notice:** This conversation is AI-generated fiction. Character statements may contain inaccuracies and should not be treated as verified professional, medical, legal, or safety advice.

**Elena Rivera:** Come in, Maya. Sit wherever. I read the note from the nursing home before you got here — they said your mother's intake has dropped off over about three weeks, and that she turns her head away now when the spoon comes.

Tell me what you've been seeing. Not what they've written down. What you've seen.

**Maya Thompson:** She keeps her mouth closed. That's the thing nobody writes down right — it's not that she's refusing, it's like she's forgotten the mouth is for that. I went Tuesday at 11:40, lunch tray, and I did what the aide showed me, little touch of the spoon to her bottom lip, and she turned her face toward the window like I'd said something rude. And then forty minutes later she took four spoonfuls of the chocolate pudding, four, I counted, and I sat in my car afterward feeling like I'd won something, which — sorry. I'm doing it again.

She's down to about ninety-six pounds. She was a hundred and forty my whole childhood. And I know I'm the one who moved her out of my basement so I don't get to act like I've been there every day, but I have been there most days, and what I've seen is that she's going somewhere I can't follow her with a spoon.

**Elena Rivera:** Don't apologize for the four spoonfuls. You counted them because they mattered.

And what you just described is more accurate than most of what I read in charts. It isn't refusal. Refusal requires a decision, and she isn't making one. Swallowing is a reflex that runs on about thirty muscles firing in a particular order, and the brain keeps the sequence filed away somewhere it no longer reliably finds. So the spoon touches her lip and the old answer doesn't come. Sometimes it does — chocolate pudding, cold, sweet, heavy on the tongue. Strong signal, easier to find. That's why it was pudding and not the chicken.

The weight is the part I want to be straight with you about. In advanced Alzheimer's the body also stops using food the way it did. She could eat twice as much and not come back to a hundred and forty. The not-eating isn't only causing the decline. It's also part of it.

Does that distinction make sense, or does it sound like I'm splitting hairs?

**Maya Thompson:** No, I — it makes sense. It's just the opposite of what everything in me says, which is that if I could get enough calories into her she'd come back up and we'd have more time. You're telling me the hunger isn't the problem, the problem is the problem.

Okay. So then I have to ask the thing I've been not asking. The nurse practitioner mentioned a PEG tube, sort of sideways, like she was leaving it on the table for me to pick up. And my brother in Sacramento has already Googled it and sent me a link at 1 a.m. with the subject line "WHY AREN'T WE DOING THIS." Would it help her? Because if it would, I don't care how hard it is. And if it wouldn't, I need you to tell me in a way I can repeat to him without crying.

**Elena Rivera:** No. It wouldn't help her, and I'll give you the version you can say out loud.

Here's the data, and it's unusually clear for my field. In advanced dementia, feeding tubes don't extend life. They don't prevent aspiration pneumonia — people still aspirate their own saliva, and tube feed refluxes up and goes down the wrong way too. They don't heal pressure sores or prevent them. They don't restore strength or function. We have decades of this now, and the studies keep landing in the same place. What tubes do reliably produce: agitation, hands tied down or mitted because she'll pull at it, trips to the ER when it clogs or comes out, and the end of being fed by a person. That last one I'd ask your brother to sit with. Right now her daughter touches her lip with a spoon and sometimes she takes four bites. A tube replaces that with a pump.

For your brother, try this sentence: "A feeding tube doesn't give her more time, it gives her less of what time she has."

Click. What I'd put in its place is sometimes called comfort feeding, or careful hand feeding. It means we feed her what she'll take, when she'll take it, for pleasure and connection, and we stop when she turns toward the window. No calorie targets. No one charting percentages. Pudding at 12:20 if that's when she opens her mouth.

How does that sit with you?

**Maya Thompson:** It sits like relief, which is the part I don't trust, because relief means some piece of me wanted permission to stop pushing and what kind of daughter — sorry. I know. I know what you'd say.

Two things, then. The aides keep saying "aspiration risk" at me like it's a weather warning, and I need to know what that actually means I'm risking when I give her the pudding. Am I going to be the one who hands her the spoonful that kills her? Because I can live with a lot but I can't live with that.

And the other thing is, if we're not counting calories anymore, then what are we doing? Like what does the next part look like. Does she get hungry? Does it hurt? Everybody keeps saying "comfort" like it's a destination and nobody will tell me the mileage.

**Elena Rivera:** Relief is information, Maya. It's your body telling you the pushing was costing you something. It isn't a verdict on your character.

Aspiration. Here's what it actually means. Food or liquid goes into the airway instead of the esophagus, and sometimes it sets up an infection in the lung. In someone at her stage, the risk is already there every hour of every day, from her own saliva, whether or not you ever lift a spoon. That's the part the aides don't say when they say it like a weather warning. You are not introducing the danger. You're choosing what she gets to have while it's present. Upright, unhurried, soft and cold, small amounts, stop when she stops — that's good technique, and it lowers the odds some. It does not make you the cause if she gets pneumonia in March. Pneumonia at the end of dementia is the disease arriving, not the daughter.

Hunger and thirst. People at this stage, when the body is shutting down, largely stop registering both. The sensation goes quiet. Dry mouth is real and is miserable and is fixable — swabs, ice chips, lip balm, every hour or two, and I will write that down for the staff. Dehydration in a dying body isn't the agony we imagine; it tends to be mildly sedating. What hurts is being forced.

Mileage — I can't give you that. I don't know if it's three weeks or four months, and anyone who gives you a number is guessing with a straight face. What I can tell you is the shape: less awake, less intake, more sleeping, and at some point a chest infection or simply a slowing. Hospice should be in this room now, not later. They are better at the last part than I am.

And before you leave. How are you sleeping?

**Maya Thompson:** Oh, like a baby. Terribly, and waking up every two hours. That's the joke, you can have it for free.

No — I'll call hospice. I'll call them today, before I talk myself into waiting until after the holidays, because I know me and I'd wait. And I'm going to tell my brother that sentence. He's going to be angry at me and then he's going to fly out, and honestly, fine.

Can I say one thing? I came in here thinking you were going to hand me a plan and I'd write it in the notebook — I've got four of them, I can't throw them out — and instead you told me the pudding counts. That's all I wanted, somebody to say the four spoonfuls counted. So. Thank you. I'll see you when she — I'll just see you.