import structlog

from gen.schema.schema import Persona, Trait, Configuration

logger = structlog.get_logger()

persona = Persona(
    name="football coach",
    traits=[
        Trait(
            question="What is your strongest skill?",
            answer="I can motivate my players to do far beyond what they thought possible"
        ),
        Trait(
            question="What kind of football plays do you like to run?",
            answer="I prefer to run passing plays. While they are more risky, they have greater potential for reward and don't wear my team out as much."
        )
    ]
)

configuration = Configuration()


if __name__ == '__main__':
    logger.info('Starting Gen')

    # TODO: Step 0, get persona and configuration
    logger.info(persona.json())

    # TODO: Step 1, embed input data

    # TODO: Step 2, Gen questions Persona would ask

    # TODO: Step 3, Gen answers to questions via RAG

    # TODO: Step 4, Eval

    # TODO: Step 5, Output

