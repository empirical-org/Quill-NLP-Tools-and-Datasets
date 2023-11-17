passage = {
    "files": {
        "because": {
            "train": "data/automl/pompeii_because_v2_train.jsonl",
            "validation": "data/automl/pompeii_because_v2_validation.jsonl",
            "test": "data/automl/pompeii_because_v2_test.jsonl"
        },
        "but": {
            "train": "data/automl/pompeii_but_v2_train.jsonl",
            "validation": "data/automl/pompeii_but_v2_validation.jsonl",
            "test": "data/automl/pompeii_but_v2_test.jsonl"
        },
        "so": {
            "train": "data/automl/pompeii_so_v2_train.jsonl",
            "validation": "data/automl/pompeii_so_v2_validation.jsonl",
            "test": "data/automl/pompeii_so_v2_test.jsonl"
        },
    },
    "text": """**A Beautiful City is Lost**

In the ancient world, the bustling city of Pompeii, Italy, was a thriving and prosperous center of Roman life. Many of the wealthiest citizens of ancient Rome had homes within the city, and it was a well-known vacation destination. Pompeii contained beautiful shops, theaters, homes, apartment buildings, bathhouses, public toilets, and temples. Many of these buildings were decorated with mosaics and wall paintings called frescoes.

But one morning nearly two thousand years ago, the ground began to shake, and the people of Pompeii realized that Mount Vesuvius, the volcano located nearby, was erupting. A cloud of black ash spewed from its top, hiding the sun. Buildings toppled off their foundations, and within minutes the city was buried under a thick layer of ash. Thousands of people were killed, and the city was destroyed.

**The Unearthing of Pompeii**

After the eruption, most of Pompeii lay preserved underground for more than a thousand years. In the 18th century, sections of the city began to be rediscovered and layers of dirt and ash were removed to expose the buried buildings and streets. Researchers digging at the site, known as archaeologists, were thrilled to learn more about this long-forgotten city.

Unfortunately, these excavations often caused major problems. Immediately after being unearthed, the city’s frescoes and mosaics began to deteriorate since they were no longer protected from the damaging effects of light and oxygen. Other natural forces such as rain, humidity, and temperature soon weakened Pompeii’s ancient buildings and caused further deterioration to the frescoes and mosaics. Many of these buildings were poorly rebuilt with inappropriate materials and were difficult to maintain.

Pompeii has also been affected by tourists. Around 2.5 million people visit the city every year, and this heavy traffic wears away the surface of the roads. Visitors remove small sections of the buildings and mosaics to take home as souvenirs, and frescoes can be damaged when tourists brush up against them.

The deterioration of the site became impossible to ignore when people arrived one morning to find the House of the Gladiators in ruins. The Italian Culture Minister, Sandro Bondi, believed the house had collapsed because of heavy rains, which had weakened the building’s poorly reconstructed walls. In his statement to the press, the Italian President Giorgio Napolitano said, "We should all feel shame for what happened."

**Conservation Challenges**

Although Pompeii was in need of restoration, the Italian Ministry of Culture did not have the funding to adequately preserve the excavated portions of the city. It has been estimated that approximately $335 million could be needed to address all of the issues at Pompeii and to prevent further deterioration. Scholars and archaeologists began to fear that Pompeii would continue to crumble and that valuable information about ancient Roman life would be lost forever.

**A New Approach**

In order to help protect Pompeii from further damage, the site was included in the World Monuments Watch list by the World Monuments Fund in 1996. The organization claimed that the site was in disrepair, and they advocated for the creation of a plan to restore the city. In the late 1990s, the Superintendent of Pompeii, Pietro Guzzo, stopped all new excavations at the site in order to focus on restoring the existing buildings.

Two years after the collapse of the House of the Gladiators, the Italian government initiated the Great Pompeii Project. The goal of the more than $100 million project is to address the ongoing conservation and restoration concerns at the site. Although more is needed to fully restore Pompeii, this project includes protecting the buildings from weather and water damage, securing foundations and walls, and restoring the frescos.

Pompeii has much to teach us about what life was like in the ancient Roman world. Ongoing restoration programs, like the Great Pompeii Project, may help to ensure that future generations of archaeologists and visitors will be able to explore this ancient city.
""",
    "plagiarism": {
        "because": """Unfortunately, these excavations often caused major problems. Immediately after being unearthed, the city’s frescoes and mosaics began to deteriorate since they were no longer protected from the damaging effects of light and oxygen. Other natural forces such as rain, humidity, and temperature soon weakened Pompeii’s ancient buildings and caused further deterioration to the frescoes and mosaics. Many of these buildings were poorly rebuilt with inappropriate materials and were difficult to maintain.
Pompeii has also been affected by tourists. Around 2.5 million people visit the city every year, and this heavy traffic wears away the surface of the roads. Visitors remove small sections of the buildings and mosaics to take home as souvenirs, and frescoes can be damaged when tourists brush up against them.
The deterioration of the site became impossible to ignore when people arrived one morning to find the House of the Gladiators in ruins. The Italian Culture Minister, Sandro Bondi, believed the house had collapsed because of heavy rains, which had weakened the building’s poorly reconstructed walls.
""",
        "but": "Although Pompeii was in need of restoration, the Italian Ministry of Culture did not have the funding to adequately preserve the excavated portions of the city. It has been estimated that approximately $335 million could be needed to address all of the issues at Pompeii and to prevent further deterioration. Scholars and archaeologists began to fear that Pompeii would continue to crumble and that valuable information about ancient Roman life would be lost forever.",
        "so": """In order to help protect Pompeii from further damage, the site was included in the World Monuments Watch list by the World Monuments Fund in 1996. The organization claimed that the site was in disrepair, and they advocated for the creation of a plan to restore the city. In the late 1990s, the Superintendent of Pompeii, Pietro Guzzo, stopped all new excavations at the site in order to focus on restoring the existing buildings.

Two years after the collapse of the House of the Gladiators, the Italian government initiated the Great Pompeii Project. The goal of the more than $100 million project is to address the ongoing conservation and restoration concerns at the site. Although more is needed to fully restore Pompeii, this project includes protecting the buildings from weather and water damage, securing foundations and walls, and restoring the frescos.
""",
    },
    "prompts": {
        "because": "Experts thought that Ancient Pompeii needed restoration work because",
        "but": "Experts thought that Ancient Pompeii needed restoration work, but",
        "so": "Experts thought that Ancient Pompeii needed restoration work, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why experts thought that Ancient Pompeii needed restoration work.

A response is optimal when
- it includes at least two of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.
- it includes one of these elements plus tourists or excavation/restoration techniques.
- it refers to environmental factors, in combination with tourists/excavation/restoration techniques.
- it says that the city was poorly rebuilt or difficult to maintain, in combination with tourism or one of the elements above.
- it mentions careless excavation, in combination with tourism or one of the elements above.
- it says that tourists cause damage by brushing against the frescoes or taking parts of the buildings as souvenirs, and refers to heavy traffic.
- it says that traffic wears away the roads, or there are lots of tourists, in combination with heavy traffic.
- it says the House of the Gladiators had already collapsed.
- it says that information about Roman life could be lost, or that the city can help teach people about what Roman life was like.
- it says that excavations have caused damage or caused frescoes and mosaics or structures to deteriorate.

A response is suboptimal when
- it says the city is crumbling/deteroriating/collapsed/damaged, without saying why.
- it refers to tourists, but does not say what they do.
- it says a volcanic eruption destroyed the city.
- it includes only one of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.
- it says the city was poorly rebuilt, or not well preserved.
- it does not explain why experts thought that Ancient Pompeii needed restoration work.
        """,
        "but": """Their response must use information from the text to show a contrasting or suprising idea about the fact that experts thought that Ancient Pompeii needed restoration work.

A response is optimal when
- it says that the Italian Ministry of Culture did not have the funding.
- it says that it would cost $335 million.

A response is suboptimal when:
- it says that they didn't have enough funding, without specifying who.
- it says it would be expensive, without mentioning the amount.
- it does not show a contrasting or suprising idea about the fact that experts thought that Ancient Pompeii needed restoration work.
        """,
        "so": """Their response must use information from the text to show a consequence of the fact that experts thought that Ancient Pompeii needed restoration work.

A response is optimal when it says:
- the site was included in the World Monuments Watchlist or World Monuments Fund.
- the Superintendent of Pompeii, or Pietro Guzzo, stopped all new excavations at the site.
- the Italian government initiated the Great Pompeii Project or spent $100 million to address conservation or restoration concerns.

A response is suboptimal when:
- it says they stopped new excavations, without saying who.
- it mentions the Great Pompeii Project, without saying who started it.
- it says they're restoring the city, without saying how.
- it does not show a consequence of the fact that experts thought that Ancient Pompeii needed restoration work.
        """
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Optimal_2": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Optimal_3": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Optimal_4": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Optimal_5": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Optimal_6": "Nice work! You used information from the text to explain why experts thought that Ancient Pompeii needed restoration work.",
            "Label_1": "That's true! Now be more specific. Why was Ancient Pompeii damaged and deteriorating?",
            "Label_2": "That's true! Now be more specific. What do tourists do that damages Ancient Pompeii?",
            "Label_3": "Revise your response. It's true that a volcano eruption destroyed the city, but try talking about what happened after that. What caused damage after the city was unearthed?",
            "Label_4": "That's true! Now be more specific. What are two elements that the city was exposed to?",
            "Label_9": "That's true! Now be more specific. What is another detail about the rebuilding of Ancient Pompeii?",
            "Label_0": "Try clearing your response and starting again. Why did Ancient Pompeii need restoration work? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrasting or surprising idea about Ancient Pompeii's need for restoration work.",
            "Optimal_2": "Nice work! You used information from the text to show a contrasting or surprising idea about Ancient Pompeii's need for restoration work.",
            "Label_1": "That's true! Now be more specific. Who didn't have enough funding to preserve the city?",
            "Label_2": "That's true! Now be more specific. How much would it cost to preserve the city?",
            "Label_3": "Try clearing your response and starting again. Go back to the text and look for a reason why restoring Ancient Pompeii would be a challenge.",
            "Label_4": "Try clearing your response and starting again. Go back to the text and look for a reason why restoring Ancient Pompeii would be a challenge.",
            "Label_0": "Try clearing your response and starting again. Why was restoring Ancient Pompeii going to be difficult? Read the highlighted text for ideas.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show an effect or consequence of the fact that Ancient Pompeii needed restoration.",
            "Optimal_2": "Nice work! You used information from the text to show an effect or consequence of the fact that Ancient Pompeii needed restoration.",
            "Optimal_3": "Nice work! You used information from the text to show an effect or consequence of the fact that Ancient Pompeii needed restoration.",
            "Label_1": "That's true! Now be more specific. Who stopped all new excavations?",
            "Label_2": "That's true! Now be more specific. Who initiated the Great Pompeii Project?",
            "Label_4": "That's true! Now be more specific. What initiatives have been started to help restore the city?",
            "Label_0": "Try clearing your response and starting again. What initiatives have been started to help restore the city? Check that your response only uses information from the text.",
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "the effects of natural forces such as rain, humidity, and temperature caused Pompeii's buildings to deteriorate.",
                "it was deteriorated from the damages of light and oxygen after being excavated."
            ],
            "Optimal_2": [
                "the buildings were poorly rebuilt with inappropriate materials.",
                "Ancient Pompeii was poorly rebuilt, difficult to maintain, and rebuilt with the wrong materials."
            ],
            "Optimal_3": [
                "millions of people visit the city each year which causes wear on roads.",
                "2.5 million people visited it and some people take stuff, like removing small sections of buildings."
            ],
            "Optimal_4": [
                "they couldn't ignore it any more when the House of the Gladiators collapsed."
            ],
            "Optimal_5": [
                "valuable information about ancient Roman life would be lost forever."
            ],
            "Optimal_6": [
                "excavations caused the city's frescoes and mosaics to deteriorate.",
                "the excavations caused major damage and is leading to deterioration."
            ],
            "Label_1": [
                "the city very own frescoes and mosaics started to deteriorate.",
                "the building was starting to crumble.",
            ],
            "Label_2": [
                "Pompeii is being impacted by tourism.",
                "around 2.5 million people visit the city every year.",
            ],
            "Label_3": [
                "the eruption of Mount Vesuvius destroyed Pompeii.",
            ],
            "Label_4": [
                "mosiacs and frescoes deteriorated from natural forces.",
                "it had been damaged by rain.",
            ],
            "Label_9": [
                "many of the buildings were poorly rebuilt.",
                "Several of these structures were subparly rebuilt, and the city as a whole was not restored particularly effectively.",
            ],
            "Label_0": [
                "most of Pompeii lays preserved underground.",
            ]
        },
        "but": {
            "Optimal_1": [
                "the Italian Ministry of Culture did not have the money to help.",
                "the Italian Ministry of Culture lacked funding in order to preserve the city.",
                "Italy did not have the money to preserve the city."
            ],
            "Optimal_2": [
                "it is a very large project and it is expensive, costing $335 million dollars.",
                "restoration on the project would be tedious and would cost 335 million dollars.",
                "it would take $335 million to address all the issues in Pompeii."
            ],
            "Label_1": [
                "they didn't have the funding needed to restore the city.",
                "there wasn't enough money.",
                "they need a lot of money to do what needs to be done."
            ],
            "Label_2": [
                "it was going to cost a lot of money.",
                "restoration on the project would be tedious and cost consuming.",
                "it is very expensive to restore and maintain the city."
            ],
            "Label_3": [
                "the buildings were poorly rebuilt with inappropriate materials and were difficult to maintain.",
                "a lot of frescoes and mosaics and other stuff are getting deteriorated because of natural forces.",
                "there are still around 2.5 million people that visit the city every year."
            ],
            "Label_4": [
                "more than 100 million dollars was donated by the Italian government to oversee the restoration and any other concerns in order to restore the ancient city.",
                "the World Monuments Watch list protected it from further damage.",
                "the Italian government started the Great Pompeii Project in order to restore the lost city."
            ],
            "Label_0": [
                "it is an ancient city with minor historical value and would be a waste to repair.",
                "the ash preserved the city."
            ]
        },
        "so": {
            "Optimal_1": [
                "in 1996, the site was put on the World Monuments Watch list",
                "in order to help defend the ancient city, the site was added to the World Monuments attention by the World Monuments Fund in around 1996.",
                "it was added to the World Monuments Watch list in order to protect it."
            ],
            "Optimal_2": [
                "the Superintendent of Pompeii stopped all new excavations so that he could focus on restoring the existing buildings.",
                "Pietro Guzzo, the Superintendent of Pompeii, stopped the new excavations to focus on restoring.",
                "Pietro Guzzo stopped all new excavations to focus on the restoration of Pompeii."
            ],
            "Optimal_3": [
                "the Italian government initiated the Great Pompeii Project to address the restoration concerns of the site.",
                "a $100 million project is happening to help rebuild the city.",
                "there are projects like the Great Pompeii Project that are being set up in order to fund the restoration of this great city."
            ],
            "Label_1": [
                "efforts have been made to restore existing buildings rather than excavate buried ones.",
                "they have stopped all new excavations to help restore Ancient Pompeii.",
                "they stopped all excavations sites so no more damage would appear."
            ],
            "Label_2": [
                "they started the Great Pompeii Project to help.",
                "The Great Pompeii Project was launched.",
                "they started a project called the Great Pompeii Project."
            ],
            "Label_4": [
                "they started to protect the buildings from weather and water damage.",
                "the Italian government started a project to restore it",
                "they could protect Pompeii from further damage."
            ],
            "Label_0": [
                "they remove to expose the buried buildings and streets in the country and they are so happy for this.",
                "they built underground to protect their stuff.",
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_1": [
                "This response includes at least two of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.",
                "This response includes at least two of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.",
            ],
            "Optimal_2": [
                "This response says that Pompeii was poorly rebuilt/difficult to maintain.",
                "This response says that Pompeii was poorly rebuilt/difficult to maintain.",
            ],
            "Optimal_3": [
                "This response says tourists cause damage by brushing against the frescoes, taking parts of buildings or wearing away the roads.",
                "This response says tourists cause damage by brushing against the frescoes, taking parts of buildings or wearing away the roads.",
            ],
            "Optimal_4": [
                "This response says the House of Gladiators had already collapsed.",
            ],
            "Optimal_5": [
                "This response says information about Roman life could be lost."
            ],
            "Optimal_6": [
                "This response says excavation caused damage and is causing frescoes and mosaics to deteriorate.",
                "This response says excavation caused damage and is causing frescoes and mosaics to deteriorate.",
            ],
            "Label_1": [
                "This response merely says the city is damaged or deteriorating.",
                "This response merely says the city is damaged or deteriorating.",
            ],
            "Label_2": [
                "This response mentions tourists, but not the damage they cause.",
                "This response mentions tourists, but not the damage they cause.",
            ],
            "Label_3": [
                "This response says a volcanic eruption destroyed the city.",
            ],
            "Label_4": [
                "This response includes only one of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.",
                "This response includes only one of the elements the city is exposed to: rain, humidity, weather, oxygen, light or temperature.",
            ],
            "Label_9": [
                "This response says the buildings were poorly rebuilt, but does not mention inappropriate materials or difficult maintenance.",
                "This response says the buildings were poorly rebuilt, but does not mention inappropriate materials or difficult maintenance.",
            ],
            "Label_0": [
                "This response does not say why experts thought that Ancient Pompeii needed restoration work."
            ]
        },
        "but": {
            "Optimal_1": [
                "The Italian Ministry of Culture did not have the funding to preserve the city.",
                "The Italian Ministry of Culture did not have the funding to preserve the city.",
                "The Italian Ministry of Culture did not have the funding to preserve the city.",
            ],
            "Optimal_2": [
                "It would cost $335 million.",
                "It would cost $335 million.",
                "It would cost $335 million.",
            ],
            "Label_1": [
                "They didn't have enough funding. Does not refer to the Italian Minstry of Culture.",
                "They didn't have enough funding. Does not refer to the Italian Minstry of Culture.",
                "They didn't have enough funding. Does not refer to the Italian Minstry of Culture.",
            ],
            "Label_2": [
                "It would be expensive. Does not mention the amount.",
                "It would be expensive. Does not mention the amount.",
                "It would be expensive. Does not mention the amount.",
            ],
            "Label_3": [
                "Gives a reason why Pompeii needs restoration (like its deterioration or difficult maintenance).",
                "Gives a reason why Pompeii needs restoration (like its deterioration or difficult maintenance).",
                "Gives a reason why Pompeii needs restoration (like its deterioration or difficult maintenance).",
            ],
            "Label_4": [
                "Restoration/protection was started.",
                "Restoration/protection was started.",
                "Restoration/protection was started.",
            ],
            "Label_0": [
                "Does not give a contrasting or suprising idea about the fact that experts thought that Ancient Pompeii needed restoration work.",
                "Does not give a contrasting or suprising idea about the fact that experts thought that Ancient Pompeii needed restoration work.",
            ]
        },
        "so": {
            "Optimal_1": [
                "The site was included in the World Monuments Watchlist or World Monuments Fund.",
                "The site was included in the World Monuments Watchlist or World Monuments Fund.",
                "The site was included in the World Monuments Watchlist or World Monuments Fund.",
            ],
            "Optimal_2": [
                "Pietro Guzzo/the Superintendent of Pompeii stopped all new excavations at the site.",
                "Pietro Guzzo/the Superintendent of Pompeii stopped all new excavations at the site.",
                "Pietro Guzzo/the Superintendent of Pompeii stopped all new excavations at the site.",
            ],
            "Optimal_3": [
                "The Italian government initiated the Great Pompeii Project/spent $100 million to address conservation or restoration concerns.",
                "The Italian government initiated the Great Pompeii Project/spent $100 million to address conservation or restoration concerns.",
                "The Italian government initiated the Great Pompeii Project/spent $100 million to address conservation or restoration concerns.",
            ],
            "Label_1": [
                "They stopped new excavations. Does not mention Pietro Guzzo/the Superintendent of Pompeii.",
                "They stopped new excavations. Does not mention Pietro Guzzo/the Superintendent of Pompeii.",
                "They stopped new excavations. Does not mention Pietro Guzzo/the Superintendent of Pompeii.",
            ],
            "Label_2": [
                "Mentions the Great Pompeii Project, but not the Italian government.",
                "Mentions the Great Pompeii Project, but not the Italian government.",
                "Mentions the Great Pompeii Project, but not the Italian government.",
            ],
            "Label_4": [
                "They're restoring the city. Does not mention any initiatives.",
                "They're restoring the city. Does not mention any initiatives.",
                "They're restoring the city. Does not mention any initiatives.",
            ],
            "Label_0": [
                "Does not mention an effect or consequence of the fact that Ancient Pompeii needed restoration.",
                "Does not mention an effect or consequence of the fact that Ancient Pompeii needed restoration.",
            ]
        }
    }
}