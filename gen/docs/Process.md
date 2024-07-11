## PersonaGen Process

### Overview
The intention behind this project is to personalize any data, anywhere, anyhow.

This means that this project can be run on server, serverless, ETL, local, and everywhere in-between.

A complexity however is that LLM applications can take a while to run, due to current LLM performance limits. And
realistically, there's lots of optimization to be done when it comes to truly personalizing data.

For now, will have this just run as a long-running process that can be composed in anything.

If we want to put a server in front of PersonaGen, that will be PersonaStack (in terms of memory regarding personas, runs, throttling, etc.)

### Runtime:
- Docker. Can run anywhere with easy control over runtime, libraries, etc.

### Input:
- [Persona](./Persona.md) to personalize data to (Who)
  - Custom supplemental input they want for the Personalization Goal
    - For example: Q/A use-case, custom questions they want the LLM to ask and answer for that persona
- Select goal of personalization (How)
  - Pull from library of prompts for that goal of personalization
    - For example, Q/A on the data
    - Or summarization of the data 
    - Or... anything
  - Allow user to provide supplemental prompts
- Data to personalize, e.g. input file(s), local, remote, parameters (What)
- Output Constraints
  - Things to filter out
  - Things to check for

### Processing:
- Compose Persona with custom supplemental input (Who)
- Determine goal of personalization (How)
- Tuning Process:
  -  Depends on the goal of personalization:
    - Personalize input data to persona based on the goal.
    - Expose hooks to allow the user to control the process as they desire.
    - For example, Q/A:
      - Generate relevant questions Persona would ask about the data, supplemented by custom questions
      - Answer all questions based on the data provided
      - Analyze Q/A based on state-of-the-art LLM eval techniques.
    - Examine output constraints and make sure they are met.
    - If performance reaches baseline for that goal, exit.
- Compose outputs

### Output:
- Metadata:
  - Process and Stage runtimes
  - Tokens Consumed
  - Recommendations to optimize inputs to PersonaGen
  - Errors or Warnings
- Composed Persona (Who)
- Goal of Personalization (How)
- Reference to input data provided (What)
- Output Constraints
- Tuned, personalized data for that Persona:
  - For example, Q/A:
    - What questions would they want to ask?
    - Answers to those questions based on the data provided
    - (Allow QA uses outside of RAG purposes)
    - RAG optimized source files with optimal RAG parameters
