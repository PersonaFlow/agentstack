## What is a Persona?

It is all the metadata, traits about me that make me unique.

![PersonaFlow - WhatIsPersona_.png](..%2Fassets%2FPersonaFlow%20-%20WhatIsPersona_.png)

A truly personalized experience is one that captures as many of these attributes about me as possible.

How do we get to know someone?  We ask them questions, so we can start to figure some of these things out.

We can teach LLMs to do things via questions as well, so they are the perfect vehicle.

Also, I would say that current context (current events, news, things going on in geographic location) would affect
the personalization as well.  TODO: think about how this might be implemented here

### Data Definition

Based on the graph above, my proposed data definition for a persona would look like this:

```json
{
  "traits": {
    "psychographics": {
      "description": "These are motivations that drive me to wake up, perform and keep going.",
      "weight": 1,
      "qa": [
        {
          "id": 1,
          "question": "What motivates you to get up in the morning?",
          "answer": "I am motivated to improve 1% each and every day, incremental improvement drives me.",
          "weight": 2
        }
      ]
    },
    "experiences": {
      "description": "These are experiences unique to me that have had an impact on my life",
      "weight": 1,
      "qa": [
        {
          "id": 1,
          "question": "What is a unique experience you have had?",
          "answer": "I played basketball for 15 years growing up and got pretty good at it",
          "weight": 1
        }
      ]
    }
  },
  ...
}
```

Then traits and each qa pair can have weights. This provides the lever to adjust importance between personalization based on traits
and can be further enhanced in the future with machine learning. Or, perhaps someone wants to play with the importance of certain traits and qa pairs 
and see how that changes the personalization. Weights will provide the levers to tweak the personalization depending on the use-case at hand.

Lastly, regardless of how many of these are provided, they will allow laser-focused personalization of the data given in the format desired.

This also allows custom traits and qa to be added to help the LLM learn more about the user before personalizing.

_Disclaimer on Demographics / other sensitive traits: if we are going to use those, we need to be really careful how that affects bias.
Users want a personalized experience, but also want a sense of privacy and not having everything known.  It's a balancing act between relevance and creepiness._
