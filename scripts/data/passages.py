passages = {
    "dresscode": {
        "passage": """
        The night before the first day of school, Nina excitedly chooses her outfit. She wants to wear jeans, a fuzzy orange sweater, and her favorite accessory: a brown hat with sequins. According to her school, though, the hat is forbidden. In fact, she could get detention for wearing it.

        This story, while fictional, was all too familiar to the students of Manchester School District in New Hampshire. They decided that it was time for a change—so they rewrote the district’s dress code.

        **Why Rewrite the Dress Code?**

        Manchester students wanted a less strict dress code for many reasons. They felt that it singled out female students by banning clothing items typically associated with women, like spaghetti straps (very thin shoulder straps) and tube tops.

        Some also thought it singled out Black students. Some Black students wear durags, hats, bonnets, and hoodies to protect their hair or to express Black cultural pride. “It is a part of our culture to wear headwraps and it helps us take care of our natural hair, which is…kinky and curly and not the same as most of our teachers,” one student at a New York City high school explained to Chalkbeat, an education news organization. At Manchester schools, this was not possible: hats, hoodies, bonnets, and durags were banned.

        Students who violated the dress code would face a range of punishments, including detention or suspension. According to a 2018 National Women's Law Center study, these dress code punishments can cause students to fall behind academically because they could lose out on crucial class time.

        **Student Advocacy Gets Results**

        Kellan Barbee, who serves as one of four student representatives to the Manchester school board in New Hampshire, addressed the concerns of his peers by proposing a rewritten school dress code in 2021.

        It states that enforcement will not discriminate on the basis of race or gender. It also allows several items that were previously not allowed, including spaghetti straps, tube tops, ripped jeans, durags, bonnets, and hats. The policy also removes the punishment that causes students to lose instructional time.

        **The Case For Manchester's Original Dress Code**

        The new policy was approved in a majority vote. However, one Manchester school board member, Gary Hamer, voted against the new policy. He explained, “I just think we’re asking ourselves for more challenges…I see some things in here that are too permissive from my perspective.”

        Despite some student opposition, schools advocate for strict dress codes for a variety of reasons. They say that having a stricter dress code can reduce in-class distractions and reduce pressures that students might feel related to socioeconomic status. Many schools feel that if fewer styles of clothing are allowed in school, students will feel less pressure to keep up with expensive fashion trends.

        **A Step Forward**

        Manchester's rewritten dress code got final approval from the school board in January 2022. It was the first policy in the district to be authored by a student.

        School board member Nicole Leapley was happy about the changes. “I just know [the original policy] is not working for all of our students,” she told the New Hampshire Union Leader, “and this is a step forward.”
        """,
        "plagiarism": {
            "because": """Manchester students wanted a less strict dress code for many reasons. They felt that it singled out female students by banning clothing items typically associated with women, like spaghetti straps (very thin shoulder straps) and tube tops. Some also thought it singled out Black students. Some Black students wear durags, hats, bonnets, and hoodies to protect their hair or to express Black cultural pride. “It is a part of our culture to wear headwraps and it helps us take care of our natural hair, which is…kinky and curly and not the same as most of our teachers,” one student at a New York City high school explained to Chalkbeat, an education news organization. At Manchester schools, this was not possible: hats, hoodies, bonnets, and durags were banned.""",
            "but": """The new policy was approved in a majority vote. However, one Manchester school board member, Gary Hamer, voted against the new policy. He explained, “I just think we’re asking ourselves for more challenges…I see some things in here that are too permissive from my perspective.” Despite some student opposition, schools advocate for strict dress codes for a variety of reasons. They say that having a stricter dress code can reduce in-class distractions and reduce pressures that students might feel related to socioeconomic status. Many schools feel that if fewer styles of clothing are allowed in school, students will feel less pressure to keep up with expensive fashion trends.""",
            "so": """Kellan Barbee, who serves as one of four student representatives to the Manchester school board in New Hampshire, addressed the concerns of his peers by proposing a rewritten school dress code in 2021. It states that enforcement will not discriminate on the basis of race or gender. It also allows several items that were previously not allowed, including spaghetti straps, tube tops, ripped jeans, durags, bonnets, and hats. The policy also removes the punishment that causes students to lose instructional time."""
        },
        "prompts": {
            "because": "Some Manchester students wanted to change their district's dress code because",
            "but": "Some Manchester students wanted to change their district's dress code, but",
            "so": "Some Manchester students wanted to change their district's dress code, so"
        },
        "label_info": {
           "because": """Their response must say why Manchester students wanted to change the dress code.
                        A response is optimal when it specifies the dress code could cause students to fall behind, or
                        when it says it singled out women or black students.
                        A response is suboptimal in the following cases:
                        - when it does not mention what students are singled out,
                        - when it simply says that the dress code was too strict or students could get detention,
                        - when the conjunction is misused,
                        - when it says black students wear durags to express cultural pride or the dress code is freedom of expression.""",
           "but": """Their response must show a contrasting or surprising idea about the changes to Manchester's dress code.
                        A response is optimal when:
                        - it says one school board member voted against changing the dress code,
                        - it says strict dress codes prevent distractions,
                        - it says strict dress codes help socioeconomic pressures.
                        It is suboptimal when:
                        - it says students who violate the code will be punished,
                        - it says other students support the code,
                        - it says schools advocate for the dress code,
                        - it misuses the conjunction,
                        - it is not based on the input text.""",
           "so" : """Their response must show a result of students wanting to change their district's dress code.
                        A response is optimal when:
                        - it says Kellan Barbee rewrote the dress code,
                        - it says punishment was removed that causes students to lose instructional time,
                        - it says enforcement will not be based on gender or race,
                        - it says new items will be allowed under the dress code.
                        A response is suboptimal when:
                        - it simply says students rewrote the dress code, without details,
                        - it simply says the policy was approved, without details,
                        - it says students opposed the dress code,
                        - it misuses the conjunction,
                        - it is not based on the input text."""
        },
        "files" : {
            "because": {
                "train": "data/automl/dress_codes_because_v6_train.jsonl",
                "test": "data/automl/dress_codes_because_v6_test_automl.jsonl"
            },
            "but": {
                "train": "data/automl/dress_codes_but_v5_train.jsonl",
                "test": "data/automl/dress_codes_but_v5_test_automl.jsonl"
            },
            "so": {
                "train": "data/automl/dress_codes_so_v7_train.jsonl",
                "test": "data/automl/dress_codes_so_v7_test_automl.jsonl"
            }
        }
    },
    "quokkas": {
        "passage": """Are Quokka Selfies Safe?

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
        "example_responses": {
            "because": {
                "Optimal": {
                    "Optimal_1": [
                        "Many tourists enjoy taking quokka selfies because quokkas have naturally curved mouths that make them look like they're smiling.",
                        "Many tourists enjoy taking quokka selfies because the quokkas always smiling, thanks to their curved mouth.",
                        "Many tourists enjoy taking quokka selfies because they have a curved mouth, so it makes them look like they are happy all the time.",
                    ],
                    "Optimal_2": [
                        "Many tourists enjoy taking quokka selfies because quokkas are curious and approach humans.",
                        "Many tourists enjoy taking quokka selfies because quokkas are naturally curious, which makes them want to go up to humans.",
                        "Many tourists enjoy taking quokka selfies because they are friendly animals, and are excited to interact with humans."
                    ],
                    "Optimal_3": [
                        "Many tourists enjoy taking quokka selfies because quokkas are curious and look like they're smiling.",
                        "Many tourists enjoy taking quokka selfies because quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans.",
                        "Many tourists enjoy taking quokka selfies because quokkas are approachable and look happy.",
                        "Many tourists enjoy taking quokka selfies because they have smiling faces and are curious."
                    ]
                },
                "Suboptimal": {
                    "Label_1": [
                        "Many tourists enjoy taking quokka selfies because quokkas' faces are unique since they always look like they are smiling.",
                        "Many tourists enjoy taking quokka selfies because #quokkaselfies are cute due to the animal appearing to be smiling."
                    ],
                    "Label_2": [
                        "Many tourists enjoy taking quokka selfies because the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas.",
                        "Many tourists enjoy taking quokka selfies because they're curious little creatures."
                    ],
                    "Label_3": [
                        "Many tourists enjoy taking quokka selfies because they are cute.",
                        "Many tourists enjoy taking quokka selfies because they have faces that are so remarkable and cute."
                    ],
                    "Label_4": [
                        "Many tourists enjoy taking quokka selfies because it became a trend on instagram and twitter.",
                        "Many tourists enjoy taking quokka selfies because these good photos turned into a social media trend."
                    ],
                    "Label_0": [
                        "Many tourists enjoy taking quokka selfies because getting too close to quokkas can be illegal.",
                        "Many tourists enjoy taking quokka selfies because they are a one of a kind animal."
                    ]
                }
            },
            "but": {
                "Optimal": {
                    "Optimal_1": [
                        "Many tourists enjoy taking quokka selfies, but these animals are known to bite dozens of visitors each year.",
                        "Many tourists enjoy taking quokka selfies, but tourists shouldn't get too close to them because many tourists have been bitten by them; dozens of tourists are bitten by them each year.",
                        "Many tourists enjoy taking quokka selfies, but reports show that dozens of visitors are bitten by quokkas each year.",
                        "Many tourists enjoy taking quokka selfies, but there could be risks, for dozens of people are bitten by quokkas every year, and they may be infectious to human food.",
                        "Many tourists enjoy taking quokka selfies, but some of the zoologists say that to not let the selfies negatively affect the quokkas, and should avoid getting to close to them because of dozens of tourists are bitten each year by quokkas."
                    ],
                    "Optimal_2": [
                        "Many tourists enjoy taking quokka selfies, but many people feed the quokkas human food like bread that can lead to infections or even death.",
                        "Many tourists enjoy taking quokka selfies, but people fed them human food which can cause infections and even death.",
                        "Many tourists enjoy taking quokka selfies, but when they are fed human food it could infect or even kill them.",
                        "Many tourists enjoy taking quokka selfies, but it can also be dangerous and a potential risk when quokkas are fed human food, causing infections and sometimes death.",
                        "Many tourists enjoy taking quokka selfies, but visitors to be careful as some have been bitten and human food can give quokkas infections and even sometimes cause death."
                    ],
                },
                "Suboptimal": {
                    "Label_1": [
                        "Many tourists enjoy taking quokka selfies, but it can be dangerous sometimes.",
                        "Many tourists enjoy taking quokka selfies, but zoologists have warned to not ruin their habitat with the photos",
                    ],
                    "Label_2": [
                        "Many tourists enjoy taking quokka selfies, but it can be harmful to the quokkas and humans as they sometimes bite.",
                    ],
                    "Label_4": [
                        "Many tourists enjoy taking quokka selfies, but the animals can be dangerous and some tourists feed them human food which can be harmful.",
                    ],
                    "Label_5": [
                        "Many tourists enjoy taking quokka selfies, but tourists have avoid getting too close to quokkas."
                    ],
                    "Label_8": [
                        "Many tourists enjoy taking quokka selfies, but there is only one place where anyone can take a picture with quokka and it is Rottnest Island just off the coast of Perth in Western Australia."
                    ],
                    "Label_9": [
                        "Many tourists enjoy taking quokka selfies, but Quokkas are particularly vulnerable to infection and death."
                    ],
                    "Label_10": [
                        "Many tourists enjoy taking quokka selfies, but humans can be bitten and then get an infection."
                    ],
                    "Label_11": [
                        "Many tourists enjoy taking quokka selfies, but they are an endangered species with only about 12,000 left."
                    ],
                    "Label_0": [
                        "Many tourists enjoy taking quokka selfies, but they are also curious so they come up to humans."
                    ]
                }

            },
            "so": {
                "Optimal": {
                    "Optimal_1": [
                        "Many tourists enjoy taking quokka selfie, so the Island tourism increased 30% from 2017 to 2018.",
                        "Many tourists enjoy taking quokka selfie, so the Australian government decided to make Rottnest Island the main attraction of its global campaign in 2019.",
                        "Many tourists enjoy taking quokka selfie, so in 2019 Tourism Australia decided to make island the head of its global campaign.",
                        "Many tourists enjoy taking quokka selfie, so Rottnest island's tourism increased 30%."

                    ],
                    "Optimal_2": [
                        "Many tourists enjoy taking quokka selfie, so an increase in tourism helps fund protection for quokkas."
                        "Many tourists enjoy taking quokka selfie, so because of the quokkas the tourism has gone up 30%, and that has helped the awareness of the quokkas."
                        "Many tourists enjoy taking quokka selfie, so they have increased the tourism in Rottnest Island which pays for research and protection."
                    ],
                    "Optimal_3": [
                        "Many tourists enjoy taking quokka selfie, so #Quokka Selfie has become an Instagram trend with over 37,000 posts.",
                        "Many tourists enjoy taking quokka selfie, so It promotes tourism, it has 37,000 posts on social media.",
                        "Many tourists enjoy taking quokka selfie, so people started posting their quokka pictures online in 2010’s with over 37,000 posts."
                    ]
                },
                "Suboptimal": {
                    "Label_1": [
                        "Many tourists enjoy taking quokka selfie, so It has a favorable influence on the quokkas, which in turn has a positive impact on the animals.",
                        "Many tourists enjoy taking quokka selfie, so the reputation of Rottnest island and quokkas increased."
                    ],
                    "Label_2": [
                        "Many tourists enjoy taking quokka selfie, so Rottnest Island's tourism went up significantly in just over a year.",
                        "Many tourists enjoy taking quokka selfie, so it attracted so many people to visit Australia."
                    ],
                    "Label_3": [
                        "Many tourists enjoy taking quokka selfie, so they have to be careful doing taking selfies as quokkas can be dangerous and bite some tourists"
                    ],
                    "Label_4": [
                        "Many tourists enjoy taking quokka selfie, so they travel to Rottnest Island in Western Australia just to go take the selfies."
                    ],
                    "Label_5": [
                        "Many tourists enjoy taking quokka selfie, so It has become a big social media trend."
                    ],
                    "Label_6": [
                        "Many tourists enjoy taking quokka selfie, so they can post it on social media so other people can see the quokkas."
                    ],
                    "Label_7": [
                        "Many tourists enjoy taking quokka selfie, so They made it the center of a worldwide campaign in 2019."
                    ],
                    "Label_0": [
                        "Many tourists enjoy taking quokka selfie, so it's a very cool and fun thing to do but be aware when near to them."
                    ]
                }

            }
        },
        "label_info": {
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
        "suboptimal_correction": {
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

For example:
- "Many tourists enjoy taking quokka selfies because quokkas' faces are unique since they always look like they are smiling" is Suboptimal because it refers only to smiling. A second element should be added.
- "Many tourists enjoy taking quokka selfies because it became a trend on instagram and twitter" is Suboptimal because it refers only to social media, but does not include any of the four elements above.
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
        "label_info_detailed": {
           "because": """Their response must use information from the text to explain why many tourists enjoy taking quokka selfies.

You now have to assign one label to the response, based on its content. Here are the possible labels:
- Optimal_1: quokkas have curved mouths and look happy or look like they're smiling
- Optimal_2: quokkas are curious and approach humans
- Optimal_3: quokkas are curious and look like they're smiling
- Label_1: the response says that quokkas look happy or look like they're smiling, but doesn't mention their curved mouths
- Label_2: the response says that quokkas are curious, but doesn't mention they like to approach humans
- Label_3: the response says that quokkas are cute, but does not mention why
- Label_4: the response says that quokka selfies are a social media trend
- Label_0: the response is not based on the text, or uses the conjunction incorrectly

Here are some examples. Many tourists enjoy taking quokka selfies because:
- quokkas have naturally curved mouths that make them look like they're smiling: Optimal_1 because it mentions curved mouths and the fact that quokkas look like they're smiling
- the quokkas always smiling, thanks to their curved mouth: Optimal_1 because it mentions curved mouths and the fact that quokkas look like they're smiling
- they have a curved mouth, so it makes them look like they are happy all the time: Optimal_1 because it mentions curved mouths and smiling
- quokkas are curious and approach humans: Optimal_2 because it says that quokkas are curious and approach humans
- quokkas are naturally curious, which makes them want to go up to humans: Optimal_2 because it says that quokkas are curious and approach humans
- they are friendly animals, and are excited to interact with humans: Optimal_2 because it says that quokkas are curious and approach humans
- quokkas are curious and look like they're smiling: Optimal_3 because it says that quokkas are curious and seem to be smiling
- quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans: Optimal_3 because it says that quokkas are curious and seem to be smiling
- quokkas are approachable and look happy: Optimal_3 because it says that quokkas are curious and seem to be smiling
- they have smiling faces and are curious: Optimal_3 because it says that quokkas are curious and seem to be smiling
- quokkas' faces are unique since they always look like they are smiling: Label_1 because it says that quokkas seem happy or look like they're smiling, but doesn't explicitly mention their curved mouths
- #quokkaselfies are cute due to the animal appearing to be smiling: Label_1 because it says that quokkas seem happy or look like they're smiling, but doesn't explicitly mention their curved mouths
- the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas: Label_2 because it says that quokkas are curious, but doesn't mention they like to approach humans
- they're curious little creatures: Label_2 because it says that quokkas are curious, but doesn't mention they like to approach humans
- they are cute: Label_3 because it says that quokkas are cute, but does not mention why
- they have faces that are so remarkable and cute: Label_3 because it says that quokkas are cute, but does not mention why
- it became a trend on instagram and twitter: Label_4 because it says that quokka selfies are a social media trend
- these good photos turned into a social media trend: Label_4 because it says that quokka selfies are a social media trend
- getting too close to quokkas can be illegal: Label_0 because it is not based on the text, or uses the conjunction incorrectly
- they are a one of a kind animal: Label_0 because it is not based on the text, or uses the conjunction incorrectly
""",
           "but": """Their response must use information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.

You now have to assign one label to the response, based on its content. You can ignore grammatical errors. Here are the possible labels:
- Optimal_1: the response says that quokkas bite *dozens* of tourists every year. The word 'dozen' or 'dozens' MUST be used. If a synonym like 'many' is used, the response should get Label_2.
- Optimal_2: the response says that quokkas can get infected or die when they eat human food. For this label, the word 'dozens' is not required.
- Label_1: the response indicates there are risks involved, but no reference to food or biting
- Label_2: the response says quokkas bite, but does not use the word 'dozens'
- Label_4: the response mentions human food, but does not refer to infections or death
- Label_5: the response says people shouldn't get too close, but does not say why
- Label_8: the response says quokka selfies are only possible on Rottnest Island
- Label_9: the response mentions infections and death, but not human food
- Label_10: the response says quokkas cause infections
- Label_11: the response says quokkas are endangered
_ Label_0: the response is not based on the text or misuses the conjunction

Here are some examples. Many tourists enjoy taking quokka selfies, but:
- these animals are known to bite dozens of visitors each year: Optimal_1 because it says quokkas bite dozens of tourists every year.
- tourists shouldn't get too close to them because many tourists have been bitten by them; dozens of tourists are bitten by them each year: Optimal_1 because it says quokkas bite dozens of tourists every year
- reports show that dozens of visitors are bitten by quokkas each year: Optimal_1 because it says quokkas bite dozens of tourists every year
- there could be risks, for dozens of people are bitten by quokkas every year, and they may be infectious to human food: Optimal_1 because it says quokkas bite dozens of tourists every year
- some of the zoologists say that to not let the selfies negatively affect the quokkas, and should avoid getting to close to them because of dozens of tourists are bitten each year by quokkas: Optimal_1 because it says quokkas bite dozens of tourists every year
- many people feed the quokkas human food like bread that can lead to infections or even death: Optimal_2 because it says quokkas can get infected or die when they eat human food
- people fed them human food which can cause infections and even death: Optimal_2 because it says quokkas can get infected or die when they eat human food
- when they are fed human food it could infect or even kill them: Optimal_2 because it says quokkas can get infected or die when they eat human food
- it can also be dangerous and a potential risk when quokkas are fed human food, causing infections and sometimes death: Optimal_2 because it says quokkas can get infected or die when they eat human food
- visitors to be careful as some have been bitten and human food can give quokkas infections and even sometimes cause death: Optimal_2 because it says quokkas can get infected or die when they eat human food
- it can be dangerous sometimes: Label_1 because it says there are risks involved, but does not mention food or biting
- zoologists have warned to not ruin their habitat with the photos: Label_1 because it says there are risks involved, but does not mention food or biting
- it can be harmful to the quokkas and humans as they sometimes bite: Label_2 because it says that quokkas bite, but does not use the word 'dozens'.
- the animals can be dangerous and some tourists feed them human food which can be harmful: Label_4 because it mentions human food, but does not refer to infections or death
- tourists have avoid getting too close to quokkas: Label_5 because it says people shouldn't get too close, but does not say why
- there is only one place where anyone can take a picture with quokka and it is Rottnest Island just off the coast of Perth in Western Australia: Label_8 because it says quokka selfies are only possible on Rottnest Island
- Quokkas are particularly vulnerable to infection and death: Label_9 because it mentions infections and death, but not human food
- humans can be bitten and then get an infection: Label_10 because it says that quokkas cause infections
- they are an endangered species with only about 12,000 left: Label_11 because it says that quokkas are endangered
- they are also curious so they come up to humans: Label_0 because it is not based on the text or misuses the conjunction
""",
           "so" : """Their response must use information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

You now have to assign one label to the response, based on its content. You can ignore grammatical errors. Here are the possible labels:
- Optimal_1: Rottnest tourism increased 30% or Tourism Australia made Rottnest Island the star of a global campaign
- Optimal_2: Increased tourism helps the quokkas, as it pays for research and conservation efforts, and spreads awareness
- Optimal_3: Quokka selfies became a social media trend with 37,000 posts
- Label_1: The response says the quokka selfie is having a positive effect on quokkas and the island, but does not say why
- Label_2: The response says more tourists are visiting Rottnest Island, but does not mention the 30%
- Label_3: The response misuses the conjunction
- Label_4: Rottnest is a good place to take a good quokka selfie
- Label_5: The response says quokka selfies became a social media trend, but does not mention the number of posts
- Label_6: The response says that as a result, quokkas can be social media famous
- Label_7: The response says quokka selfies became the star of a global campaign, but does not refer to the Australian government
- Label_8: The response is not based on the text.

Here are some examples. Many tourists enjoy taking quokka selfies, so:
- the Island tourism increased 30% from 2017 to 2018: Optimal_1 because it says Rottnest tourism increased 30%
- so the Australian government decided to make Rottnest Island the main attraction of its global campaign in 2019: Optimal_1 because it says Tourism Australia made Rottnest Island the star of a global campaign
- in 2019 Tourism Australia decided to make island the head of its global campaign: Optimal_1 because it says Tourism Australia made Rottnest Island the star of a global campaign
- Rottnest island's tourism increased 30%: Optimal_1 because it says Rottnest tourism increased 30%
- an increase in tourism helps fund protection for quokkas: Optimal_2 because it says increased tourism helps the quokkas, and refers to conservation efforts
- because of the quokkas the tourism has gone up 30%, and that has helped the awareness of the quokkas: Optimal_2 because it says increased tourism helps the quokkas, and refers to awareness
- they have increased the tourism in Rottnest Island which pays for research and protection: Optimal_2 because it says increased tourism helps the quokkas, and refers to research and protection
- #Quokka Selfie has become an Instagram trend with over 37,000 posts: Optimal_3 because it says quokka selfies became a social media trend with 37,000 posts
- It promotes tourism, it has 37,000 posts on social media: Optimal_3 because it says quokka selfies became a social media trend with 37,000 posts
- people started posting their quokka pictures online in 2010’s with over 37,000 posts: Optimal_3 because it says quokka selfies became a social media trend with 37,000 posts
- It has a favorable influence on the quokkas, which in turn has a positive impact on the animals: Label_1 because it says the quokka selfie is having a positive effect on quokkas and the island, but does not say why
- the reputation of Rottnest island and quokkas increased: Label_1 because it says the quokka selfie is having a positive effect on quokkas and the island, but does not say why
- Rottnest Island's tourism went up significantly in just over a year: Label_2 because it says more tourists are visiting, but does not mention the 30%
- it attracted so many people to visit Australia: Label_2 because it says more tourists are visiting, but does not mention the 30%
- they have to be careful doing taking selfies as quokkas can be dangerous and bite some tourists: Label_3 because it misuses the conjunction: should be 'but' instead of 'so'
- they travel to Rottnest Island in Western Australia just to go take the selfies: Label_4 because it says Rottnest is a good place to take a good quokka selfie
- It has become a big social media trend: Label_5 because it says quokka selfies became a social media trend, but does not mention the number of posts
- they can post it on social media so other people can see the quokkas: Label_6 because it says that as a result, quokkas can be social media famous
- They made it the center of a worldwide campaign in 2019: Label_7 because it says quokka selfies became the star of a global campaign, but does not refer to the Australian government
- it's a very cool and fun thing to do but be aware when near to them: Label_8 because the response is not based on the text.
"""
        },
        "feedback_list": {
            "because": [
                {
                    "Response": "quokkas have naturally curved mouths that make them look like they're smiling.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "the quokkas always smiling, thanks to their curved mouth.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "they have a curved mouth, so it makes them look like they are happy all the time.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas are curious and approach humans.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas are naturally curious, which makes them want to go up to humans.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "they are friendly animals, and are excited to interact with humans.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas are curious and look like they're smiling.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas are approachable and look happy.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "they have smiling faces and are curious.",
                    "Label": "Nice work!",
                    "Feedback": "You used information from the text to explain why many tourists enjoy taking quokka selfies."
                },
                {
                    "Response": "quokkas' faces are unique since they always look like they are smiling.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?"
                },
                {
                    "Response": "#quokkaselfies are cute due to the animal appearing to be smiling.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?"
                },
                {
                    "Response": "the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?"
                },
                {
                    "Response": "they're curious little creatures.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?"
                },
                {
                    "Response": "they are cute.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?"
                },
                {
                    "Response": "they have faces that are so remarkable and cute.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?"
                },
                {
                    "Response": "it became a trend on instagram and twitter.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?"
                },
                {
                    "Response": "these good photos turned into a social media trend.",
                    "Label": "You have the right idea! Now be more specific.",
                    "Feedback": "Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?"
                },
                {
                    "Response": "getting too close to quokkas can be illegal.",
                    "Label": "Try clearing your response and starting again.",
                    "Feedback": "Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text."
                },
                {
                    "Response": "they are a one of a kind animal.",
                    "Label": "Try clearing your response and starting again.",
                    "Feedback": "Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text."
                },
            ]
        },
        "feedback": {
           "because": """Their response must use information from the text to explain why many tourists enjoy taking quokka selfies.

Here are some general rules for your feedback:
- Make sure your response is *understandable and engaging for a fifth grade student*. Use simple language, clear explanations, and avoid complex vocabulary or concepts.
- Try to keep you feedback short and friendly.
- Focus on one issue only. You are not an annoying bot. It is annoying when a student gets an additional piece of feedback. Only tell the student one thing. When you are telling two things, you are being annoying.
- Do NOT give feedback about conciseness.
- Do NOT correct grammar and spelling errors.
- Do not say "great job", but "nice work".

Here are some example responses and their desired feedback:

Response: quokkas have naturally curved mouths that make them look like they're smiling.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: the quokkas always smiling, thanks to their curved mouth.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they have a curved mouth, so it makes them look like they are happy all the time.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are curious and approach humans.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are naturally curious, which makes them want to go up to humans.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they are friendly animals, and are excited to interact with humans.
Feedback:  Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are curious and look like they're smiling.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Reponse: quokkas are approachable and look happy.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they have smiling faces and are curious.
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas' faces are unique since they always look like they are smiling.
Feedback:  You have the right idea! Now be more specific. Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?

Response: #quokkaselfies are cute due to the animal appearing to be smiling.
Feedback: You have the right idea! Now be more specific. Quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?

Response: the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas.
Feedback: You have the right idea! Now be more specific. Quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?

Response: they're curious little creatures.
Feedback: You have the right idea! Now be more specific. Quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?

Response: they are cute.
Feedback: You have the right idea! Now be more specific. Many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?

Response: they have faces that are so remarkable and cute.
Feedback: You have the right idea! Now be more specific. Many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?

Response: it became a trend on instagram and twitter.
Feedback: You have the right idea! Now be more specific. Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?

Response: these good photos turned into a social media trend.
Feedback: You have the right idea! Now be more specific. Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?

Response: getting too close to quokkas can be illegal.
Feedback: Try clearing your response and starting again. Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.

Response: they are a one of a kind animal.
Feedback: Try clearing your response and starting again. Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.
""",
           "but": """Their response must use information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.

Your feedback should start with 'Nice work!' when:
- the response says that quokkas bite dozens of tourists every year,
- THE RESPONSE MUST INCLUDE THE WORD DOZENS IF IT IS ABOUT TOURISTS BEING BITTEN.
- IF IT DOES NOT HAVE THE WORD DOZENS IN IT AND IT IS ABOUT TOURISTS BEING BITTEN, IT IS SUBOPTIMAL.
- the response says that feeding them human food can lead to infections or death.

Your feedback should start with 'You have the right idea! Now be more specific' when the response:
- says there are risks, but doesn't mention specific risks,
- says that quokkas bite, but doesn't mention the 'dozens' of victims,
- says human food can be harmful to quokkas, but doesn't mention infections or death,
- simply says people shouldn't get too close, without mentioning the risks,
- simply says quokkas dislike people taking selfies,
- says selfies can only be taken on Rottnest Island,
- says quokkas can get infections or die, without mentioning how,
- says quokka bites can cause infections, which is not in the text,
- says quokkas are endangered.

Your feedback should start with 'Try clearing your response and starting again' in all other cases.

Here are some general rules for your feedback:
- Make sure your response is *understandable and engaging for a fifth grade student*. Use simple language, clear explanations, and avoid complex vocabulary or concepts.
- Try to keep you feedback short and friendly.
- Focus on one issue only. You are not an annoying bot. It is annoying when a student gets an additional piece of feedback. Only tell the student one thing. When you are telling two things, you are being annoying.
- Do NOT give feedback about conciseness.
- Do NOT correct grammar and spelling errors.
- Do not say "great job", but "nice work".

Here are some example responses and their desired feedback:

Response: these animals are known to bite dozens of visitors each year.
Feedback: Nice work! You used information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: tourists shouldn't get too close to them because many tourists have been bitten by them; dozens of tourists are bitten by them each year.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: reports show that dozens of visitors are bitten by quokkas each year.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: there could be risks, for dozens of people are bitten by quokkas every year, and they may be infectious to human food.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: some of the zoologists say that to not let the selfies negatively affect the quokkas, and should avoid getting to close to them because of dozens of tourists are bitten each year by quokkas.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: many people feed the quokkas human food like bread that can lead to infections or even death.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: people fed them human food which can cause infections and even death.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: when they are fed human food it could infect or even kill them.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: it can also be dangerous and a potential risk when quokkas are fed human food, causing infections and sometimes death.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: visitors to be careful as some have been bitten and human food can give quokkas infections and even sometimes cause death.
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: it can be dangerous sometimes.
Feedback: You have the right idea! Now be more specific. Taking quokka selfies can be risky. What negative effects can quokka selfies lead to?

Response: zoologists have warned to not ruin their habitat with the photos.
Feedback: You have the right idea! Now be more specific. Taking quokka selfies can be risky. What negative effects can quokka selfies lead to?

Response: it can be harmful to the quokkas and humans as they sometimes bite.
Feedback: You have the right idea! Now be more specific. Quokka selfies can sometimes lead to bites. How many people are bitten by quokkas each year?

Response: the animals can be dangerous and some tourists feed them human food which can be harmful.
Feedback: You have the right idea! Now be more specific. Human food can be harmful to quokkas. What can happen to quokkas if they eat human food?

Response: Quokkas are particularly vulnerable to infection and death.
Feedback: You have the right idea! Now be more specific. Quokkas can get infections. What can cause quokkas to get infected and die?

Response: tourists have avoid getting too close to quokkas.
Feedback: You have the right idea! Now be more specific. Tourists shouldn't get too close to the quokkas. What can happen if a tourist gets too close?

Response: there is only one place where anyone can take a picture with quokka and it is Rottnest Island just off the coast of Perth in Western Australia.
Feedback: Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.

Response: humans can be bitten and then get an infection.
Feedback: Try clearing your response and starting again. Quokka bites could cause infections, but the text doesn't say that. Read the part again. How can tourists cause quokkas to get infected?

Response: they are an endangered species with only about 12,000 left.
Feedback: Try clearing your response and starting again. Instead of talking about the fact that quokkas are endangered, focus on a contrast to the idea that tourists enjoy taking photos with them.

Response: they are also curious so they come up to humans.
Feedback: Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.
""",
           "so" : """Their response must use information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Your feedback should start with 'Nice work!' when the response says one of the following:
- Rottnest tourism increased 30%, or Tourism Australia made Rottnest Island the star of a global campaign,
- increased tourism is helping the quokkas, because it pays for research, conservation efforts, and to spread awareness,
- quokka selfies became a social media trend, with 37,000 posts.

Your feedback should start with 'You have the right idea! Now be more specific' when:
- it merely says quokka selfies have a positive effect, without specifying what effect exactly,
- it merely says that more tourists are visiting Rottnest Island, without mentioning the precise percentage,
- it just says Rottnest is a good place to take quokka selfies,
- it merely says quokka selfies became a social media trend, without mentioning numbers,
- it says Rottnest Island was made the star of a global campaign, but not by who,
- it misuses the conjunction,

Your feedback should start with 'Try clearing your response and starting again' in all other cases.

Here are some general rules for your feedback:
- Make sure your response is *understandable and engaging for a fifth grade student*. Use simple language, clear explanations, and avoid complex vocabulary or concepts.
- Try to keep you feedback short and friendly.
- Focus on one issue only. You are not an annoying bot. It is annoying when a student gets an additional piece of feedback. Only tell the student one thing. When you are telling two things, you are being annoying.
- Do NOT give feedback about conciseness.
- Do NOT correct grammar and spelling errors.
- Do not say "great job", but "nice work".

Here are some example responses and their desired feedback:
Response: the Island tourism increased 30% from 2017 to 2018.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: so the Australian government decided to make Rottnest Island the main attraction of its global campaign in 2019.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: in 2019 Tourism Australia decided to make island the head of its global campaign.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: Rottnest island's tourism increased 30%.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: an increase in tourism helps fund protection for quokkas.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: because of the quokkas the tourism has gone up 30%, and that has helped the awareness of the quokkas.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: they have increased the tourism in Rottnest Island which pays for research and protection.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: #Quokka Selfie has become an Instagram trend with over 37,000 posts.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: It promotes tourism, it has 37,000 posts on social media.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: people started posting their quokka pictures online in 2010’s with over 37,000 posts.
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: It has a favorable influence on the quokkas, which in turn has a positive impact on the animals.
Feedback: You have the right idea! Now be more specific. The selfie trend has helped Rottnest Island. What positive effects is Rottnest Island experiencing?

Response: the reputation of Rottnest island and quokkas increased.
Feedback: You have the right idea! Now be more specific. The selfie trend has helped Rottnest Island. What positive effects is Rottnest Island experiencing?

Response: Rottnest Island's tourism went up significantly in just over a year.
Feedback: You have the right idea! Now be more specific. More tourists are visiting Rottnest Island. How many more tourists are visiting Rottnest Island?

Response: it attracted so many people to visit Australia.
Feedback: You have the right idea! Now be more specific. More tourists are visiting Rottnest Island. How many more tourists are visiting Rottnest Island?

Response: they have to be careful doing taking selfies as quokkas can be dangerous and bite some tourists.
Feedback: Try clearing your response and starting again. So is used to explain a consequence or result. Go back to the text and look for a result of the fact that many tourists enjoy taking quokka selfies.

Response: they travel to Rottnest Island in Western Australia just to go take the selfies.
Feedback: Try clearing your response and starting again. Instead of talking about why Rottnest Island is a good place to take a quokka selfie, focus on an effect that the quokka selfie trend has had on the island.

Response: It has become a big social media trend.
Feedback: You have the right idea! Now be more specific. Quokka selfies have become a social media trend. How many people does the text say have posted a quokka selfie?

Response: they can post it on social media so other people can see the quokkas.
Feedback: Try clearing your response and starting again. Instead of talking about why people want to take quokka selfies, focus on an effect that the quokka selfie trend has had on the island.

Response: They made it the center of a worldwide campaign in 2019.
Feedback: You have the right idea! Now be more specific. Rottnest Island is now the star of a global campaign thanks to quokkas. Who made Rottnest Island the star of its campaign?

Response: it's a very cool and fun thing to do but be aware when near to them.
Feedback: Try clearing your response and starting again. What happened as a result of the fact that many tourists enjoy taking quokka selfies? Check that your response only uses information from the text.
"""
        },
        "feedback_and_label": {
           "because": """Their response must use information from the text to explain why many tourists enjoy taking quokka selfies.

You have to classify the response and give students feedback on the content. Here are the possible labels:
- Optimal_1: quokkas have curved mouths and look happy or look like they're smiling
- Optimal_2: quokkas are curious and approach humans
- Optimal_3: quokkas are curious and look like they're smiling
- Label_1: the response says that quokkas look happy or look like they're smiling, but doesn't mention their curved mouths
- Label_2: the response says that quokkas are curious, but doesn't mention they like to approach humans
- Label_3: the response says that quokkas are cute, but does not mention why
- Label_4: the response says that quokka selfies are a social media trend
- Label_0: the response is not based on the text, or uses the conjunction incorrectly


Here are some example responses, with their labels and feedback.

Response: quokkas have naturally curved mouths that make them look like they're smiling.
Label: Optimal_1
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: the quokkas always smiling, thanks to their curved mouth.
Label: Optimal_1
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they have a curved mouth, so it makes them look like they are happy all the time.
Label: Optimal_1
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are curious and approach humans.
Label: Optimal_2
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are naturally curious, which makes them want to go up to humans.
Label: Optimal_2
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they are friendly animals, and are excited to interact with humans.
Label: Optimal_2
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are curious and look like they're smiling.
Label: Optimal_3
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas are very photogenic and are always smiling, they also are naturally curious making them eager to approach humans.
Label: Optimal_3
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Reponse: quokkas are approachable and look happy.
Label: Optimal_3
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: they have smiling faces and are curious.
Label: Optimal_3
Feedback: Nice work! You used information from the text to explain why many tourists enjoy taking quokka selfies.

Response: quokkas' faces are unique since they always look like they are smiling.
Label: Label_1
Feedback: That's true—quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?

Response: #quokkaselfies are cute due to the animal appearing to be smiling.
Label: Label_1
Feedback: That's true—quokkas do look like they're smiling. Now add a detail from the text to strengthen your claim. What makes quokkas look like they're smiling?

Response: the quokka are also curious, and many tourist go and enjoy to taking selfies to the quokkas.
Label: Label_2
Feedback: That's true—quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?

Response: they're curious little creatures.
Label: Label_2
Feedback: That's true—quokkas are naturally curious. Now add a detail from the text to strengthen your claim. What shows that quokkas are curious?

Response: they are cute.
Label: Label_3
Feedback: That's true—many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?

Response: they have faces that are so remarkable and cute.
Label: Label_3
Feedback: That's true—many people think that quokkas are cute. Now add more details from the text to strengthen your claim. Why do people think that quokkas are cute?

Response: it became a trend on instagram and twitter.
Label: Label_4
Feedback: Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?

Response: these good photos turned into a social media trend.
Label: Label_4
Feedback: Quokka selfies have become a social media trend, but your response should focus on the reason why people like taking pictures with them. What is one reason why people enjoy taking selfies with quokkas?

Response: getting too close to quokkas can be illegal.
Label: Label_0
Feedback: Try clearing your response and starting again. Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.

Response: they are a one of a kind animal.
Label: Label_0
Feedback: Try clearing your response and starting again. Why do tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.
""",
           "but": """Their response must use information from the text to show a contrasting or surprising idea about the fact that many tourists enjoy taking quokka selfies.

You have to classify the response and give students feedback on the content. Here are the possible labels:
- Optimal_1: the response says that quokkas bite *dozens* of tourists every year. The word 'dozen' or 'dozens' MUST be used. If a synonym like 'many' is used, the response should get Label_2.
- Optimal_2: the response says that quokkas can get infected or die when they eat human food. For this label, the word 'dozens' is not required.
- Label_1: the response indicates there are risks involved, but no reference to food or biting
- Label_2: the response says quokkas bite, but does not use the word 'dozens'
- Label_4: the response mentions human food, but does not refer to infections or death
- Label_5: the response says people shouldn't get too close, but does not say why
- Label_8: the response says quokka selfies are only possible on Rottnest Island
- Label_9: the response mentions infections and death, but not human food
- Label_10: the response says quokkas cause infections
- Label_11: the response says quokkas are endangered
_ Label_0: the response is not based on the text or misuses the conjunction

Here are some example responses, with their labels and feedback. Do not give feedback on spelling or grammar.

Response: these animals are known to bite dozens of visitors each year.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: tourists shouldn't get too close to them because many tourists have been bitten by them; dozens of tourists are bitten by them each year.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: reports show that dozens of visitors are bitten by quokkas each year.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: there could be risks, for dozens of people are bitten by quokkas every year, and they may be infectious to human food.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: some of the zoologists say that to not let the selfies negatively affect the quokkas, and should avoid getting to close to them because of dozens of tourists are bitten each year by quokkas.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: many people feed the quokkas human food like bread that can lead to infections or even death.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: people fed them human food which can cause infections and even death.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: when they are fed human food it could infect or even kill them.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: it can also be dangerous and a potential risk when quokkas are fed human food, causing infections and sometimes death.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: visitors to be careful as some have been bitten and human food can give quokkas infections and even sometimes cause death.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a contrasting or suprising idea about the fact that many tourists enjoy taking quokka selfies.

Response: it can be dangerous sometimes.
Label: Label_1
Feedback: That's true—taking quokka selfies can be risky. Now make your response even stronger by adding specific information from the text. What negative effects can quokka selfies lead to?

Response: zoologists have warned to not ruin their habitat with the photos.
Label: Label_1
Feedback: That's true—taking quokka selfies can be risky. Now make your response even stronger by adding specific information from the text. What negative effects can quokka selfies lead to?

Response: it can be harmful to the quokkas and humans as they sometimes bite.
Label: Label_2
Feedback: That's true—quokka selfies can sometimes lead to bites. Now make your response even stronger by adding a specific number from the text. How many people are bitten by quokkas each year?

Response: the animals can be dangerous and some tourists feed them human food which can be harmful.
Label: Label_4
Feedback: That's true—human food can be harmful to quokkas. Now make your response even stronger by adding specific information from the text. What can happen to quokkas if they eat human food?

Response: tourists have avoid getting too close to quokkas.
Label: Label_5
Feedback: That's true—tourists shouldn't get too close to the quokkas. Now make your response even stronger by adding specific information from the text. What can happen if a tourist gets too close?

Response: there is only one place where anyone can take a picture with quokka and it is Rottnest Island just off the coast of Perth in Western Australia.
Label: Label_8
Feedback: Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.

Response: Quokkas are particularly vulnerable to infection and death.
Label: Label_9
Feedback: That's true—quokka can get infections. Now make your response even stronger by adding specific information from the text. What can cause quokkas to get infected and die?

Response: humans can be bitten and then get an infection.
Label: Label_10
Feedback: Quokka bites could cause infections, but the text doesn't say that. Read the part again. How can tourists cause quokkas to get infected?

Response: they are an endangered species with only about 12,000 left.
Label: Label_11
Feedback: Revise your response. Instead of talking about the fact that quokkas are endangered, focus on a contrast to the idea that tourists enjoy taking photos with them.

Response: they are also curious so they come up to humans.
Label: Label_0
Feedback: Try clearing your response and starting again. What is a contrast to the fact that many tourists enjoy taking selfies with quokkas? Check that your response only uses information from the text.
""",
           "so" : """Their response must use information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

You have to classify the response and give students feedback on the content. Here are the possible labels:
- Optimal_1: Rottnest tourism increased 30% or Tourism Australia made Rottnest Island the star of a global campaign
- Optimal_2: Increased tourism helps the quokkas, as it pays for research and conservation efforts, and spreads awareness
- Optimal_3: Quokka selfies became a social media trend with 37,000 posts
- Label_1: The response says the quokka selfie is having a positive effect on quokkas and the island, but does not say why
- Label_2: The response says more tourists are visiting Rottnest Island, but does not mention the 30%
- Label_3: The response misuses the conjunction
- Label_4: Rottnest is a good place to take a good quokka selfie
- Label_5: The response says quokka selfies became a social media trend, but does not mention the number of posts
- Label_6: The response says that as a result, quokkas can be social media famous
- Label_7: The response says quokka selfies became the star of a global campaign, but does not refer to the Australian government
- Label_8: The response is not based on the text.

Here are some example responses, with their labels and feedback. Do not give feedback on spelling or grammar.

Response: the Island tourism increased 30% from 2017 to 2018.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: so the Australian government decided to make Rottnest Island the main attraction of its global campaign in 2019.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: in 2019 Tourism Australia decided to make island the head of its global campaign.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: Rottnest island's tourism increased 30%.
Label: Optimal_1
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: an increase in tourism helps fund protection for quokkas.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: because of the quokkas the tourism has gone up 30%, and that has helped the awareness of the quokkas.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: they have increased the tourism in Rottnest Island which pays for research and protection.
Label: Optimal_2
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: #Quokka Selfie has become an Instagram trend with over 37,000 posts.
Label: Optimal_3
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: It promotes tourism, it has 37,000 posts on social media.
Label: Optimal_3
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: people started posting their quokka pictures online in 2010’s with over 37,000 posts.
Label: Optimal_3
Feedback: Nice work! You used information from the text to show a consequence of the fact that many tourists enjoy taking quokka selfies.

Response: It has a favorable influence on the quokkas, which in turn has a positive impact on the animals.
Label: Label_1
Feedback: That's true—the selfie trend has helped Rottnest Island. Now make your response even stronger by adding specific details. What positive effects is Rottnest Island experiencing?

Response: the reputation of Rottnest island and quokkas increased.
Label: Label_1
Feedback: That's true—the selfie trend has helped Rottnest Island. Now make your response even stronger by adding specific details. What positive effects is Rottnest Island experiencing?

Response: Rottnest Island's tourism went up significantly in just over a year.
Label: Label_2
Feedback: That's true—more tourists are visiting Rottnest Island. Now make your response even stronger by adding a specific number from the text. How many more tourists are visiting Rottnest Island?

Response: it attracted so many people to visit Australia.
Label: Label_2
Feedback: That's true—more tourists are visiting Rottnest Island. Now make your response even stronger by adding a specific number from the text. How many more tourists are visiting Rottnest Island?

Response: they have to be careful doing taking selfies as quokkas can be dangerous and bite some tourists.
Label: Label_3
Feedback: Try clearing your response and starting again. So is used to explain a consequence or result. Go back to the text and look for a result of the fact that many tourists enjoy taking quokka selfies.

Response: they travel to Rottnest Island in Western Australia just to go take the selfies.
Label: Label_4
Feedback: Revise your response. Instead of talking about why Rottnest Island is a good place to take a quokka selfie, focus on an effect that the quokka selfie trend has had on the island.

Response: It has become a big social media trend.
Label: Label_5
Feedback: That's true—quokka selfies have become a social media trend. Now make your response even stronger by adding a specific number from the text. How many people does the text say have posted a quokka selfie?

Response: they can post it on social media so other people can see the quokkas.
Label: Label_6
Feedback: Revise your response. Instead of talking about why people want to take quokka selfies, focus on an effect that the quokka selfie trend has had on the island.

Response: They made it the center of a worldwide campaign in 2019.
Label: Label_7
Feedback: That's true—Rottnest Island is now the star of a global campaign thanks to quokkas. Now make your response even stronger by adding specific details. Who made Rottnest Island the star of its campaign?

Response: it's a very cool and fun thing to do but be aware when near to them.
Label: Label_8
Feedback: Try clearing your response and starting again. What happened as a result of the fact that many tourists enjoy taking quokka selfies? Check that your response only uses information from the text.
"""
        },
        "files" : {
            "because": {
                "train": "data/automl/quokkas_because_v7_train.jsonl",
                "test": "data/automl/quokkas_because_v7_test_automl.jsonl"
            },
            "but": {
                "train": "data/automl/quokkas_but_v3_train.jsonl",
                "test": "data/automl/quokkas_but_v3_test_automl.jsonl"
            },
            "so": {
                "train": "data/automl/quokkas_so_v6_train.jsonl",
                "test": "data/automl/quokkas_so_v6_test_automl.jsonl"
            }
        }
    },
    "athletes_salaries": {
        "passage": """Should Minor League Baseball Players Make More Money?

Living off peanut butter and jelly sandwiches. Sleeping on air mattresses, sofas, or floors in overcrowded apartments. Bringing home a small salary and working side gigs to make ends meet.

This is the not so glamorous life of a minor league baseball player.

What is Minor League Baseball?

Minor League Baseball, or MiLB, is a group of professional baseball leagues that are associated with Major League Baseball, or MLB. Minor league teams are used to train players to join the majors. Almost every major league player—from Babe Ruth to A-Rod—started in the minor leagues and worked their way up.

Should Minor Leaguers Make Higher Salaries?

Players and their advocates argue that players are not fairly paid for their work during the season. They often work over 60 hours a week, but are only paid for 40 hours. They also aren’t paid for spring training or the off-season. Most minor league players make very low salaries, with some making below the poverty line.

On the other hand, MLB argues that minor league players are paid bonuses to sign for a team. Additionally, if players make it to the major leagues, they could make millions of dollars. Even if they don’t, they can still make more money by choosing another career.

Taking Action

In 2014, a group of minor league players filed a class-action lawsuit against MLB over their low wages. Since then, the case has expanded to include thousands of players who were not paid for spring training or made salaries below the poverty line. They want back pay and rules to pay players for hours worked.

"The ultimate goal is pretty simple: to get MLB to comply with the same laws that Walmart and McDonald's comply with," Garrett Broshuis, a lawyer and former minor league player who filed the original lawsuit, told ESPN.

After facing several hurdles making its way through the courts, a trial is set for 2022. The lawsuit could have major consequences for the future of Minor League Baseball.
        """,
        "plagiarism": {
            "because": """They often work 60+ hours a week, but are only paid for 40 hours. They also aren’t paid for spring training or the off-season. Most minor league players make very low salaries, with some making below the poverty line.""",
            "but": """On the other hand, MLB argues that minor league players are paid bonuses to sign for a team. Additionally, if players make it to the major leagues, they could make millions of dollars. Even if they don’t, they can still make more money by choosing another career.""",
            "so": """In 2014, a group of minor league players filed a class-action lawsuit against MLB over their low wages.

After facing several hurdles making its way through the courts, a trial is set for 2022."""
        },
        "prompts": {
            "because": "Some minor league baseball players believe their salaries are unfair because",
            "but": "Some minor league baseball players believe their salaries are unfair, but",
            "so": "Some minor league baseball players believe their salaries are unfair, so"
        },
        "label_info_detailed": {
            "because": """
- they work over 60 hours a week but are only paid for 40 hours.
- they work many hours but are only paid for 40.
- they are worked for 20+ extra hours but do not receive pay for it.
- they are only paid for 40 hours while actually working for 60+ hours, and they are not paid for spring and off-season.
- they work over 60 hours a week, but are not paid that much.
- players are not fairly paid for their work during the season they say
- they are paid unfairly.
- players and their supporters argue that players are not fairly paid for their work during the season.
- they make very low salaries.
- many of them experience difficulties making ends meet, often having to obtain secondary sources of income.
- MLB claims they can make millions if they make it to the major leagues.
- Minor league players, on the other hand, are paid bonuses to join with a team, according to MLB.
- a group of players filed a lawsuit over their low wages.
- In 2014 a group of minor players field a class action against MLB over their low wages.
- they often work overtime.
- they work long hours, some of which are unpaid.
- they are expected to do significant amounts of unpaid work.
- they often work for 60+ hours a week.
- They frequently put in 60 or more hours each week.
- they not glamorous life of minor league baseball player in 2014.
            """},
        "files" : {
            "because": {
                "train": "data/automl/athlete_salaries_because_v3_train.jsonl",
                "test": "data/automl/athlete_salaries_because_v3_test_automl.jsonl"
            },
            "but": {
                "train": "data/automl/athlete_salaries_but_v3_train.jsonl",
                "test": "data/automl/athlete_salaries_but_v3_test_automl.jsonl"
            },
            "so": {
                "train": "data/automl/athlete_salaries_so_v4_train.jsonl",
                "test": "data/automl/athlete_salaries_so_v4_test_automl.jsonl"
            }
        }
    }

}

feedback_instructions = """
These are the general instructions for the feedback:
- Be nice.
- Give only one piece of feedback at a time.
- Use one sentence only.
- Don't give feedback about grammar and spelling.
- Don't give feedback about clarity and conciseness.
- Don't tell students they are wrong, but focus on the correction they need to make.
- Don't give an example of the right answer.
"""