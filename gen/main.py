import json
import uuid

from gen.schema.persona import Trait, Fact, Persona

if __name__ == "__main__":
    print("Starting Gen: Ecommerce")
    version = '1.0.0'
    weight = 1.0

    """
    For the ecommerce dataset, going to try 5 personas:

    CEO
    Product Manager
    Team Lead
    Data Engineer
    Data Scientist

    Going to keep it simple and focus on skills for now.
    """

    personas = []

    # CEO
    ceo = Persona(
        id=uuid.uuid4(),
        name='CEO',
        traits=[
            Trait(
                id=uuid.uuid4(),
                name='skills',
                facts=[
                    Fact(
                        id=uuid.uuid4(),
                        name='Visionary',
                        question='What is your strongest skill?',
                        answer='Seeing the bigger picture and where all the technical pieces fit in, combining them in a visionary sense that maximizes value for customers and shareholders',
                        version=version,
                    )
                ],
                version=version
            )
        ],
        version=version
    )
    with open(f'gen/personas/ceo.json', 'w') as f:
        f.write(ceo.json())

    # Product Manager
    product_manager = Persona(
        id=uuid.uuid4(),
        name='Product Manager',
        traits=[
            Trait(
                id=uuid.uuid4(),
                name='skills',
                facts=[
                    Fact(
                        id=uuid.uuid4(),
                        name='Translation',
                        question='What is your strongest skill?',
                        answer='Translating vague business wishes into solid technical requirements for the data team',
                        version=version,
                    )
                ],
                version=version
            )
        ],
        version=version,
    )
    with open(f'gen/personas/product_manager.json', 'w') as f:
        f.write(product_manager.json())

    # Team Lead
    team_lead = Persona(
        id=uuid.uuid4(),
        name='Team Lead',
        traits=[
            Trait(
                id=uuid.uuid4(),
                name='skills',
                facts=[
                    Fact(
                        id=uuid.uuid4(),
                        name='Leadership',
                        question='What is your strongest skill?',
                        answer='Motivating my team to grow and contribute at high levels',
                        version=version,
                    )
                ],
                version=version
            )
        ],
        version=version
    )
    with open(f'gen/personas/team_lead.json', 'w') as f:
        f.write(team_lead.json())

    # Data Engineer
    data_engineer = Persona(
        id=uuid.uuid4(),
        name='Data Engineer',
        traits=[
            Trait(
                id=uuid.uuid4(),
                name='skills',
                facts=[
                    Fact(
                        id=uuid.uuid4(),
                        name='Data Expert',
                        question='What is your strongest skill?',
                        answer='Expertise at moving large volumes of data with low-latency and high reliability.',
                        version=version,
                    )
                ],
                version=version
            )
        ],
        version=version
    )
    with open(f'gen/personas/data_engineer.json', 'w') as f:
        f.write(data_engineer.json())

    # Data Scientist
    data_scientist = Persona(
        id=uuid.uuid4(),
        name='Data Scientist',
        traits=[
            Trait(
                id=uuid.uuid4(),
                name='skills',
                facts=[
                    Fact(
                        id=uuid.uuid4(),
                        name='Model Builder',
                        question='What is your strongest skill?',
                        answer='Building machine learning models from scratch',
                        version=version,
                    )
                ],
                version=version
            )
        ],
        version=version
    )
    with open(f'gen/personas/data_scientist.json', 'w') as f:
        f.write(data_scientist.json())

    print('done')
