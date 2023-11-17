passage = {
    "files": {
        "because": {
            "train": "data/automl/bereal_because_v4_train.jsonl",
            "validation": "data/automl/bereal_because_v4_validation.jsonl",
            "test": "data/automl/bereal_because_v4_test.jsonl" # "data/automl/bereal_because_v4_problems.jsonl"
        },
        "but": {
            "train": "data/automl/bereal_but_v4_train.jsonl",
            "validation": "data/automl/bereal_but_v4_validation.jsonl",
            "test": "data/automl/bereal_but_v4_test.jsonl"
        },
        "so": {
            "train": "data/automl/bereal_so_v4_train.jsonl",
            "validation": "data/automl/bereal_so_v4_validation.jsonl",
            "test": "data/automl/bereal_so_v4_test.jsonl"
        },
    },
    "text": """⚠️ Time to BeReal. ⚠️

Every day, millions of people receive this notification from the popular social media app BeReal. They have two minutes to snap a picture to share with their friends—whether they’re climbing a mountain or just sitting at home on the couch.

**What is BeReal?**

First released in 2020, BeReal claims to be different from other social media apps. In the app store, its description explains, “BeReal won’t make you famous. If you want to become an influencer you can stay on TikTok and Instagram.”

Unlike TikTok or Instagram, BeReal doesn’t have filters or allow users to edit their photos. Instead, users are required to post a picture of themselves within two minutes of when they get their daily notification, forcing them to post even if what they're doing looks boring or embarrassing. Everyone posts at the same time, so users can quickly get a sense of everything their friends are up to, from hanging out with friends, spending time outside, or attending a concert to simply lying in bed, doing homework, or walking the dog.

Many, like Meena Kuduva, a student at the University of Washington Seattle, were quickly attracted to its “pro-authenticity” philosophy. Kuduva explained to the student newspaper, “I use BeReal so much more than the other [social media apps] because it feels so much more casual. There’s a lot less pressure to post and look a certain way.”

**Time to BeFake**

Some aren’t sold on the new app’s promise of authenticity. One reason is because, even though the app encourages users to post within the first two minutes, it’s possible to post later on when you’re doing something more interesting. The post will simply be labeled as “late.”

“In all honesty, I tend to wait until I’m in a scenic or cool location,” said New York City dog walker Macartney MacDonald, who has been using BeReal since June 2022, in a Huffington Post article. “And I try to make sure that I at least look decent.”

Others, like the writer Emily Bootle, argue that it's impossible to be truly authentic on social media. She claims that many people who use the app are still presenting carefully curated versions of themselves. Instead of pretending to have glamorous, exciting lives, however, they are pretending to be authentic. “If ‘realness’ is performed by 53 million people every day,” Bootle writes in an article for the New Statesman, “it becomes […] ‘inauthentic’.”

**A Growing Trend**

Though BeReal may offer upsides and downsides to its users, there is no doubt that the app has had a huge impact. In fact, the amount of people who use the app each month grew over 315% from 2021 to 2022.

It's impossible to say whether BeReal will remain popular, but Mariah Macias, a junior at Pepperdine University, feels optimistic about the app's future: “I feel like it’ll continue to stay decently popular for a good amount of time,” Macias told the student paper. “I don’t really see it dying out because I feel like most people are pretty consistent about doing it. And there’s such a big community of people doing it—let’s be real together.”""",
    "plagiarism": {
        "because": """Unlike TikTok or Instagram, BeReal doesn’t have filters or allow users to edit their photos. Instead, users are required to post a picture of themselves within two minutes of when they get their daily notification, forcing them to post even if what they're doing looks boring or embarrassing. Everyone posts at the same time, so users can quickly get a sense of everything their friends are up to, from hanging out with friends, spending time outside, or attending a concert to simply lying in bed, doing homework, or walking the dog.
Many, like Meena Kuduva, a student at the University of Washington Seattle, were quickly attracted to its “pro-authenticity” philosophy. Kuduva explained to the student newspaper, “I use BeReal so much more than the other [social media apps] because it feels so much more casual. There’s a lot less pressure to post and look a certain way.”""",
        "but": """Some aren’t sold on the new app’s promise of authenticity. One reason is because, even though the app encourages users to post within the first two minutes, it’s possible to post later on when you’re doing something more interesting. The post will simply be labeled as “late.”
“In all honesty, I tend to wait until I’m in a scenic or cool location,” said New York City dog walker Macartney MacDonald, who has been using BeReal since June 2022, in a Huffington Post article. “And I try to make sure that I at least look decent.”
Others, like the writer Emily Bootle, argue that it's impossible to be truly authentic on social media. She claims that many people who use the app are still presenting carefully curated versions of themselves. Instead of pretending to have glamorous, exciting lives, however, they are pretending to be authentic. “If ‘realness’ is performed by 53 million people every day,” Bootle writes in an article for the New Statesman, “it becomes […] ‘inauthentic’.”""",
        "so": "Though BeReal may offer upsides and downsides to its users, there is no doubt that the app has had a huge impact. In fact, the amount of people who use the app each month grew over 315% from 2021 to 2022."
        },
    "prompts": {
        "because": "Some consider BeReal a more authentic form of social media because",
        "but": "Some consider BeReal a more authentic form of social media, but",
        "so": "Some consider BeReal a more authentic form of social media, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why some people consider BeReal a more authentic form of social media.

A response is optimal when it says:
- people use no filter or editing, and post realistic photos,
- people have a limited period to post and post realistic photos,
- people have less pressure to post.

A response is suboptimal when:
- it says people use no filter or editing, but does not mention realistic photos,
- it says people have a limited period to post, but does not mention realistic photos,
- it says posts on BeReal are more in the moment, casual or authentic, but does not mention why,
- it says BeReal does not make people famous,
- it says everyone posts at the same time, but does not mention realistic photos,
- it says BeReal posts are more realistic photos, but does not mention that people use no filter or have a limited time period to post,
- it misuses the conjuction,
- it is not related to the text.
        """,
        "but": """Their response must use information from the text to show a contrasting or suprising idea about the fact that some people consider BeReal a more authentic form of social media.

A response is optimal when it says:
- people can post later, and do something interesting, attractive, curated or inauthentic,
- it is impossible to be authentic on social media.

A response is suboptimal when:
- it says people can post later, but does not mention they may do something interesting or attractive,
- it says BeReal is inauthentic, without saying why,
- it says people try to curate their posts, without mentioning it is possible to post later,
- it says BeReal may not remain popular,
- it misuses the conjuction,
- it is not related to the text.
        """,
        "so": """Their response must use information from the text to show a consequence of the fact that some people consider BeReal a more authentic form of social media.

A response is optimal when it says the app has grown by 315%.

A response is suboptimal when:
- it says the app has grown, but does not mention the growth rate,
- it says people think it will remain popular,
- it says people enjoy it,
- it says people use it more than other platforms,
- it misuses the conjunction,
- it is not related to the text.
        """
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why some people think BeReal is a more authentic form of social media.",
            "Optimal_2": "Nice work! You used information from the text to explain why some people think BeReal is a more authentic form of social media.",
            "Optimal_3": "Nice work! You used information from the text to explain why some people think BeReal is a more authentic form of social media.",
            "Label_1": "That's true—BeReal doesn't allow filters or photo editing. Now make your response even stronger by explaining why this makes the app feel more authentic. What is different about photos that aren't edited or filtered?",
            "Label_2": "That's true—people have a limited amount of time to post on BeReal. Now make your response even stronger by explaining why this makes the app feel more authentic. What kinds of photos does this lead to?",
            "Label_3": "That's true—many people think BeReal is more casual than other forms of social media. Now make your response even stronger by explaining why. What makes BeReal feel more casual?",
            "Label_4": "Revise your response. It's true that BeReal isn't intended to make people famous. Why does this lead to the app feeling more authentic than other forms of social media?",
            "Label_5": "That's true—BeReal encourages people to post at the same time. Now make your response even stronger by explaining why this makes it feel more authentic. What kinds of photos does this lead to?",
            "Label_6": "That's true—BeReal can lead to more realistic photos. Now make your response even stronger by explaining why this happens. How does the app encourage realistic photos?",
            "Label_7": "Try clearing your response and starting again. Because is used to tell why or give a reason. Why do some people think BeReal is a more authentic form of social media?",
            "Label_8": "Try clearing your response and starting again. Because is used to tell why or give a reason. Why do some people think BeReal is a more authentic form of social media?",
            "Label_0": "Try clearing your response and starting again. Why do some people think BeReal is a more authentic form of social media? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrast to the idea that BeReal is more authentic than other forms of social media.",
            "Optimal_3": "Nice work! You used information from the text to show a contrast to the idea that BeReal is more authentic than other forms of social media.",
            "Label_1": "That's true—people can post their BeReals later. Now make your response even stronger by explaining how this contrasts with the idea of BeReal being authentic. Why are late BeReals inauthentic?",
            "Label_2": "That's true—some people think BeReal is inauthentic. Why do they think this?",
            "Label_3": "That's true—some people still try to curate what they post on BeReal. Now make your response even stronger by explaining how they do this. How do some people manage to curate their BeReals?",
            "Label_4": "Revise your work. Instead of focusing on the app's popularity, focus on a contrast to the fact that some people think the app is more authentic than other forms of social media. Why do some people think the app is inauthentic?",
            "Label_5": "Try clearing your response and starting again. But is used to introduce a contrasting idea. What is a contrast to the idea that some people think BeReal is more authentic than other forms of social media?",
            "Label_6": "Try clearing your response and starting again. But is used to introduce a contrasting idea. What is a contrast to the idea that some people think BeReal is more authentic than other forms of social media?",
            "Label_0": "Try clearing your response and starting again. What is a contrast to the idea that some people think BeReal is more authentic than other forms of social media? Check that your response only uses information from the text.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show a consequence of the fact that some people think BeReal is a more authentic form of social media.",
            "Label_1": "That's true—the app has grown in popularity. Now make your response even stronger by adding a specific number from the text. How much has it grown?",
            "Label_2": "Revise your work. Instead of talking about what people think will happen with BeReal, focus on a consequence of the fact that many people think it is a more authentic form of social media.",
            "Label_3": "Revise your work. Instead of focusing on the fact that people enjoy using the app, talk about what happened to the app as a result of them liking it.",
            "Label_4": "Try clearing your response and starting again. So is used to give consequence or effect. What is a consequence of the fact that some people think BeReal is a more authentic form of social media?",
            "Label_5": "Try clearing your response and starting again. So is used to give consequence or effect. What is a consequence of the fact that some people think BeReal is a more authentic form of social media?",
            "Label_6": "That's true—some people prefer BeReal to other social media platforms. What has happened to BeReal as a result?",
            "Label_0": "Try clearing your response and starting again. What is a consequence of the fact that some people think BeReal is a more authentic form of social media? Check that your response only uses information from the text.",
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "users cannot edit photos, so interactions with friends are more realistic."
            ],
            "Optimal_2": [
                "people have two minutes to post themselves even if it looks boring or not."
            ],
            "Optimal_3": [
                "there is a lot less pressure when they post on BeReal than any other social media."
            ],
            "Label_1": [
                "BeReal does not have any filters and does not allow users to edit their photos.",
                "the app does not allow users to alter their photos in any way as it does not feature any filters.",
            ],
            "Label_2": [
                "the app prompts users to post a picture within 2 minutes.",
                "users are tasked with posting a picture of themselves within a specific time range of when they get their daily notification.",
            ],
            "Label_3": [
                "it feels more casual than other social medias.",
                "it helps users be more authentic online.",
            ],
            "Label_4": [
                "it wont make anyone famous unlike other social media apps.",
                "it wont make someone famous.",
            ],
            "Label_5": [
                "everyone posts at the same time.",
                "everybody posts pictures at the same time when they get the notification",
            ],
            "Label_6": [
                "it provides a view of what people are actually doing.",
                "it encourages realistic photos by showing friends.",
            ],
            "Label_7": [
                "users are able to post later after the notification is released, so they have time to choose their photos.",
                "people who use the app are still presented carefully",
            ],
            "Label_8": [
                "the app's usage grew by 315% in one year.",
                "the number of app users who started using the app monthly in 2022 was more than 315% of the number of app users who started using the app monthly in 2021.",
            ],
            "Label_0": [
                "they could use instagram.",
            ],
        },
        "but": {
            "Optimal_1": [
                "it is possible to post later when they are doing something more interesting.",
                "some people do not feel it's authentic because the app still allows users to post late even though it encourages them to post within the first two minutes and it will be labeled late.",
            ],
            "Optimal_3": [
                "some argue that it's impossible to be authentic on social media.",
                "some critics argue that it is not possible to be completely authentic on social media.",
            ],
            "Label_1": [
                "it is possible to post a picture later than the 2 minutes and it'll only be labeled late.",
                "it still allows people to post at different times.",
                "some people don't because they're allowed to not post in the 2 minute time limit.",
            ],
            "Label_2": [
                "it allows the user to misrepresent the authenticity of their photos.",
                "people aren't authentic when using bereal.",
                "others are not so sure about it.",
            ],
            "Label_3": [
                "people can fake versions of themselves on the app.",
                "some argue that many curate their pictures to look better and make their lives seem more glamourous.",
                "some people present the app carefully by going to places that look fun and are not boring.",
            ],
            "Label_4": [
                "it may not stay popular for long.",
                "some people speculate the app could be a short-lived trend.",
            ],
            "Label_5": [
                "BeReal doesn't have filters or allow users to edit their photos",
                "people are expected to post within two minutes so it shows what they are actually doing at that moment.",
            ],
            "Label_6": [
                "the number of monthly users of the app increased by 315% in 2022 compared to 2021.",
                "user engagement with the app grew by 315%.",
            ],
            "Label_0": [
                "people get on it everyday to post what they’re doing every single day.",
            ]
        },
        "so": {
            "Optimal_1": [
                "from 2021 to 2022 the app and amount of people using it grew rapidly by 315%.",
                "the number of users increased by 315% within one year.",
                "the number of people using the app increased by 315% over the course of 2021 and 2022.",
            ],
            "Label_1": [
                "it has grown so much more over time.",
                "its popularity has exploded recently.",
                "the app has become very popular and millions have downloaded it.",
            ],
            "Label_2": [
                "it is likely to remain popular for people to share and express themselves.",
                "they say it isn’t gonna die out because there’s so many people who enjoy being real.",
                "the app will stay popular because of the amount of people who is consistently using it.",
            ],
            "Label_3": [
                "it positively impacts relationships.",
                "many people enjoy it everyday.",
                "many users enjoy it because of it is not like other apps because it allows them to be real.",
            ],
            "Label_4": [
                "BeReal doesn't have filters or allows anyone to edit, so there's less pressure to post and look a certain way",
                "users are encouraged to post within a few minutes.",
            ],
            "Label_5": [
                "one can still post after the two-minute window, opening the door for inauthentic pictures, and some people will take pictures only if they look good.",
                "there are others who believe that it really isn't possible to be authentic on social media.",
            ],
            "Label_6": [
                "many people claim that they use it more than other forms of social media.",
                "they prefer to post there rather than any other social media platform.",
            ],
            "Label_0": [
                "it’s time to bereal",
                "people are talking abut bing and community and being true too everyone.",
            ]
        }
    },
    "evaluation": {
        "but": {
            "Optimal_1": [
                "It says people can post later when they are doing something interesting.",
                "It says people can post later when they are doing something interesting."
            ],
            "Optimal_3": [
                "It says it is impossible to be authentic on social media.",
                "It says it is impossible to be authentic on social media."
            ],
            "Label_1": [
                "It says people can post later, but does not mention they may do something interesting or attractive.",
                "It says people can post later, but does not mention they may do something interesting or attractive.",
                "It says people can post later, but does not mention they may do something interesting or attractive."
            ],
            "Label_2": [
                "It says BeReal is inauthentic, but does not say why.",
                "It says BeReal is inauthentic, but does not say why.",
                "It says BeReal is inauthentic, but does not say why."
            ],
            "Label_3": [
                "It says people try to curate their posts, but does not mention it is possible to post later.",
                "It says people try to curate their posts, but does not mention it is possible to post later.",
                "It says people try to curate their posts, but does not mention it is possible to post later."
            ],
            "Label_4": [
                "It says BeReal may not remain popular.",
                "It says BeReal may not remain popular."
            ],
            "Label_5": [
                "It gives a reason why some people consider BeReal a more authentic form of social media, but not a contrasting or suprising idea.",
                "It gives a reason why some people consider BeReal a more authentic form of social media, but not a contrasting or suprising idea."
            ],
            "Label_6": [
                "It gives a consequence of the fact that some people consider BeReal a more authentic form of social media, but not a contrasting or suprising idea.",
                "It gives a consequence of the fact that some people consider BeReal a more authentic form of social media, but not a contrasting or suprising idea.",
            ],
            "Label_0": [
                "It is too general."
            ]
        },
    }
}