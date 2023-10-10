passage = {
    "files": {
        "because": {
            "train": "data/automl/villages_because_v2_train.jsonl",
            "validation": "data/automl/villages_because_v2_validation.jsonl",
            "test": "data/automl/villages_because_v2_test.jsonl"
        },
        "but": {
            "train": "data/automl/villages_but_v2_train.jsonl",
            "validation": "data/automl/villages_but_v2_validation.jsonl",
            "test": "data/automl/villages_but_v2_test.jsonl"
        },
        "so": {
            "train": "data/automl/villages_so_v2_train.jsonl",
            "validation": "data/automl/villages_so_v2_validation.jsonl",
            "test": "data/automl/villages_so_v2_test.jsonl"
        },
    },
    "text": """**The Chime Heard** '**Round Japan**

It's 5 p.m. in Japan, and a song begins to play over the loudspeakers in the streets. Children in Tokyo know that the 5 p.m. chime means it's time to head home before it gets dark, but in some rural villages, no children are running home to their parents. Nobody is playing outside, nobody is cooking dinner for their kids, and in certain places, nobody is even there to hear the chime.

More and more rural villages in Japan are falling victim to the phenomenon called shoushikoureika (pronounced show-she-ko-ray-kah): people are getting older, fewer children are being born, and young people are moving to large cities. According to the Japan Policy Council, almost half of Japanese towns could be completely abandoned by 2040, with the 5 p.m. chime echoing throughout hundreds of empty villages.

**An Aging Population**

Decades ago, rural villages were full of young children who planned on becoming farmers or miners in the Japanese countryside, just like their parents. However, as large cities like Tokyo and Osaka developed, more young adults decided to move away from their rural hometowns to pursue educational opportunities and jobs at Japanese companies like Sony, Toyota, and Nintendo. These jobs are more profitable and less physically demanding than farming, but this trend has left aging parents and grandparents alone in rural villages.

Kensaku Fueki's three daughters all moved away from their hometown of Tochikubo to find jobs in Tokyo, three hours away. He told The Atlantic, "I don't expect them to come back. It's very tough to live on farming." Rural villages do not have large universities or high-paying jobs to attract young people, so elderly people who have remained in the countryside are struggling to keep their villages alive. Without young people to have children, which increases the population, many villages in Japan are either completely deserted or the majority of the citizens are over 65 years old. In addition, when there aren't enough working-age residents, the local government receives less tax money to use on retirement homes and health care for elderly residents.

**Hope for Rural Villages**

Attracting young permanent residents is the main goal for some rural villages. Mayumi Matsuyama, the head of planning and finance for a small mountain town called Yusuhara, told EFE News Service, "We're facing a challenge. All our efforts are now focused on making the [young] people move here permanently. Otherwise, we will not be able to support ourselves."

According to Deutsche Bank's 2019 annual Mapping the World's Prices report, monthly rent for a two bedroom apartment in Tokyo is typically around the equivalent of $1,900. However, the government of Yusuhara is offering houses for the equivalent of around $130 a month, only 7% of the average price, in hopes of drawing in young people. In addition, if a young person wants to build their own house in Yusuhara, the local government will give them more than $27,000 to do so.

Some villages have slightly increased their populations through these measures, but the overall number of young people in Japanese rural villages is still very low. As Mihoko Onoue, a realtor in a rural village, explains, "depopulation is an unstoppable phenomenon happening all across the nation. It's neither good nor bad, but something we must accept."
""",
    "plagiarism": {
        "because": "Rural villages do not have large universities or high-paying jobs to attract young people, so elderly people who have remained in the countryside are struggling to keep their villages alive. Without young people to have children, which increases the population, many villages in Japan are either completely deserted or the majority of the citizens are over 65 years old. In addition, when there aren't enough working-age residents, the local government receives less tax money to use on retirement homes and health care for elderly residents.",
        "but": "However, as large cities like Tokyo and Osaka developed, more young adults decided to move away from their rural hometowns to pursue educational opportunities and jobs at Japanese companies like Sony, Toyota, and Nintendo. These jobs are more profitable and less physically demanding than farming, but this trend has left aging parents and grandparents alone in rural villages.",
        "so": "According to Deutsche Bank's 2019 annual Mapping the World's Prices report, monthly rent for a two bedroom apartment in Tokyo is typically around the equivalent of $1,900. However, the government of Yusuhara is offering houses for the equivalent of around $130 a month, only 7% of the average price, in hopes of drawing in young people. In addition, if a young person wants to build their own house in Yusuhara, the local government will give them more than $27,000 to do so.",
    },
    "prompts": {
        "because": "Young residents are essential to the survival of rural Japanese villages because",
        "but": "Young residents are essential to the survival of rural Japanese villages, but",
        "so": "Young residents are essential to the survival of rural Japanese villages, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why young residents are essential to the survival of rural Japanese villages.

A response is optimal when it they contain at least two from these five categories:
- young residents have children,
- young residents make the population increase and prevent towns from being abandoned,
- young residents can work,
- young residents can work support elderly people,
- young residents can work pay taxes and help the economy

A response is suboptimal when
- it contains none or only one of the five categories above.
- it misuses the conjuction,
- it is not related to the text.
        """,
        "but": """Their response must use information from the text to show a contrasting or surprising idea about the fact that young residents are essential to the survival of rural Japanese villages.

A response is optimal when it says young people are moving to cities and leaving rural areas in search for higher-paying jobs or educational opportunities. It must include a verb like moving, leaving or struggling.

A response is suboptimal when:
- it says young people are moving to cities, but does not mention why,
- it says rural areas struggle to attract young people, but does not mention why,
- it says farming is difficult or rural villages have no education or jobs, but misses the action of moving or leaving,
- it does not show a contrasting or surprising idea about the fact that young residents are essential to the survival of rural Japanese villages.
        """,
        "so": """Their response must use information from the text to show a consequence of the fact that young residents are essential to the survival of rural Japanese villages.

A response is optimal when it says:
- Yusuhara offers houses for $130, $1770 less than the average, or 7% of the average price,
- Yusuhara gives young people money to build houses.

A response is suboptimal when:
- it says villages are trying to attract young people, but not how,
- it says villages are offering lower house prices, but misses the name 'Yusuhara',
- it says villages are giving people money, but does not mention building houses,
- it says villages offer money to build houses, but misses the town name 'Yusuhara',
- it says the government is offering houses, but misses that the government is offering 'cheaper' houses, or is paying people to build houses,
- it says Tokyo instead of Yusuhara,
- it does not show a consequence of the fact that young residents are essential to the survival of rural Japanese villages.
        """
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why young residents are essential for the survival of rural Japanese villages.",
            "Label_1": "It's true that young people bring money to rural villages! Now add another reason why young residents are important to rural villages.",
            "Label_2": "That's true! Now be more specific. What is one way that young people support rural villages?",
            "Label_3": "It's true that young people can work in rural villages! Now add another reason why young residents are important to rural villages.",
            "Label_4": "It's true that young people can have children, which benefits rural villages! Now add another reason why young residents are important to rural villages.",
            "Label_5": "Try clearing your response and starting again. Because is used to explain why or give a reason. Go back to the text and look for a way that young people support rural villages.",
            "Label_6": "It's true that young people help keep rural villages alive by increasing the population! Now add another reason why young residents are important to rural villages.",
            "Label_7": "It's true that young people can support the elderly people in rural villages! Now add another reason why young residents are important to rural villages.",
            "Label_0": "Try clearing your response and starting again. How do young people support rural villages? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrasting idea about young residents being essential for the survival of rural Japanese villages.",
            "Label_1": "That's true! Now be more specific. Why are young people leaving rural areas and moving to cities?",
            "Label_2": "That's true! Now be more specific. Why are rural villages struggling to attract and keep young residents?",
            "Label_3": "That's true! Now be more specific. What are young people doing as a result of these factors?",
            "Label_4": "Try clearing your response and starting again. But is used to provide an opposing or contrasting idea. Go back to the text and look for a reason why so few young people are living in rural villages.",
            "Label_0": "Try clearing your response and starting again. Why are so few young people living in rural villages? Check that your response only uses information from the text.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show an effect or consequence of the fact that young residents are essential to the survival of rural Japanese villages.",
            "Optimal_2": "Nice work! You used information from the text to show an effect or consequence of the fact that young residents are essential to the survival of rural Japanese villages.",
            "Label_1": "It's true that rural villages are trying to attract young people! Now be more specific. How are local governments attempting to convince young people to live in rural villages?",
            "Label_2": "It's true that lower housing prices are being offered! Now be more specific. Which rural village is making this offer?",
            "Label_3": "It's true that young people are receiving money from rural governments! Now be more specific. What is this money for?",
            "Label_4": "Try clearing your response and starting again. So is used to show an effect or consequence. Go back to the text and look for a way that rural governments are attempting to attract young people.",
            "Label_5": "It's true that young people are being offered money to build houses! Now be more specific. Which rural village is making these offers?",
            "Label_6": "Revise your response. Check the text for details. What are rural governments offering young people?",
            "Label_7": "You have the right idea! Now make sure you're using the correct town's name.",
            "Label_0": "Try clearing your response and starting again. How are rural villages attempting to attract young people? Check that your response only uses information from the text.",
        }
    },
    "labels": {
        "because": {
            "Optimal_1": """Responses must contain something from two of these five categories:
- have children
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- working-age residents / farming / mining
- support elderly people
- pay taxes / help the economy / give the gov or town money
            """,
            "Label_1": """Responses mention that young residents pay taxes, help the economy, or bring money, and add something from one of these four categories:
- have children
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- working-age residents / farming / mining
- support elderly people
            """,
            "Label_2": """Responses are too general and don't really mention any of the 5 valid categories:
- have children
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- working-age residents / farming / mining
- support elderly people
- pay taxes / help the economy / give the gov or town money
            """,
            "Label_3": """Responses mention farming/mining/work-force and need to add something from one of these four categories:
- have children
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- support elderly people
- pay taxes / help the economy / give the gov or town money""",
            "Label_4": """Responses mention having children, and add something from one of these four categories:
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- working-age residents / farming / mining
- support elderly people
- pay taxes / help the economy / give the gov or town money
            """,
            "Label_5": """The response misuses the conjunction.""",
            "Label_6": """The response mentions population increase/keeping the village alive, and adds something from one of these four categories:
- have children
- working-age residents / farming / mining
- support elderly people
- pay taxes / help the economy / give the gov or town money
            """,
            "Label_7": """The response mentions supporting the elderly, and adds something from one of these four categories:
- have children
- increase population / repopulate / population decreases without them / prevent towns from being abandoned, being deserted, or filled with elderly people, keep villages alive / increase number of young people / shoushikoureika
- working-age residents / farming / mining
- pay taxes / help the economy / give the gov or town money
            """,
            "Label_0": "Miscellaneous"
        },
        "but": {
        },
        "so": {
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "they are able to have children, which increases the population, ensuring that villages are not deserted.",
                "the majority of citizens aren't working-age, so the government has less tax money to fund healthcare and retirement homes."
            ],
            "Label_1": [
                "the young people bring more taxes to the local government.",
                "they keep the economy going.",
            ],
            "Label_2": [
                "elderly people are struggling.",
                "younger people bring more joy and liveliness to the area.",
            ],
            "Label_3": [
                "young people work jobs to help support the village.",
                "young people help with farming and mining.",
            ],
            "Label_4": [
                "the elderly people can't have children.",
                "the younger people are able to have kids.",
            ],
            "Label_5": [
                "young residents decided to move away from their rural hometowns to pursue educational opportunties and jobs at Japanese companies like Sony, Toyota, and Nintendo.",
                "to solve this problem Yusuhara is offering houses for $130 a month.",
            ],
            "Label_6": [
                "without young people they can't increase the population.",
                "the population rate in the villages are going down.",
            ],
            "Label_7": [
                "they are able to care for and support the older people",
                "the elderly people cant support themselves.",
            ],
            "Label_0": [
                "in japan the victims in phenomenon.",
                "the young residents are usually the ones who rural, young people can get the older people to listen from the way they talk for what they say to them",
            ]
        },
        "but": {
            "Optimal_1": [
                "rural villages do not have things that attract young people like good paying jobs or big universities, so they are moving into cities.",
                "many young people are choosing to move into larger cities such as Tokyo and Osaka because of jobs more profitable and less physically demanding.",
                "many young residents are moving to big cities because they offer better educations and better paying jobs.",
                "many young people do not want to live hard lives as farmers and would rather work in large cities at large companies.",
            ],
            "Label_1": [
                "big cities like Tokyo and Osaka developed, young adult decided to move away.",
                "young residents continue to move out to the big cities.",
                "many young adults are moving away from their rural hometown.",
            ],
            "Label_2": [
                "villages in Japan are victims to shoushikoureika so fewer children are being born.",
                "the overall number of young people is still low.",
                "Japanese villages do not offer anything to attract young people.",
            ],
            "Label_3": [
                "jobs in the big city are more profitable and less physically demanding.",
                "they do not have universities or high-paying jobs.",
                "it is very hard to live on farming.",
                "large cities like Tokyo and Osaka have more educational opportunities and jobs for them.",
            ],
            "Label_4": [
                "they are trying to get them to move back permanently by lowering house prices and giving them money to build houses there.",
                "there aren't enough young people to help out in the village so the government can't provide for the elderly in the retirement homes.",
                "they also reproduce and they increase the population of the rural villages.",
            ],
            "Label_0": [
                "depopulation is inevitable and it is just something society has to accept.",
                "it isn't necessary for them to help.",
                "children in Tokyo know that the 5 p.m. chime means it's time to go home before it gets dark.",
            ]
        },
        "so": {
            "Optimal_1": [
                "the government of Yusuhara is offering cheap housing, in hopes of drawing in young children.",
                "the Yushuhara government is offering around $130 dollars a month for a house compared to around $1,700 a month in Tokyo.",
            ],
            "Optimal_2": [
                "the government of Yasuhara will give the young people more than $27,000 to build their own house.",
                "the government of Yusuhara is offering money for young residents to move back and build a house.",
            ],
            "Label_1": [
                "they try and make everything attractive to make more people come to the Japanese village.",
                "attracting permanent young residents is the main goal for a lot of rural villages.",
            ],
            "Label_2": [
                "the villages make housing cheaper then the big cities.",
                "villages are trying to draw young people in by making rent $130 a month, which is 7% of the average price.",
            ],
            "Label_3": [
                "They are trying to draw back the young people by give them money.",
                "young people are being given money and funding",
            ],
            "Label_4": [
                "rural villages don't give have good universities and high paying jobs.",
                "they are leaving countryside in droves and concentrating in larger cities.",
            ],
            "Label_5": [
                "the local government gives young people $27,000 to build there own houses.",
                "the local government is offering incentives to get more young people to live in the village such as money to build houses.",
            ],
            "Label_6": [
                "the government is offering houses to young people.",
                "they are attracting young permanent residents by giving them a home.",
            ],
            "Label_7": [
                "the Tokyo villages are giving young people $27,000 dollars to build a home in their village so they will move there.",
                "the Tokyo government lowers the rent to $130 a month.",
            ],
            "Label_0": [
                "they will be very benificial to society, to help the community or offer things",
                "Mayumi Matsuyama mentioned this problem to EFE new services.",
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_1": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains two of these elements: having children and population increase.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains two of these elements: working-age residents and paying taxes.",
            ],
            "Label_1": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: taxes/economy.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: taxes/economy."
            ],
            "Label_2": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response does not contain any valid elements.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response does not contain any valid elements."
            ],
            "Label_3": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: working-age residents.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: working-age residents."
            ],
            "Label_4": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: having children.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: having children."
            ],
            "Label_5": [
                "This response gives a contrasting idea about the fact that young residents are essential to the survival of rural Japanese villages, not a reason.",
                "This response gives a consequence of the fact that young residents are essential to the survival of rural Japanese villages, not a reason."
            ],
            "Label_6": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: population increase.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: population increase."
            ],
            "Label_7": [
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: supporting elderly people.",
                "An optimal response must contain at least two of the five valid elements: having children, supporting elderly people, taxes/economy, population increase, and working-age residents. This response contains one element only: supporting elderly people."
            ],
            "Label_0": [
                "This response does not give a reason why young residents are essential to the survival of rural Japanese villages.",
                "This response does not give a reason why young residents are essential to the survival of rural Japanese villages."
            ]
        },
        "but": {
            "Optimal_1": [
                "Young people are moving to cities in search for education or higher-paying jobs. Includes a verb like leaving, moving or struggling.",
                "Young people are moving to cities in search for education or higher-paying jobs. Includes a verb like leaving, moving or struggling.",
                "Young people are moving to cities in search for education or higher-paying jobs. Includes a verb like leaving, moving or struggling.",
                "Young people are moving to cities in search for education or higher-paying jobs. Includes a verb like leaving, moving or struggling.",
            ],
            "Label_1": [
                "Young people are moving to cities.",
                "Young people are moving to cities.",
                "Young people are moving to cities.",
            ],
            "Label_2": [
                "Rural areas struggle to attract young people.",
                "Rural areas struggle to attract young people.",
                "Rural areas struggle to attract young people.",
            ],
            "Label_3": [
                "Rural villages lack educational opportunities or high-paying jobs.",
                "Rural villages lack educational opportunities or high-paying jobs.",
                "Rural villages lack educational opportunities or high-paying jobs.",
                "Rural villages lack educational opportunities or high-paying jobs.",
            ],
            "Label_4": [
                "Shows a consequence of the fact that young residents are essential to the survival of rural Japanese villages.",
                "Says why young residents are essential to the survival of rural Japanese villages.",
                "Says why young residents are essential to the survival of rural Japanese villages.",
            ],
            "Label_0": [
                "Does not show a contrasting or surprising idea about the fact that young residents are essential to the survival of rural Japanese villages.",
                "Does not show a contrasting or surprising idea about the fact that young residents are essential to the survival of rural Japanese villages.",
                "Does not show a contrasting or surprising idea about the fact that young residents are essential to the survival of rural Japanese villages.",
            ]
        },
        "so": {
            "Optimal_1": [
                "Yusuhara offers cheap housing.",
                "Yusuhara offers cheap housing.",
            ],
            "Optimal_2": [
                "Yusuhara gives young people money to build houses.",
                "Yusuhara gives young people money to build houses.",
            ],
            "Label_1": [
                "Villages are trying to attract young people. Does not mention how.",
                "Villages are trying to attract young people. Does not mention how.",
            ],
            "Label_2": [
                "Villages offer cheap housing. Does not mention the name Yusuhara.",
                "Villages offer cheap housing. Does not mention the name Yusuhara.",
            ],
            "Label_3": [
                "Villages are giving people money. Does not mention building houses",
                "Villages are giving people money. Does not mention building houses",
            ],
            "Label_4": [
                "Shows a contrasting idea to the fact that young residents are essential to the survival of rural Japanese villages, not a consequence.",
                "Shows a contrasting idea to the fact that young residents are essential to the survival of rural Japanese villages, not a consequence.",
            ],
            "Label_5": [
                "Villages offer money to build houses, but does not mention the name Yusuhara.",
                "Villages offer money to build houses, but does not mention the name Yusuhara.",
            ],
            "Label_6": [
                "The government is offering houses. Does not say that the government is offering 'cheaper' houses, or is paying people to build houses",
                "The government is offering houses. Does not say that the government is offering 'cheaper' houses, or is paying people to build houses",
            ],
            "Label_7": [
                "Mentions Tokyo instead of Yusuhara.",
                "Mentions Tokyo instead of Yusuhara.",
            ],
            "Label_0": [
                "Does not give a consequence of the fact that young residents are essential to the survival of rural Japanese villages.",
                "Does not give a consequence of the fact that young residents are essential to the survival of rural Japanese villages.",
            ]
        }
    }
}