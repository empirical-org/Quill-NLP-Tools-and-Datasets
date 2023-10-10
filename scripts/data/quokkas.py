passage = {
    "files": {
        "because": {
            "train": "data/automl/quokkas_because_v7_train.jsonl",
            "validation": "data/automl/quokkas_because_v7_validation.jsonl",
            "test": "data/automl/quokkas_because_v7_test_automl.jsonl"
        },
        "but": {
            "train": "data/automl/quokkas_but_v3_train.jsonl",
            "validation": "data/automl/quokkas_but_v3_validation.jsonl",
            "test": "data/automl/quokkas_but_v3_test_automl.jsonl"
        },
        "so": {
            "train": "data/automl/quokkas_so_v6_train.jsonl",
            "validation": "data/automl/quokkas_so_v6_validation.jsonl",
            "test": "data/automl/quokkas_so_v6_test_automl.jsonl"
        },
    },
    "text": """Are Quokka Selfies Safe?

Quokkas (pronounced kwow-kuhs) are small, cat-sized mammals that snack on plants and hop like kangaroos. They can climb trees, dig tunnels, and live off fat stored in their tails.

But their most notable feature? Their faces. In fact, quokkas’ faces are so remarkable that the animals quickly became a social media trend—and it’s all thanks to some selfies.

The World’s Happiest Animal

What’s so remarkable about the face of the quokka? Since quokkas have naturally curved mouths that make them look like they are always smiling, they have been called the “world’s happiest animal.” Quokkas are also naturally curious, which makes them eager to approach humans. For these reasons, many tourists have enjoyed taking “selfies” with quokkas.

After people started posting their quokka selfies online in the mid 2010s, it became a trend on Instagram and Twitter. Now, the #QuokkaSelfie hashtag on Instagram has over 37,000 posts, from influencers, celebrities and everyday people alike.

Look, But Don’t Touch

Those who want to take a quokka selfie can’t do it just anywhere: their best bet is to travel to Rottnest Island, an island just off the coast of Perth, a city in Western Australia. Of the estimated 12,000 total endangered quokkas left in the world, more than 80% of them live on the island.

The island lives up to its reputation. Quokkas run around searching through trash for food and occasionally posing for pictures. Some zoologists and experts think the social media trend is fine, but they warn tourists who are seeking selfies not to let their photos negatively affect the animals and their habitat.

According to the experts, tourists should avoid getting too close to quokkas while taking selfies, as it can be dangerous: dozens of Rottnest Island visitors are bitten by quokkas each year. Another potential risk is when people feed the quokkas human food. Bread, for example, can cause quokkas infections and sometimes even death.

Quokkas Go Global

While there are potential downsides to the #QuokkaSelfie, the social media trend has had positive effects as well. Thanks in part to the thousands of photos on social media, Rottnest Island’s tourism went up 30% from 2017 to 2018. The island’s executive director, Michelle Reynolds, told People Magazine that the increase in revenue from tourism helps the island pay for research and conservation (protection) efforts for the endangered quokkas.

Additionally, Tourism Australia, the Australian government agency responsible for promoting Australian locations as appealing travel destinations, decided to take advantage of the popular social media trend by making Rottnest Island the star of its global campaign in 2019.

Despite the possible risks, Reynolds is grateful for the impact of #QuokkaSelfies. “It has really highlighted and brought to the attention of the world this most amazing mammal,” she said, “and the opportunity to really see them close up, in their natural environment.”
""",
    "plagiarism": {
        "because": "What’s so remarkable about the face of the quokka? Since quokkas have naturally curved mouths that make them look like they are always smiling, they have been called the “world’s happiest animal.” Quokkas are also naturally curious, which makes them eager to approach humans. For these reasons, many tourists have enjoyed taking “selfies” with quokkas.",
        "but": """According to the experts, tourists should avoid getting too close to quokkas, as touching them is illegal due to their endangered status. It can also be dangerous: dozens of Rottnest Island visitors are bitten by quokkas each year (fortunately, the injuries usually aren't serious).

Another potential negative impact of quokkas’ newfound social media fame is when people feed the quokkas human food. Biologist Sue Miller of the University of Western Australia explained to National Geographic, “People tend to feed them fries, bread, or fruit, and the animals become trusting of humans, which can cause problems. Animals that live farther away from [tourist activity] would probably hop away when approached."" Bread, for example, can cause quokkas harm, infections, and even death.""",
        "so": """While there are potential downsides to the #QuokkaSelfie, the social media trend has had positive effects as well. Thanks in part to the thousands of photos on social media, Rottnest Island’s tourism went up 30% from 2017 to 2018. The island’s executive director, Michelle Reynolds, told People Magazine that the increase in revenue from tourism helps the island pay for research and conservation (protection) efforts for the endangered quokkas.

Additionally, Tourism Australia, the Australian government agency responsible for promoting Australian locations as appealing travel destinations, decided to take advantage of the popular social media trend by making Rottnest Island the star of its global campaign in 2019.

After people started posting their quokka selfies online in the mid 2010s, it became a trend on Instagram and Twitter. Now, the #QuokkaSelfie hashtag on Instagram has over 37,000 posts, from influencers, celebrities and everyday people alike."""
        },
    "prompts": {
        "because": "Many tourists enjoy taking quokka selfies because",
        "but": "Many tourists enjoy taking quokka selfies, but",
        "so": "Many tourists enjoy taking quokka selfies, so"
    },
    "instructions": {
           "because": """Their response must use information from the text to explain why many tourists enjoy taking quokka selfies.

A response is optimal when it mentions at least two out of these four elements:
- quokkas have curved mouths,
- quokkas seem happy or seem to be smiling,
- quokkas are curious,
- quokkas approach humans.

A response is suboptimal:
- when it mentions only one of these elements,
- when it refers to social media, without the elements above,
- when the conjunction is misused,
- when it is not based on the text.
""",
           "but": """Their response must use information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.

A response is optimal when:
- it says that quokkas bite dozens of tourists every year,
- IT MUST INCLUDE THE WORD DOZENS IF IT IS ABOUT TOURISTS BEING BITTEN.
- IF IT DOES NOT HAVE THE WORD DOZENS IN IT AND IT IS ABOUT TOURISTS BEING BITTEN, IT IS SUBOPTIMAL.
- it says that feeding them human food can lead to infections or death.

A response is suboptimal when:
- it says there are risks, but doesn't mention specific risks,
- it says that quokkas bite, but doesn't mention the 'dozens' of victims,
- it says human food can be harmful to quokkas, but doesn't mention infections or death,
- it simply says people shouldn't get too close, without mentioning the risks,
- it simply says quokkas dislike people taking selfies,
- it says selfies can only be taken on Rottnest Island,
- it says quokkas can get infections or die, without mentioning how,
- it says quokka bites can cause infections, which is not in the text,
- it says quokkas are endangered,
- the conjunction is misused,
- it is not based on the text.
""",
           "so" : """Their response must use information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

A response is optimal when:
- it says Rottnest tourism increased 30%, or Tourism Australia made Rottnest Island the star of a global campaign,
- it says increased tourism is helping the quokkas, because it pays for research, conservation efforts, and to spread awareness,
- it says quokka selfies became a social media trend, with 37,000 posts.

A response is suboptimal when:
- it merely says quokka selfies have a positive effect, without specifying what effect exactly,
- it merely says that more tourists are visiting Rottnest Island, without mentioning the precise percentage,
- it just says Rottnest is a good place to take quokka selfies,
- it merely says quokka selfies became a social media trend, without mentioning numbers,
- it says Rottnest Island was made the star of a global campaign, but not by who,
- it misuses the conjunction,
- it is not based on the text.
"""
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.",
            "Optimal_2": "Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.",
            "Optimal_3": "Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.",
            "Label_1": "You have the right idea! Now be more specific. Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?",
            "Label_2": "You have the right idea! Now be more specific. Quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?",
            "Label_3": "You have the right idea! Now be more specific. Many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?",
            "Label_4": "You have the right idea! Now be more specific. Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?",
            "Label_0": "Try clearing your response and starting again. Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.",
            "Optimal_2": "Nice work! You used information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.",
            "Label_1": "You have the right idea! Now be more specific. Taking quokka selfies can be risky. What negative effects can quokka selfies lead to?",
            "Label_2": "You have the right idea! Now be more specific. Quokka selfies can sometimes lead to bites. How many people are bitten by quokkas each year?",
            "Label_4": "You have the right idea! Now be more specific. Human food can be harmful to quokkas. What can happen to quokkas if they eat human food?",
            "Label_5": "You have the right idea! Now be more specific. Tourists shouldn't get too close to the quokkas. What can happen if a tourist gets too close?",
            "Label_8": "Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.",
            "Label_9": "You have the right idea! Now be more specific. Quokkas can get infections. What can cause quokkas to get infected and die?",
            "Label_10": "Try clearing your response and starting again. Quokka bites could cause infections, but the text doesn't say that. Read the part again. How can tourists cause quokkas to get infected?",
            "Label_11": "Try clearing your response and starting again. Instead of talking about the fact that quokkas are endangered, focus on a contrast to the idea that tourists enjoy taking photos with them.",
            "Label_0": "Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.",
            "Optimal_2": "Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.",
            "Optimal_3": "Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.",
            "Label_1": "That's true—the selfie trend has helped Rottnest Island. Now make your response even stronger by adding specific details. What positive effects is Rottnest Island experiencing?",
            "Label_2": "That's true—more tourists are visiting Rottnest Island. Now make your response even stronger by adding a specific number from the text. How many more tourists are visiting Rottnest Island?",
            "Label_3": "Try clearing your response and starting again. So is used to explain a consequence or result. Go back to the text and look for a result of the fact that many tourists enjoy taking quokka selfies.",
            "Label_4": "Revise your response. Instead of talking about why Rottnest Island is a good place to take a quokka selfie, focus on an effect that the quokka selfie trend has had on the island.",
            "Label_5": "That's true—quokka selfies have become a social media trend. Now make your response even stronger by adding a specific number from the text. How many people does the text say have posted a quokka selfie?",
            "Label_6": "Revise your response. Instead of talking about why people want to take quokka selfies, focus on an effect that the quokka selfie trend has had on the island.",
            "Label_7": "That's true—Rottnest Island is now the star of a global campaign thanks to quokkas. Now make your response even stronger by adding specific details. Who made Rottnest Island the star of its campaign?",
            "Label_0": "Try clearing your response and starting again. What happened as a result of the fact that many tourists enjoy taking quokka selfies? Check that your response only uses information from the text."
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "quokkas have naturally curved mouths that make them look like they're smiling.",
                "the quokkas always smiling, thanks to their curved mouth.",
                "they have a curved mouth, so it makes them look like they are happy all the time.",
            ],
            "Optimal_2": [
                "quokkas are curious and approach humans.",
                "quokkas are naturally curious, which makes them want to go up to humans.",
                "they are friendly animals, and are excited to interact with humans."
            ],
            "Optimal_3": [
                "quokkas are curious and look like they're smiling.",
                "quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans.",
                "quokkas are approachable and look happy.",
                "they have smiling faces and are curious."
            ],
            "Label_1": [
                "quokkas' faces are unique since they always look like they are smiling.",
                "#quokkaselfies are cute due to the animal appearing to be smiling."
            ],
            "Label_2": [
                "the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas.",
                "they're curious little creatures."
            ],
            "Label_3": [
                "they are cute.",
                "they have faces that are so remarkable and cute."
            ],
            "Label_4": [
                "it became a trend on instagram and twitter.",
                "these good photos turned into a social media trend."
            ],
            "Label_0": [
                "getting too close to quokkas can be illegal.",
                "they are a one of a kind animal."
            ]
        },
        "but": {
            "Optimal_1": [
                "these animals are known to bite dozens of visitors each year.",
                "tourists shouldn't get too close to them because many tourists have been bitten by them; dozens of tourists are bitten by them each year.",
                "reports show that dozens of visitors are bitten by quokkas each year.",
                "there could be risks, for dozens of people are bitten by quokkas every year, and they may be infectious to human food.",
                "some of the zoologists say that to not let the selfies negatively affect the quokkas, and should avoid getting to close to them because of dozens of tourists are bitten each year by quokkas."
            ],
            "Optimal_2": [
                "many people feed the quokkas human food like bread that can lead to infections or even death.",
                "people fed them human food which can cause infections and even death.",
                "when they are fed human food it could infect or even kill them.",
                "it can also be dangerous and a potential risk when quokkas are fed human food, causing infections and sometimes death.",
                "visitors to be careful as some have been bitten and human food can give quokkas infections and even sometimes cause death."
            ],
            "Label_1": [
                "it can be dangerous sometimes.",
                "zoologists have warned to not ruin their habitat with the photos",
            ],
            "Label_2": [
                "it can be harmful to the quokkas and humans as they sometimes bite.",
            ],
            "Label_4": [
                "the animals can be dangerous and some tourists feed them human food which can be harmful.",
            ],
            "Label_5": [
                "tourists have avoid getting too close to quokkas."
            ],
            "Label_8": [
                "there is only one place where anyone can take a picture with quokka and it is Rottnest Island just off the coast of Perth in Western Australia."
            ],
            "Label_9": [
                "Quokkas are particularly vulnerable to infection and death."
            ],
            "Label_10": [
                "humans can be bitten and then get an infection."
            ],
            "Label_11": [
                "they are an endangered species with only about 12,000 left."
            ],
            "Label_0": [
                "they are also curious so they come up to humans."
            ]
        },
        "so": {
            "Optimal_1": [
                "the Island tourism increased 30% from 2017 to 2018.",
                "the Australian government decided to make Rottnest Island the main attraction of its global campaign in 2019.",
                "in 2019 Tourism Australia decided to make island the head of its global campaign.",
                "so Rottnest island's tourism increased 30%."

            ],
            "Optimal_2": [
                "an increase in tourism helps fund protection for quokkas."
                "because of the quokkas the tourism has gone up 30%, and that has helped the awareness of the quokkas."
                "they have increased the tourism in Rottnest Island which pays for research and protection."
            ],
            "Optimal_3": [
                "#Quokka Selfie has become an Instagram trend with over 37,000 posts.",
                "It promotes tourism, it has 37,000 posts on social media.",
                "people started posting their quokka pictures online in 2010’s with over 37,000 posts."
            ],
            "Label_1": [
                "It has a favorable influence on the quokkas, which in turn has a positive impact on the animals.",
                "the reputation of Rottnest island and quokkas increased."
            ],
            "Label_2": [
                "Rottnest Island's tourism went up significantly in just over a year.",
                "it attracted so many people to visit Australia."
            ],
            "Label_3": [
                "they have to be careful doing taking selfies as quokkas can be dangerous and bite some tourists"
            ],
            "Label_4": [
                "they travel to Rottnest Island in Western Australia just to go take the selfies."
            ],
            "Label_5": [
                "It has become a big social media trend."
            ],
            "Label_6": [
                "they can post it on social media so other people can see the quokkas."
            ],
            "Label_7": [
                "They made it the center of a worldwide campaign in 2019."
            ],
            "Label_0": [
                "it's a very cool and fun thing to do but be aware when near to them."
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_1": [
                "This response mentions curved mouths and happy/smiling.",
                "This response mentions curved mouths and happy/smiling.",
                "This response mentions curved mouths and happy/smiling.",
            ],
            "Optimal_2": [
                "This response says that quokkas like to approach humans.",
                "This response says that quokkas like to approach humans.",
                "This response says that quokkas like to approach humans."
            ],
            "Optimal_3": [
                "There are four valid elements: curved mouths, smiling/happy, curious, and approachable. This response mentions two of those elements.",
                "There are four valid elements: curved mouths, smiling/happy, curious, and approachable. This response mentions two of those elements.",
                "There are four valid elements: curved mouths, smiling/happy, curious, and approachable. This response mentions two of those elements.",
                "There are four valid elements: curved mouths, smiling/happy, curious, and approachable. This response mentions two of those elements.",
            ],
            "Label_1": [
                "This response says that quokkas look like they're happy or smiling, but does not mention their curved mouths.",
                "This response says that quokkas look like they're happy or smiling, but does not mention their curved mouths."
            ],
            "Label_2": [
                "This response says that quokkas are curious, but does not mention they approach humans.",
                "This response says that quokkas are curious, but does not mention they approach humans.",
            ],
            "Label_3": [
                "This response mentions how quokkas look, but does not mention smiling, posing for photos, or curiosity.",
                "This response mentions how quokkas look, but does not mention smiling, posing for photos, or curiosity.",
            ],
            "Label_4": [
                "This response mentions social media, but no other elements from the text.",
                "This response mentions social media, but no other elements from the text.",
            ],
            "Label_0": [
                "This response does not give a reason why many tourists enjoy taking quokka selfies.",
                "This response does not give a reason why many tourists enjoy taking quokka selfies.",
            ]
        },
        "but": {
            "Optimal_1": [
                "This response says that quokkas bite dozens of tourists every year.",
                "This response says that quokkas bite dozens of tourists every year.",
                "This response says that quokkas bite dozens of tourists every year.",
                "This response says that quokkas bite dozens of tourists every year.",
                "This response says that quokkas bite dozens of tourists every year.",
            ],
            "Optimal_2": [
                "This response says that feeding quokkas human food can lead to infections or death.",
                "This response says that feeding quokkas human food can lead to infections or death.",
                "This response says that feeding quokkas human food can lead to infections or death.",
                "This response says that feeding quokkas human food can lead to infections or death.",
                "This response says that feeding quokkas human food can lead to infections or death.",
            ],
            "Label_1": [
                "This response says that taking quokka selfies is risky, but does not mention any specific risks.",
                "This response says that taking quokka selfies is risky, but does not mention any specific risks.",
            ],
            "Label_2": [
                "This response says that quokkas can bite, but does not contain the word 'dozens'.",
            ],
            "Label_4": [
                "This response says that human food can be harmful to quokkas, but does not mention infections or death."
            ],
            "Label_5": [
                "This response says people shouldn'get get too close to quokkas, but does not mention the risks involved."
            ],
            "Label_8": [
                "This response says that quokka selfies can only be taken on Rottnest Island."
            ],
            "Label_9": [
                "This response says that quokkas can get infections or die, without mentioning how."
            ],
            "Label_10": [
                "This response says that quokka bites can cause infections, which is not in the text."
            ],
            "Label_11": [
                "This response says that quokkas are endangered."
            ],
            "Label_0": [
                "This response does not give a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies."
            ]
        },
    }
}