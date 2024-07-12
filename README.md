<p align="center">
  <img src="assets/PersonaFlowIcon-512.png" height="256">
  <h1 align="center">PersonaFlow</h1>
  <h2 align="center"><b><i>Where AI Meets Individuality for Unmatched Personalization</i></b></h2>
</p>

<p align="center">
  <a href="https://discord.gg/zqHHYGuHFd"> 
    <img
      src="https://img.shields.io/discord/1086345563026489514?label=&logo=discord&style=for-the-badge&logoWidth=20&logoColor=white&labelColor=000000&color=blueviolet">
  </a>
</p>

**The PersonaFlow platform aims to provide highly personalized user experiences fueled by Generative AI. With a focus on scalability and efficiency, PersonaFlow offers a suite of tools and APIs to create complex agents and high-performing retrieval augmented generation (RAG) systems.**

Key features include:
- Context optimization: Intelligent partitioning of ingested data based on the semantic similarity of surrounding content (see: [Document Processing](/docs/rag.md)).
- Enterprise feasibility: focus on scalability, cost efficiency, and privacy
- Agent development: Quickly build and evaluate custom assistants (see: [Assistants](/docs/assistants.md))
- Evaluation: Deep integration with evaluation tools to score and optimize agents and RAG configurations
- Build and deploy: Easily deploy agents and RAG configurations to production environments
- Multiple built-in auth options (see: [Auth Guide](/docs/auth.md))

Upcoming features:
- Client SDKS: Easy integration of generative AI features into applications via the PersonaFlow client SDKs (Python, TypeScript, C#)
- Personalization features: user-specific RAG based on up to 100 different dimenensions.
- Evaluation and scoring of assistants and RAG configurations (Currently done through [Arize Phoenix](https://arize.com/phoenix/) and [LangFuse](https://langfuse.com/) integrations.)
  

# Overview

Much of the API and business language is modeled after the OpenAI Assistants API and uses LangGraph under the hood for the agent functionality along with a [highly configurable]() RAG system, and a suite of agent-based features. It will be further expanded with personalization features, additional RAG optimization techniques, and more.

 <p align="center" style="color:green"><b><i>Note: This project is in the very early stages of development and testing. Breaking changes should therefore be expected until the first stable release.</i></b></p>

> Web site and documentation are in the works, but in the meantime you can find the API documentation [on SwaggerHub](https://app.swaggerhub.com/apis-docs/DanOrlando/personaflow/0.1.0).

<!-- # Roadmap

- [x] Assistants API
- [x] File management
- [x] Advanced RAG with adaptive chunking and summarization
- [x] Advanced RAG assistants integration
- [x] More LLMs, embedding options
- [x] Local LLMs and embeddings (Ollama, Huggingface)
- [ ] Auth
- [ ] Admin client (in progress)
- [ ] More agent types (self-reflection, etc.)
- [ ] Persona generation
- [ ] PersonaGen integration
- [ ] Evaluation and scoring of assistants and RAG configurations
- [ ] TypeScript SDK
- [ ] Python SDK -->

## Technology Stack

- Programming Language
  - Server and backend libraries: Python
  - Admin UI: Next.js (TypeScript)
- Relational Database: PostgreSQL
- Vector Database: Qdrant (more will be supported - easily added by extending the base class)
- Agent Framework: LangGraph
- Document Processing: Semantic-Router, Unstructured, LlamaIndex, LangChain
- Mono-repo manager: Pants
- ORM: SQLAlchemy
- Database Migration Tool: Alembic


## Quickstart (Docker)

Follow these instructions if you are only running from Docker and do not need to set up the environment for development.

1. Clone the repo and navigate to the root directory
2. Create .env file using the .env.example template.
3. Run `docker-compose up -d` from terminal.

## Dev Setup

_Builds and dependencies are managed by [Pantsbuild](https://www.pantsbuild.org/2.20/docs/python/overview). Pants is a fast, scalable, user-friendly rust-based build system._

1. [install Pants](https://www.pantsbuild.org/2.20/docs/getting-started/installing-pants) on your system. 
2. Clone the repo and make sure you have Python 3.11.* installed and the interpreter selected in your IDE.
3. Create .env file using the .env.example template.
4. Open docker-compose.yaml and make sure the `stack` block under `services` is commented out. Optionally uncomment the `langfuse` and `phoenix` blocks if you plan to run the evaluation services. 
5. Open docker on your machine if it is not already running and run `docker-compose up -d`. This will download and start the images. 
6. Install dependencies by running `poetry install --no-root`. 
7.  When that is fiinished, run `make migrate`. This will run the migrations and seed the database with initial data.
8.  To run the backend with hot reload, use `make stack-dev`, otherwise you can use `pants run stack:local` if you do not need the backend server to hot reload.
9.  Navigate to `http://localhost:9000/docs` to see the API documentation.

## Useful Pants Commands
- Lint: `pants lint ::`
- Test: `pants test ::`
- Run the stack server: `pants run stack:local` (use `--ldebug` for debug logging)
- Run the dev server with hot reload: `make stack-dev`

Note: `::` means all files in project. For more information on targeting, see: [Targets and BUILD files](https://www.pantsbuild.org/2.20/docs/using-pants/key-concepts/targets-and-build-files).

>_Pants uses a constraints.txt as the lock file for dependencies, which is exported from the from poetry.lock. If you add a new dependency, you will need to run `poetry lock` to update the poetry.lock, followed by `poetry export --format constraints.txt --output constraints.txt` to regenerate the constraints file which will lock the new dependency to the version in the poetry.lock file._

# API Usage

To run the APIs, you can use the Swagger UI at `http://localhost:9000/docs` or via [the Postman collection](/stack/tests/integration/PersonaFlow.postman_collection.json).

## UI Setup

_Dependencies are managed by [NPM](https://www.npmjs.com/)_

1. Install node or make sure you have it installed (`node -v`).
2. Navigate to `ui` folder.
3. Run `npm install` to install dependencies.
4. copy `.env.local.example` into `.env.local` file (e.g., `cp .env.local.example .env.local`).
5. Update `.env.local` and comment out the line where `NEXT_PUBLIC_BASE_API_URL` is defined. Make sure that the key value is correct and you have backend running under the same address.
6. Run `npm run dev` and open the link from the console in a browser.

# Documentation
- [Assistants](/docs/assistants.md)
- [Document Processing and RAG](/docs/rag.md)
- [Auth](/docs/auth.md)
- Evaluation and scoring: Coming soon
- Custom architectures and tools: Coming soon
- Admin Client: Coming soon
- SDKs: Coming soon
- Personalization: Coming soon
- [Troubleshooting](/docs/troubleshooting.md)

# Contributing

Contributions are welcome! If you have a feature request, bug report, or a pull request, please feel free to open an issue or submit a PR.

# 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
