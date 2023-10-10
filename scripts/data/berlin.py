passage = {
    "files": {
        "because": {
            "train": "data/automl/berlin_because_v2_train.jsonl",
            "validation": "data/automl/berlin_because_v2_validation.jsonl",
            "test": "data/automl/berlin_because_v2_test.jsonl"
        },
        "but": {
            "train": "data/automl/berlin_but_v2_train.jsonl",
            "validation": "data/automl/berlin_but_v2_validation.jsonl",
            "test": "data/automl/berlin_but_v2_test.jsonl"
        },
        "so": {
            "train": "data/automl/berlin_so_v2_train.jsonl",
            "validation": "data/automl/berlin_so_v2_validation.jsonl",
            "test": "data/automl/berlin_so_v2_test.jsonl"
        },
    },
    "text": """As the world’s best athletes made their way into the stadium for the opening ceremony of the 1936 Summer Olympic Games, they were met with a scene that modern Olympians would probably recognize. Crowds roared as each team joined the parade of countries. Triumphant music played while the Olympic flame was lit by the last runner in the first-ever torch relay. On the surface, the event appeared to be the same show of global unity and peace that’s often associated with the Olympic Games today.

This wasn’t an ordinary Olympics, though. New official German flags, each bright red with a stark black and white swastika, billowed in the wind next to banners featuring the Olympic rings. And, during the athletes’ procession, many competitors raised a one-armed salute as they passed the host of this international competition: Germany’s leader, Adolf Hitler.

**An Olympic Opportunity**

When the International Olympic Committee (IOC) chose Berlin in 1931 to host the upcoming 1936 Summer Olympics, they hoped the event would give Germany an opportunity to rejoin the global community in a positive way after World War I. However, once Hitler seized power in 1933, many people around the world began to question whether Germany was actually committed to peace. The Nazi regime’s agenda was no secret: international newspapers reported widely on Hitler’s harmful, discriminatory statements and actions, along with the government’s persecution of Jewish people. Athletes even threatened to boycott the Berlin Olympics after the antisemitic Nuremberg Laws were passed in Germany in 1935, worried they might seem to support Nazi beliefs if they participated in the Games.

Despite this international outcry, the Nazi government remained committed to promoting Germany as a tolerant, peaceful nation for the Summer Olympics. They believed the Games could be used as an effective propaganda tool to improve the world’s opinion of the country. Hitler’s government thought this would help humanize them and downplay the dangers of their fascist regime. If the Nazi leaders could convince the world they were not a threat, then Germany could pursue its imperialist, nationalist agenda without resistance.

**The Power of Propaganda**

Nazi leaders thought this propaganda campaign would be effective because similar tactics had already helped them gain and maintain power in Germany. In 1933, Hitler created the Ministry of Public Enlightenment and Propaganda. This government agency used the media, public events, and even children’s textbooks to promote Nazi ideology and blame the people they called “enemies of the state”—a group that included Jewish people, Black people, Romani people, political opponents, and members of the LGBTQ community—for Germany’s problems.

As global protests grew ahead of the 1936 Olympics, however, German leaders knew they needed to control their public image in a different way. Instead of aggressively promoting their beliefs, they attempted to hide them. Antisemitic posters, including ones barring Jews from public spaces, were torn down throughout the city. Hate-filled newspapers stopped publishing new editions. Radio shows told German citizens that it was their duty to behave like good hosts, encouraging them to be “...more charming than the Parisians, more easy-going than the Viennese, more vivacious than the Romans, more cosmopolitan than London, and more practical than New York.”

World leaders and IOC representatives were invited to visit Berlin once the government’s preparations were complete. Nazi officials designed these tours to convince others that reports of discrimination were exaggerated and to show that Germany would be a warm, welcoming host. Most of the visitors believed the carefully-crafted version of Berlin that they saw and, in August of 1936, forty-nine countries met there to compete in the Summer Olympics—more than in any previous Games.

**Hitler’s March Toward WWII**

Unfortunately, this show of tolerance was nothing more than that: a show. Hitler chose to avoid shaking hands with medal winners rather than risk controversy by refusing to acknowledge Black and Jewish athletes. All but one Jewish athlete was excluded from Germany’s national teams. And, before the visits that convinced the world that the Games could go on, many Romani families who lived in Berlin were sent to concentration camps.

Nevertheless, historians now see the Berlin Olympics as a resounding success for the Nazi Party. By persuading others to at least temporarily ignore the growing threat of fascism in Germany, Nazi propagandists helped clear the way for Hitler’s imperialist plans. Just three years after the country’s Olympic spectacle, the German military invaded Poland, and World War II officially began.
""",
    "plagiarism": {
        "because": """Hitler’s government thought this would help humanize them and downplay the dangers of their fascist regime. If the Nazi leaders could convince the world they were not a threat, then Germany could pursue its imperialist, nationalist agenda without resistance.""",
        "but": "Unfortunately, this show of tolerance was nothing more than that: a show. Hitler chose to avoid shaking hands with medal winners rather than risk controversy by refusing to acknowledge Black and Jewish athletes. All but one Jewish athlete was excluded from Germany’s national teams. And, before the visits that convinced the world that the Games could go on, many Romani families who lived in Berlin were sent to concentration camps.",
        "so": """Instead of aggressively promoting their beliefs, they attempted to hide them. Antisemitic posters, including ones barring Jews from public spaces, were torn down throughout the city. Hate-filled newspapers stopped publishing new editions. Radio shows told German citizens that it was their duty to behave like good hosts, encouraging them to be “...more charming than the Parisians, more easy-going than the Viennese, more vivacious than the Romans, more cosmopolitan than London, and more practical than New York.”""",
    },
    "prompts": {
        "because": "Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics because",
        "but": "Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics, but",
        "so": "Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.

A response is optimal when it says that
- they wanted to downplay the dangers of the Nazi party.
- they wanted to pursue their imperialist agenda more easily.

A response is suboptimal when
- it says that they wanted to improve the perception of Germany, but does not mention why.
- it says it is useful propaganda, but does not specify for what purpose.
- it misuses the conjuction.
- it says propaganda had worked in the past, but does not mention the present goal.
""",
        "but": """Their response must use information from the text to show a contrasting or suprising idea about the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.

A response is optimal when
- it gives a specific example of an intolerant action.
- it says there were protests and mentions a specific intolerant action.
- it says the persecution or hate was well-documented.

A response is suboptimal when:
- it says this was a facade, but does not give a specific example of an intolerant action.
- it says other people were skeptical or boycotted the event, but does not specify why.
- it misuses the conjunction by saying that the German leaders hid their beliefs.
- it misuses the conjunction by saying that the German leaders wanted to pursue their agenda.
""",
        "so": """Their response must use information from the text to show a consequence of the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.

A response is optimal when it says that
- they invited world leaders for controlled visits.
- they hid antisemitic publications.
- they instructed their citizens to be good hosts.

A response is suboptimal when:
- it says they hid their beliefs, but does not give a specific example.
- it says they used propaganda, or created a ministry, but does not cite any actions taken in relation to the preparation of the Olympics.
- it misuses the conjunction by saying they continued their plans without resistance.
- it says historians see this as a success, but does not mention any of the Nazi leaders' actions.
"""
    },
    "instructions_short": {
        "because": """Their response must use information from the text to explain why Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.""",
        "but": """Their response must use information from the text to show a contrasting or suprising idea about the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.""",
        "so": """Their response must use information from the text to show a consequence of the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics."""
    },
    "feedback": {
        "because": {
            "Optimal_2": "Nice work! You used information from the text to explain why Nazi leaders wanted to seem tolerant ahead of the Berlin Olympics.",
            "Optimal_3": "Nice work! You used information from the text to explain why Nazi leaders wanted to seem tolerant ahead of the Berlin Olympics.",
            "Label_1": "Nazi leaders did want the world to see Germany in a more positive way—that's true. Add more information to make your response clearer. Why was this a priority for the Nazi government?",
            "Label_2": "It's true that Nazi leaders saw the Olympics as useful propaganda. Add another detail from the text to make your sentence more specific. What was the purpose of this propaganda?",
            "Label_3": "Many people around the world knew about the Nazi Party's actions and beliefs—that's true. Instead of focusing on their intolerance, write about a reason Nazi leaders wanted to change this image. Why did Nazi leaders want the world to think Germany was tolerant?",
            "Label_5": "Instead of writing about past propaganda, focus on what Nazi leaders hoped to accomplish with the Berlin Olympics. What is one reason that Nazi leaders wanted the world to think Germany was tolerant?",
            "Label_0": "Try clearing your response and starting again. Why did Nazi leaders want the world to think Germany was tolerant? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show how Nazi leaders' actions contrasted with the image they wanted to project.",
            "Optimal_2": "Nice work! You used information from the text to show how Nazi leaders' actions contrasted with the image they wanted to project.",
            "Optimal_3": "Nice work! You used information from the text to show how Nazi leaders' actions contrasted with the image they wanted to project.",
            "Label_1": "You're on the right track! Add more information from the text to make your sentence stronger. What specific action shows that the Nazi government wasn't actually tolerant?",
            "Label_2": "It's true that many people were concerned that Germany wasn't peaceful. Be more specific. What is one action that contrasts with, or challenges, the idea that the Nazi-led government was tolerant?",
            "Label_3": "Instead of focusing on how Nazi leaders tried to seem tolerant, write about a detail that contrasts with the image they tried to project. What is one action that challenges the idea that the Nazi-led government was tolerant?",
            "Label_4": """That's a reason why Nazi leaders wanted to seem tolerant. Since this sentence uses "but," focus on a detail that contrasts with the idea that the government was tolerant instead. What is one action that challenges the tolerant image that leaders tried to project?""",
            "Label_0": "Try clearing your response and starting again. What is one action that challenges, or contrasts with, the tolerant image that leaders tried to project? Check that your response only uses information from the text.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to explain something that happened as a result of Nazi leaders' desire to promote Germany as a tolerant country.",
            "Optimal_2": "Nice work! You used information from the text to explain something that happened as a result of Nazi leaders' desire to promote Germany as a tolerant country.",
            "Optimal_3": "Nice work! You used information from the text to explain something that happened as a result of Nazi leaders' desire to promote Germany as a tolerant country.",
            "Label_1": "It's true that Nazi leaders tried to control their image before the Olympics. Add another detail to make your response more specific. What did they do to hide their beliefs from visitors?",
            "Label_2": "The Nazi government did use propaganda to control their public image—that's true. Add more information about how they did this before the 1936 Olympics. What did Nazi leaders do to try to convince visitors that Germany was tolerant?",
            "Label_3": "Instead of writing about why the Nazi Party wanted their government to be seen as tolerant, focus on what they did to accomplish that goal. What did Nazi leaders do to try to convince others that their regime wasn't dangerous?",
            "Label_4": "Instead of writing about how historians think about the Berlin Olympics today, focus on what the Nazi government did at the time. What did Nazi leaders do to try to convince others that their regime wasn't dangerous?",
            "Label_0": "Try clearing your response and starting again. What did Nazi leaders do to try to convince the world that their government was tolerant? Check that your response only uses information from the text.",
        }
    },
    "examples": {
        "because": {
            "Optimal_2": [
                "they wanted to use it as propaganda to humanize their views.",
                "this would help hide the danger of their fascism.",
                "they wanted to downplay what the threat the they were and not disrupt their agenda."
            ],
            "Optimal_3": [
                "they wanted to be able to achieve their goals without other countries interfering.",
                "it would help convince the world they were not a threat and would allow them to pursue a nationalist agenda.",
                "they thought this would make it easier to carry out their imperialist plans."
            ],
            "Label_1": [
                "they wanted to change their image the world had on them.",
                "they wanted to be seen positively.",
                "they would get the opportunity to rejoin the global community in a good way.",
                "they had a bad reputation."
            ],
            "Label_2": [
                "they thought it was a effective propaganda.",
                "they thought Games could be a tool for propaganda.",
                "they wanted to have positive propaganda for the nazi party.",
            ],
            "Label_3": [
                "athletes threatened to boycott after the Nuremberg Laws.",
                "they were persecuting Jewish people.",
                "the international news paper reported Hitler's harmful, discriminatory statements."
            ],
            "Label_5": [
                "propaganda had worked before",
                "it could be used as effective propaganda to help improve the world's opinion of Germany because similar tactics have worked in the past.",
            ],
            "Label_0": [
                "they were met with a scene that modern Olympians would most likely recoginze.",
                "they were so improve in sport."
            ]
        },
        "but": {
            "Optimal_1": [
                "Hitler refused to respect Blacks and Jewish athletes, and he did not want to shake their hands.",
                "they excluded almost every Jewish athlete from their Olympics team."
            ],
            "Optimal_2": [
                "some athletes protested the antisemitic actions of the Nazi regime like the Nuremberg Laws.",
                "athletes threatened to boycott because they didn't want to be seen as okay with the Nazi beliefs"
            ],
            "Optimal_3": [
                "people knew of Hitler's actions and persecution of the Jewish people.",
                "newspapers reported world wide on their discrimination statements and actions."
            ],
            "Label_1": [
                "they were not and were just pretending to be.",
                "it wasn't really how they felt.",
                "unfortunately the whole tolerant country thing was a show."
            ],
            "Label_2": [
                "people questioned if Germany was really peaceful.",
                "many people already had there thoughts on them.",
                "athletes didn't believe it."
            ],
            "Label_3": [
                "german leaders knew they needed to control their public image.",
                "they tried to hide their beliefs and stop publishing hate-filled papers.",
                "they hid their beliefs from the pubic."
            ],
            "Label_4": [
                "they thought they could show others they weren’t a threat.",
                "they still wanted to become imperialistic.",
                "they needed people to ignore the danger of the government."
            ],
            "Label_0": [
                "they were so strong.",
                "this wasn't an ordinary Olympics, though."
            ]
        },
        "so": {
            "Optimal_1": [
                "Nazi officials made tours to show world leaders that Germany doesn't have discrimination.",
                "they invited world leaders for planned visits to convince them.",
            ],
            "Optimal_2": [
                "they removed antisemitic posters from public places before the Games.",
                "they hide their newspapers that had hateful speeches, and told their radio host to talk good things instead of bad."
            ],
            "Optimal_3": [
                "they ordered citizens to be warm and welcoming to all visitors.",
                "they told German citizens to be easy going and polite citizens to everyone."
            ],
            "Label_1": [
                "they tried to control their public image in different ways.",
                "they used the olympics as a way to make them seem not as bad.",
                "they hid their beliefs about black and Jewish athletes."
            ],
            "Label_2": [
                "they used propaganda to get their country in line.",
                "They spread positive propaganda amongst the world.",
                "hitler created the ministry of public enlightment."
            ],
            "Label_3": [
                "they could continue their hateful regime without interference..",
                "they could improve the world's opinion of the country.",
                "other countries won't see them as a threat."
            ],
            "Label_4": [
                "people now see the Berlin Olympics a success for the Nazi party.",
                "historians think this was a success.",
                "historians now see the Berlin Olympics as a successful attempt to distract people from the growing threat of fascism."
            ],
            "Label_0": [
                "they held the Berlin Olympics.",
                "they deciede invention to sporet.",
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_2": [
                "They wanted to downplay the dangers of the Nazi party.",
                "They wanted to downplay the dangers of the Nazi party.",
                "They wanted to downplay the dangers of the Nazi party.",
            ],
            "Optimal_3": [
                "They wanted to pursue their imperialist agenda more easily.",
                "They wanted to pursue their imperialist agenda more easily.",
                "They wanted to pursue their imperialist agenda more easily.",
            ],
            "Label_1": [
                "They wanted to improve their reputation. Does not mention why.",
                "They wanted to improve their reputation. Does not mention why.",
                "They wanted to improve their reputation. Does not mention why.",
                "They wanted to improve their reputation. Does not mention why.",
            ],
            "Label_2": [
                "It is useful propaganda. Does not specify the purpose.",
                "It is useful propaganda. Does not specify the purpose.",
                "It is useful propaganda. Does not specify the purpose.",
            ],
            "Label_3": [
                "Does not explain why Nazi leaders wanted Germany to be seen as a tolerant country, but gives a consequence or a contrasting idea.",
                "Does not explain why Nazi leaders wanted Germany to be seen as a tolerant country, but gives a consequence or a contrasting idea.",
                "Does not explain why Nazi leaders wanted Germany to be seen as a tolerant country, but gives a consequence or a contrasting idea.",
            ],
            "Label_5": [
                "Propaganda had worked in the past. Does not mention the present goal.",
                "Propaganda had worked in the past. Does not mention the present goal.",
            ],
            "Label_0": [
                "Does not explain why Nazi leaders wanted Germany to be seen as a tolerant country.",
                "Does not explain why Nazi leaders wanted Germany to be seen as a tolerant country.",
            ]
        },
        "but": {
            "Optimal_1": [
                "Gives an example of an intolerant action, like the invasion of Poland or the exclusion of Jewish athletes.",
                "Gives an example of an intolerant action, like the invasion of Poland or the exclusion of Jewish athletes.",
            ],
            "Optimal_2": [
                "There were protests. Mentions a specific intolerant action.",
                "There were protests. Mentions a specific intolerant action.",
            ],
            "Optimal_3": [
                "The persecution/hate was well-documented.",
                "The persecution/hate was well-documented.",
            ],
            "Label_1": [
                "This was a show. Does not give an example of an intolerant action.",
                "This was a show. Does not give an example of an intolerant action.",
                "This was a show. Does not give an example of an intolerant action.",
            ],
            "Label_2": [
                "Other people were skeptical or boycotted the event. Does not specify why.",
                "Other people were skeptical or boycotted the event. Does not specify why.",
                "Other people were skeptical or boycotted the event. Does not specify why.",
            ],
            "Label_3": [
                "The German leaders hid their beliefs.",
                "The German leaders hid their beliefs.",
                "The German leaders hid their beliefs.",
            ],
            "Label_4": [
                "The German leaders wanted to pursue their agenda.",
                "The German leaders wanted to pursue their agenda.",
                "The German leaders wanted to pursue their agenda.",
            ],
            "Label_0": [
                "Does not show a contrasting or suprising idea about the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.",
                "Does not show a contrasting or suprising idea about the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.",
            ]
        },
        "so": {
            "Optimal_1": [
                "They invited world leaders for controlled visits.",
                "They invited world leaders for controlled visits.",
            ],
            "Optimal_2": [
                "They hid antisemitic publications.",
                "They hid antisemitic publications.",
            ],
            "Optimal_3": [
                "They instructed their citizens to be good hosts.",
                "They instructed their citizens to be good hosts.",
            ],
            "Label_1": [
                "They hid their beliefs. Does not mention how.",
                "They hid their beliefs. Does not mention how.",
                "They hid their beliefs. Does not mention how.",
            ],
            "Label_2": [
                "They used propaganda or created a ministry. Does not cite any actions taken in relation to the preparation of the Olympics.",
                "They used propaganda or created a ministry. Does not cite any actions taken in relation to the preparation of the Olympics.",
                "They used propaganda or created a ministry. Does not cite any actions taken in relation to the preparation of the Olympics.",
            ],
            "Label_3": [
                "They continued their plans without resistance.",
                "They continued their plans without resistance.",
                "They continued their plans without resistance.",
            ],
            "Label_4": [
                "Historians see the Olympics as a success for the Nazis. Does not mention any of their actions.",
                "Historians see the Olympics as a success for the Nazis. Does not mention any of their actions.",
                "Historians see the Olympics as a success for the Nazis. Does not mention any of their actions.",
            ],
            "Label_0": [
                "Does not give a consequence of the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.",
                "Does not give a consequence of the fact that Nazi leaders wanted Germany to be seen as a tolerant country for the 1936 Berlin Olympics.",
            ]
        }

    }
}