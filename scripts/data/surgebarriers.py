passage = {
    "files": {
        "because": {
            "train": "data/automl/surgebarriers_because_v10_train.jsonl",
            "validation": "data/automl/surgebarriers_because_v10_validation.jsonl",
            "test": "data/automl/surgebarriers_because_v10_test.jsonl"
        },
        "but": {
            "train": "data/automl/surgebarriers_but_v11_train.jsonl",
            "validation": "data/automl/surgebarriers_but_v11_validation.jsonl",
            "test": "data/automl/surgebarriers_but_v11_test.jsonl"
        },
        "so": {
            "train": "data/automl/surgebarriers_so_v12_train.jsonl",
            "validation": "data/automl/surgebarriers_so_v12_validation.jsonl",
            "test": "data/automl/surgebarriers_so_v12_test.jsonl"
        },
    },
    "text": """**Climate Change Brings Extreme Weather**

In 2012, Superstorm Sandy claimed about 150 lives and caused over $70 billion in damages in the United States. Scientists warned that Sandy was part of a growing trend: extreme weather events caused by climate change. The event sparked a national conversation between scientists, government officials, and American citizens.

**Are Surge Barriers the Answer?**

With speeds reaching over 100 miles per hour, hurricane winds can drive water from the ocean towards coastal cities. When this happens, waves of seawater surge above the normal tide and crash through city streets, endangering lives and destroying neighborhoods and businesses. These storm surges are the leading cause of death during a hurricane.

In 2019, the United States Army Corps of Engineers (USACE) proposed five different options to protect New York City against massive hurricane floods like those that damaged the city during Hurricane Sandy. The most expensive option, estimated at $118.8 billion, is a surge barrier made of concrete and steel. The five-mile-long, thirty-foot tall surge barrier would be built in the water between the Rockaways and New York Harbor. During storms, the city would be able to close the barrier’s gates, blocking storm surges. The USACE estimated that the barrier could save billions of dollars in property damage and countless lives.

**The Plans Hit a Wall**

In New York, many environmental groups worried about how a surge barrier might affect marine ecosystems in New York Harbor and the Hudson River. New York Harbor and the Hudson River are home to a diverse array of marine creatures, including crabs, lobsters, herring, eel, and striped bass.

Environmental advocates argued that the surge barrier could change these ecosystems in various ways. For example, the surge barrier could interrupt the spawning season for many fish. At particular times in the year, fish travel to new locations where they lay their eggs. A surge barrier could block certain fish from getting to their spawning locations and safely releasing their eggs.

**Exploring Alternatives**

Some environmental activists advocated for alternative solutions. Some proposed that New York City invest in building flood walls and levees on the shore rather than surge barriers in the water. Advocates argued that those solutions would not have the same negative impact on the local ecosystem as surge barriers. Others offered entirely different solutions, such as raising up buildings and elevating New York City’s subway system.

As New York and other coastal cities continue to endure extreme weather events, scientists, advocates, residents, and elected officials weigh in on the proposals. Are surge barriers the right option for New York City?
""",
    "plagiarism": {
        "because": "Environmental advocates argued that the surge barrier could change these ecosystems in various ways. For example, the surge barrier could interrupt the spawning season for many fish. At particular times in the year, fish travel to new locations where they lay their eggs. A surge barrier could block certain fish from getting to their spawning locations and safely releasing their eggs.",
        "but": "In 2019, the United States Army Corps of Engineers (USACE) proposed five different options to protect New York City against massive hurricane floods like those that damaged the city during Hurricane Sandy. The most expensive option, estimated at $118.8 billion, is a surge barrier made of concrete and steel. The five-mile-long, thirty-foot tall surge barrier would be built in the water between the Rockaways and New York Harbor. During storms, the city would be able to close the barrier’s gates, blocking storm surges. The USACE estimated that the barrier could save billions of dollars in property damage and countless lives.",
        "so": """Some environmental activists advocated for alternative solutions. Some proposed that New York City invest in building flood walls and levees on the shore rather than surge barriers in the water. Advocates argued that those solutions would not have the same negative impact on the local ecosystem as surge barriers. Others offered entirely different solutions, such as raising up buildings and elevating New York City’s subway system.""",
    },
    "prompts": {
        "because": "A surge barrier in New York City could harm the local ecosystem because",
        "but": "A surge barrier in New York City could harm the local ecosystem, but",
        "so": "A surge barrier in New York City could harm the local ecosystem, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why a surge barrier in New York City could harm the local ecosystem.

A response is optimal when it says that a surge barrier can block fish from getting to their spawning sites.

A response is suboptimal when
- it says a surge barrier can affect spawning, but not how.
- it says a surge barrier can harm the ecosystem, but does not mention spawning.
- it says a surge barrier can block fish, but does not mention spawning.
- it does not give a reason why a surge barrier in New York City could harm the local ecosystem.
        """,
        "but": """Their response must use information from the text to show a contrasting idea about a surge barrier in New York City.

A response is optimal when it says that surge barriers:
- save lives during a storm.
- prevent damage during a storm.
- save lives and prevent damage.

A response is suboptimal when:
- it says that surge barriers save lives, but does not mention storms.
- it says that surge barriers prevent damage, but does not mention storms.
- it says that there alternative solutions.
- it says that surge barriers block storm surges or protect the city, but does not mention saving lives or preventing damage.
- it misuses the conjuction.
- it is not related to the text.
        """,
        "so": """Their response must use information from the text to show an effect or consequence of the surge barrier debate in New York City.

A response is optimal when it says that environmental activists proposed specific alternatives, and mentions at least one such alternative.

A response is suboptimal when:
- it says environmental activists proposed alternatives, but does not mention at least one such alternative.
- it says alternative solutions exist, but not who proposed them.
- it says people oppose surge barriers.
- it says surge barriers harm ecosystems.
- it misuses the conjunction.
- it is not related to the text.
        """
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why a surge barrier could harm the local ecosystem in New York City.",
            "Label_1": "That's true! Now expand your response. How could a surge barrier make it hard for fish to spawn or reproduce?",
            "Label_2": "That's true! Now be more specific. How could a surge barrier hurt marine life and the local ecosystem?",
            "Label_3": "It's true that a surge barrier could block fish! Now be more specific. Where could it block fish from going?",
            "Label_0": "Clear your response and try again. How could a surge barrier hurt fish? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrasting idea about a surge barrier in New York City.",
            "Optimal_2": "Nice work! You used information from the text to show a contrasting idea about a surge barrier in New York City.",
            "Optimal_3": "Nice work! You used information from the text to show a contrasting idea about a surge barrier in New York City.",
            "Label_1": "It's true that surge barriers can protect people from flooding! Now be more specific. What causes the floods?",
            "Label_2": "It's true that surge barriers prevent damage during floods! Now be more specific. What causes the floods?",
            "Label_3": "Clear your response and try again. Instead of talking about alternative solutions, explain how a surge barrier could help New York City.",
            "Label_4": "Surge barriers could block storm surges and protect New York City—that's true. Now add a specific example from the text. What are things in the city that surge barriers could help save?",
            "Label_0": "Try clearing your response and starting again. Focus on the benefits of building a surge barrier, and check that your response only uses information from the text. How could a surge barrier help New York City during a hurricane?",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show an effect or consequence of the surge barrier debate in New York City.",
            "Label_1": "It's true that environmental activists advocated for alternatives! Now expand your response. What are some alternative solutions that they proposed?",
            "Label_2": "It's true that there are alternatives to a surge barrier! Now be more specific. Who proposed these alternatives?",
            "Label_3": "It's true that some people opposed the plans for a surge barrier! Now expand your response. What did they suggest that New York City do instead?",
            "Label_5": "That's true—a surge barrier could harm the ecosystem. Now focus on what environmental activists did as a result of this. What did environmental activists think New York City should do instead of building a surge barrier?",
            "Label_0": "Clear your response and try again. What did environmental activists propose that New York City should do instead of building a surge barrier?",
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "it would interrupt the spawning seasons for many of the fish, and a surge barrier would also block certain species of fish from getting to their spawning locations.",
                "it could interrupt the spawning season for fish by blocking some kinds of fish from getting to their spawning areas and safely laying their eggs.",
                "it is changing the water´s flow which could affect the migration patterns of fish and other marine animals and the surge barrier prevents fish from swimming upstream to spawn.",
                "the barrier will block the creatures which need to go back for breeding descendant."
            ],
            "Label_1": [
                "it could stunt the spawning of certain species of fish in New York's unique ecosystem by putting their eggs at harm.",
                "they can destroy marine ecosystems by interrupting the spawning season for many fish as evidenced by research done in the New York Harbor.",
                "it could interrupt the spawning season for many fish.",
                "a surge barrier can effect where fish lay eggs and could change some ecosystems"
            ],
            "Label_2": [
                "How a surge surge  barrier might affect marine ecosystems home to a diverse array of marine creatures, including crabs, lobster , herring, eel and striped bass.",
                "it was destroyed.",
                "it could harm fish and other animals.",
                "it can hurt the fish because the barrier can kill or hurt the fish in any way."
            ],
            "Label_3": [
                "It could physically block the the natural migrations patterns of local wildlife.",
                "everthing will hit the wall eventuely ya like fish or the wall or the  wall blocks everthing",
                "it would stop fish from growing.",
                "it could cut off the fishes route or nesting ground."
            ],
            "Label_0": [
                "in 2019, the united states army corps of Engineers(USACE) proposed five different options to protect New York city  against massive hurricane floods like those who damaged the city",
                "the same negative impact on local ecosystem as surge barriers other offered entirely different solution  such as raising  up buildings and elevating New York City's subway system.",
                "they are home to a diverse array of marine creatures.",
                "they want to protect from massive hurricane floods like those that damaged the city during Hurricane Sandy."
            ]
        },
        "but": {
            "Optimal_1": [
                "during storms, the location would be able to close the barrier's gates, perhaps saving a lot of lives.",
                "a surge barrier, according to the USACE, might save lives during a hurricane."
            ],
            "Optimal_2": [
                "during storms, the city would be able to save billions of dollars on their property damages and expenses.",
                "surge barriers safeguard the city and save billions of dollars in property damage in the event of a major storm."
            ],
            "Optimal_3": [
                "it could save a lot of money, and prevent more deaths.",
                "it could save billions of dollars in property damage and save countless lives during a storm surge."
            ],
            "Label_1": [
                "it is believed that it will save thousands of lives.",
                "the USACE estimated that the surge barrier could save countless lives.",
                "it could save lots of lives by keeping the water at bay and not get out of hand."
            ],
            "Label_2": [
                "it would save New York City billions of dollars in damage.",
                "the surge barrier will prevent harmful damages to New York City.",
                "it would stop property from being damaged."
            ],
            "Label_3": [
                "environmental activists found alternative solutions like building floodwalls and levees.",
                "activists are advocating for many different solutions from floodwalls and levees to raising up buildings.",
                "some people propose to build floodwalls."
            ],
            "Label_4": [
                "New York City would be protected against massive hurricane floods.",
                "it's needed to provide protection for the city.",
                "it keeps water out and would help New York not to flood."
            ],
            "Label_0": [
                "it protects the city streets, endangering people's lives, and ruining neighborhoods and businesses.",
                "many say it it changes it would still cause the same negative impact on the environment."
            ]
        },
        "so": {
            "Optimal_1": [
                "environmental activists advocated for alternative solutions on the shore including investing in building flood walls and levees.",
                "other environmental activists offered to raise up buildings and elevating New York's subway system.",
                "scientists, advocates, residents, and elected officials of New York City came up with other ideas like flood walls and levees placed on the shores.",
                "environmentalists gave ideas to build flood walls to help prevent storm surges."
            ],
            "Label_1": [
                "environmental activists came up with alternative solutions.",
                "environmental activists are looking for better solutions that won't disrupt the fish.",
                "environmental advocates have begun looking into alternative ideas to prevent death and damage."
            ],
            "Label_2": [
                "there is a different way to deal with the problem.",
                "some said that new york city needed floodwalls.",
                "people are asking for other solutions.",
                "some people in New York City said to put building floor walls and levees rather than surge barriers."
            ],
            "Label_3": [
                "some people dont like the idea of having surge barriers because it can harm stuff.",
                "environmental advocates disagree with surge barriers.",
                "it would be better to not use it.",
                "building the surge barrier have many negative effects on it."
            ],
            "Label_5": [
                "environmental groups are worried about the long term effects on the ecosystem.",
                "advocates argued the surge barrier wouldn't be ok for the ecosystem.",
                "people argued that the surge could change the ecosystems in various ways."
            ],
            "Label_0": [
                "people can not not use them.",
                "New York will continue to have extreme weather."
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_1": [
                "A surge barrier can block fish from getting to their spawning sites.",
                "A surge barrier can block fish from getting to their spawning sites.",
                "A surge barrier can block fish from getting to their spawning sites.",
                "A surge barrier can block fish from getting to their spawning sites.",
            ],
            "Label_1": [
                "A surge barrier can affect spawning.",
                "A surge barrier can affect spawning.",
                "A surge barrier can affect spawning.",
                "A surge barrier can affect spawning.",
            ],
            "Label_2": [
                "A surge barrier can harm the ecosystem.",
                "A surge barrier can harm the ecosystem.",
                "A surge barrier can harm the ecosystem.",
                "A surge barrier can harm the ecosystem.",
            ],
            "Label_3": [
                "A surge barrier can block fish.",
                "A surge barrier can block fish.",
                "A surge barrier can block fish.",
                "A surge barrier can block fish.",
            ],
            "Label_0": [
                "Does not give a reason why a surge barrier in New York City could harm the local ecosystem.",
                "Does not give a reason why a surge barrier in New York City could harm the local ecosystem.",
                "Does not give a reason why a surge barrier in New York City could harm the local ecosystem.",
                "Does not give a reason why a surge barrier in New York City could harm the local ecosystem.",
            ]
        },
        "but": {
            "Optimal_1": [
                "A surge barrier can save lives during storms.",
                "A surge barrier can save lives during storms.",
            ],
            "Optimal_2": [
                "A surge barrier can prevent damage during storms.",
                "A surge barrier can prevent damage during storms.",
            ],
            "Optimal_3": [
                "A surge barrier can save lives and prevent damage.",
                "A surge barrier can save lives and prevent damage.",
            ],
            "Label_1": [
                "A surge barrier can save lives. Does not mention storms.",
                "A surge barrier can save lives. Does not mention storms.",
                "A surge barrier can save lives. Does not mention storms.",
            ],
            "Label_2": [
                "A surge barrier can prevent damage. Does not mention storms.",
                "A surge barrier can prevent damage. Does not mention storms.",
                "A surge barrier can prevent damage. Does not mention storms.",
            ],
            "Label_3": [
                "There are alternative solutions.",
                "There are alternative solutions.",
                "There are alternative solutions.",
            ],
            "Label_4": [
                "A surge barrier can block storm surges and protect the city.",
                "A surge barrier can block storm surges and protect the city.",
                "A surge barrier can block storm surges and protect the city.",
            ],
            "Label_0": [
                "Does not show a contrasting idea about a surge barrier in New York City.",
                "Does not show a contrasting idea about a surge barrier in New York City.",
            ]
        },
        "so": {
            "Optimal_1": [
                "Environmental activists proposed specific alternatives, with at least one such alternative.",
                "Environmental activists proposed specific alternatives, with at least one such alternative.",
                "Environmental activists proposed specific alternatives, with at least one such alternative.",
                "Environmental activists proposed specific alternatives, with at least one such alternative.",
            ],
            "Label_1": [
                "Environmental activists proposed alternatives.",
                "Environmental activists proposed alternatives.",
                "Environmental activists proposed alternatives.",
            ],
            "Label_2": [
                "Alternative solutions exist.",
                "Alternative solutions exist.",
                "Alternative solutions exist.",
                "Alternative solutions exist.",
            ],
            "Label_3": [
                "People oppose surge barriers.",
                "People oppose surge barriers.",
                "People oppose surge barriers.",
                "People oppose surge barriers.",
            ],
            "Label_5": [
                "Surge barriers harm ecosystems.",
                "Surge barriers harm ecosystems.",
                "Surge barriers harm ecosystems.",
            ],
            "Label_0": [
                "Does not show an effect or consequence of the surge barrier debate in New York City.",
                "Does not show an effect or consequence of the surge barrier debate in New York City.",
            ]
        }

    }
}