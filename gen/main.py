import json
import uuid

from gen.schema.persona import Trait, Fact, Persona

if __name__ == "__main__":
    print("Starting Gen")
    version = '1.0.0'
    example_file_name = './personas/example.json'


    traits = [
        Trait(
            id=uuid.uuid4(),
            name='skills',
            facts=[
                Fact(
                    id=uuid.uuid4(),
                    name="programming language preference",
                    question="What programming language do you prefer to use?",
                    answer="Python",
                    version=version
                )
            ],
            version=version
        )
    ]
    persona = Persona(
        id=uuid.uuid4(),
        name='Persona',
        traits=traits,
        version=version
    )

    with open(example_file_name, 'w') as f:
        f.write(persona.json())

    # load
    with open(example_file_name) as f:
        persona2 = Persona(**json.load(f))

    print(persona2)

    print('done')
