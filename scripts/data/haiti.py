passage = {
    "files": {
        "because": {
            "train": "data/automl/haiti_because_v2_train.jsonl",
            "validation": "data/automl/haiti_because_v2_validation.jsonl",
            "test": "data/automl/haiti_because_v2_test.jsonl"
        },
        "but": {
            "train": "data/automl/haiti_but_v3_train.jsonl",
            "validation": "data/automl/haiti_but_v3_validation.jsonl",
            "test": "data/automl/haiti_but_v3_test.jsonl"
        },
        "so": {
            "train": "data/automl/haiti_so_v2_train.jsonl",
            "validation": "data/automl/haiti_so_v2_validation.jsonl",
            "test": "data/automl/haiti_so_v2_test.jsonl"
        },
    },
    "text": """Among the jagged mountains that cover much of the island nation of Haiti, one peak stands out from the rest: Bonnet à l’Evêque. Here, over two hundred years ago, Haitian revolutionaries built a massive stone fortress called Citadelle Laferrière.

Today, the monumental structure has become a popular tourist site. For many Haitians, it’s a reminder of the revolutionary fight to establish the first free Black republic in the Caribbean.

**Colonial Saint-Domingue**

When the Seven Years’ War ended in 1763, France had lost most of its territory in North America. However, they kept their most valuable colony: Saint-Domingue (known today as Ayiti, or Haiti). The island’s climate and geography made it possible to grow cash crops on large plantations, and the French government exploited these resources to recover from costly conflicts like the Seven Years’ War. By the 1780s, plantations in Saint-Domingue supplied about 40% of Europe’s sugar and 60% of its coffee.

The plantation system was profitable, but it created an unstable social pyramid. A small group of wealthy white planters known as *grands blancs* (“big whites”) were at the top of this hierarchy. Enslaved people on the island—almost 500,000 people, or nearly 90% of residents—were at the bottom.

In the middle of this hierarchy were the *petits blancs* (“little whites”) and *gens de couleur* *libres* (“free people of color”). The *petits blancs* were poorer white people who were laborers or part of the working class. The *gens de couleur libres* had a variety of backgrounds; many were multiracial children of enslaved people and *grands blancs*, and some even owned plantations themselves.

**Life, Liberty, and Labor**

By 1789, revolutionary ideas from France had spread to Saint-Domingue. Each social group had its own grievances. *Grands blancs* didn’t want to pay taxes on their growing fortunes to a faraway leader. *Petits blancs* aligned with French revolutionaries and challenged the social hierarchy: they resented the power of both *grands blancs* and wealthy *gens de couleur libres*. The *gens de couleur libres*, even those with the privilege of wealth, were still seen as inferior because of their race.

Perhaps the biggest reason for social instability in Saint-Domingue, though, was that 90% of the population was enslaved and lived under incredibly brutal conditions. Some estimate that the life expectancy of an enslaved person born in the colony was 15 years; those transported from Africa often lived only 3 to 5 years. The mortality rate was so high that by 1787 over 40,000 enslaved people—nearly 10% of Saint-Domingue’s total population—were forcibly brought to the island every year to keep up with the deaths.

As long as there was enslavement, there was resistance. Communication networks among enslaved people and some *gens de couleur libres* shared news and promoted revolutionary ideas. Some enslaved people used violence to fight back against abusive enslavers, while others ran away and helped peers do the same. Maroons (people who escaped enslavement themselves) formed communities in Haiti's forests and mountains; they led and supported resistance efforts across the island too.

**From Resistance to Rebellion…**

These early organizing efforts helped make a larger revolt possible. In August of 1791, enslaved people from different plantations met together with spiritual leaders. A rebellion erupted across the island soon after. Within days, hundreds of plantations were burned to the ground.

Revolutionaries did this, in part, to disrupt the plantation economy. However, rebellion was also deeply personal for many enslaved people and free people of color. Some were fighting to escape the brutality of plantation life. Others were motivated by the belief that Enlightenment ideas should be applied literally. Self-government wasn’t just about political leadership—it actually meant the right to own yourself, and the denial of any right to own others.

As a result of this rebellion, many enslavers fled. Some returned to France, while others moved to places like the United States, where slavery remained legal and a plantation economy continued to grow. And, by 1793, formerly-enslaved people controlled nearly 30% of the island and had successfully united behind revolutionary leaders like Toussaint Louverture.

**…And Rebellion to Revolution**

While revolutionaries wanted to change the island society, independence from France wasn’t their goal at first. Enslaved people initially revolted to control their own lives and labor, and end enslavement on the island. However, when the French government used diplomacy and force to try to quash the rebellion, some questioned whether it was possible to end slavery while the country was governed by a colonial power.

Even after Haiti won its independence in 1804, the French military threat remained. Revolutionaries built forts like the Citadelle Laferrière, but many were never used. Instead, France attacked the island financially: the Haitian government was forced to pay reparations to former enslavers. Colonization—and the payments the French government demanded in exchange for the island’s sovereignty—had consequences that continue to impact Haiti today.

Importantly, the legacy of the successful 1791 rebellion and revolutionaries’ resilience and determination persists, too. When Haiti became the first free Black republic, it was also the site of another important global first: slavery was officially banned in the new nation’s constitution.
""",
    "plagiarism": {
        "because": """Revolutionaries did this, in part, to disrupt the plantation economy. However, rebellion was also deeply personal for many enslaved people and free people of color. Some were fighting to escape the brutality of plantation life. Others were motivated by the belief that Enlightenment ideas should be applied literally. Self-government wasn’t just about political leadership—it actually meant the right to own yourself, and the denial of any right to own others.

While revolutionaries wanted to change the island society, independence from France wasn’t their goal at first. Enslaved people initially revolted to control their own lives and labor, and end enslavement on the island. However, when the French government used diplomacy and force to try to quash the rebellion, some questioned whether it was possible to end slavery while the country was governed by a colonial power.""",
        "but": """While revolutionaries wanted to change the island society, independence from France wasn’t their goal at first. Enslaved people initially revolted to control their own lives and labor, and end enslavement on the island. However, when the French government used diplomacy and force to try to quash the rebellion, some questioned whether it was possible to end slavery while the country was governed by a colonial power.

Even after Haiti won its independence in 1804, the French military threat remained. Revolutionaries built forts like the Citadelle Laferrière, but many were never used. Instead, France attacked the island financially: the Haitian government was forced to pay reparations to former enslavers. Colonization—and the payments the French government demanded in exchange for the island’s sovereignty—had consequences that continue to impact Haiti today.""",
        "so": """As a result of this rebellion, many enslavers fled. Some returned to France, while others moved to places like the United States, where slavery remained legal and a plantation economy continued to grow. And, by 1793, formerly-enslaved people controlled nearly 30% of the island and had successfully united behind revolutionary leaders like Toussaint Louverture.

Importantly, the legacy of the successful 1791 rebellion and revolutionaries’ resilience and determination persists, too. When Haiti became the first free Black republic, it was also the site of another important global first: slavery was officially banned in the new nation’s constitution.

the French government used diplomacy and force to try to quash the rebellion""",
    },
    "prompts": {
        "because": "Enslaved people led a rebellion in Saint-Domingue in August of 1791 because",
        "but": "Enslaved people led a rebellion in Saint-Domingue in August of 1791, but",
        "so": "Enslaved people led a rebellion in Saint-Domingue in August of 1791, so"
    },
    "instructions": {
        "because": """Their response must use information from the text to explain why enslaved people led a rebellion in Saint-Domingue in August of 1791.

A response is optimal when it says that
- they wanted the right to govern themselves/their labor.
- they wanted to escape mistreatment on plantations.
- they wanted to disrupt the plantation economy.

A response is suboptimal when
- it says that they wanted more rights, without specifying what rights.
- it says they wanted to fight for change, without specifying what change.
- it merely says they met with others.
- it merely says they were enslaved and the conditions were brutal.
- it mentions revolutionary ideas, without the specifics of those ideas.
- it outlines the grievances of other socioeconomic groups.
- it says they hated slavers.
- it says they took the ideals of the Enlightenment literally.
- it misuses the conjuction.
""",
        "but": """Their response must use information from the text to show a contrasting or surprising idea about the 1791 rebellion in Saint-Domingue (Haiti).

A response is optimal when it says that
- France used diplomacy or force to stop the rebellion.
- it was uncertain whether slavery could end while the French government was in power.
- Haitian independence from France was not the initial motivation. In this case, the response must include at least one place name: Haiti or France.
- Haiti was not recognized as an independent country until years later.

A response is suboptimal when
- it misuses the conjunction by referring to a reason why enslaved people rebelled.
- it misuses the conjunction by listing a consequence or result of the rebellion.
- it says the threat remained, without specifying what threat.
- it says that France fought back, without specifying how.
- it says the revolutionaries didn't know if slavery could be stopped, but does not mention France or living under a colonial power.
- it says the plantation economy continued growing or slavery remained legal.
- it says something wasn't their first goal, without specifying what.
- in all other cases.
""",
        "so": """Their response must use information from the text to show an effect or consequence of the rebellion in Saint-Domingue.

A response is optimal when it says
- the slavers fled the island.
- slavery was banned in the constitution of the new nation.
- France tried to retake the island with force and diplomacy.
- formerly enslaved people controlled a sizable part of the island.
- the people united to fight with Toussaint Louverture or other revolutionary leaders.

A response is suboptimal when
- it merely says Haiti became independent.
- it says slavery was banned, without mentioning the new constution or country.
- it says France fought back, without specifying how.
- it mentions how enslaved people rebelled (e.g., by burning plantations), rather than a consequence of those actions.
- it says they continued fighting.
- it says people united, but not around whom.
- it says France used force or diplomacy, but does not explain their motivation for doing so.
"""
    },
    "feedback": {
        "because": {
            "Optimal_1": "Nice work! You used information from the text to explain why enslaved people led a rebellion in Saint-Domingue in 1791.",
            "Optimal_2": "Nice work! You used information from the text to explain why enslaved people led a rebellion in Saint-Domingue in 1791.",
            "Optimal_3": "Nice work! You used information from the text to explain why enslaved people led a rebellion in Saint-Domingue in 1791.",
            "Label_1": "It's true that Haitian revolutionaries wanted more rights in society. Now, be more specific. What right were they fighting to protect?",
            "Label_2": "Revolutionary leaders wanted to change life on the island—that's true. Now, be more specific. What change were they fighting for?",
            "Label_3": "Enslaved people met with spiritual leaders before the rebellions, but historians aren't sure that this meeting caused the rebellions. Revise your response—focus on a specific motivation or reason. Why did enslaved people lead a rebellion in August of 1791?",
            "Label_4": "Many on the island were enslaved and lived in harsh conditions—that's true. This is important context for the Haitian Revolution. Think about how this context is connected to revolutionaries' motivation or reason to rebel. What did revolutionaries want to do?",
            "Label_5": "It's true that the spread of new ideas helped motivate Haitian revolutionaries. Add more information from the text to make your response clearer. What specific belief or goal motivated people to rebel?",
            "Label_6": "Different groups had their own reasons to challenge the social hierarchy in Haiti—that's true. Make sure your response focuses on the group of people named in the stem. Why did enslaved people, specifically, led a rebellion?",
            "Label_7": "Some people may have felt this way, but we don't know for sure. Instead of making an inference about revolutionary leaders' feelings, focus on why they rebelled. What specific belief or goal motivated people to rebel?",
            "Label_8": """Almost there! Be more specific. What did it mean to take ideas about freedom and rights "literally"? How would that impact enslaved people in Haiti?""",
            "Label_0": "Try clearing your response and starting again. Why did enslaved people lead a rebellion in August of 1791? Check that your response only uses information from the text.",
        },
        "but": {
            "Optimal_1": "Nice work! You used information from the text to show a contrasting or surprising idea about the 1791 rebellion in Saint-Domingue (Haiti).",
            "Optimal_2": "Nice work! You used information from the text to show a contrasting or surprising idea about the 1791 rebellion in Saint-Domingue (Haiti).",
            "Optimal_3": "Nice work! You used information from the text to show a contrasting or surprising idea about the 1791 rebellion in Saint-Domingue (Haiti).",
            "Optimal_4": "Nice work! You used information from the text to show a contrasting or surprising idea about the 1791 rebellion in Saint-Domingue (Haiti).",
            "Label_1": "That's a reason why enslaved people rebelled in 1791. Add information from the text that shows a contrasting or complicating idea instead. How did France respond to this uprising?",
            "Label_2": "That's a result of the organized rebellion in 1791. Add information from the text that shows a contrasting or complicating idea instead. How did France respond to this uprising?",
            "Label_3": "It's true that a threat remained after the 1791 rebellion. Add information from the text to make your response clearer. Where did this threat come from?",
            "Label_5": "It's true that France tried to stop the rebellion. Add another detail to make your response more specific. How did France try to end the 1791 uprising?",
            "Label_6": "It's true that many didn't know if slavery could end. Add another detail to make your response more specific. Why did they think this?",
            "Label_7": "Revise your work. Focus your response on a contrast to the idea that enslaved people led a rebellion in 1791. How did France respond?",
            "Label_8": "It's true that revolutionaries had a different goal at first. Now add more details from the text to make your response even stronger. What wasn't their first goal?",
            "Label_0": "Try clearing your response and starting again. How did France respond to the 1791 rebellion? Check that your response only uses information from the text.",
        },
        "so": {
            "Optimal_1": "Nice work! You used information from the text to show an effect or consequence of the rebellion in Saint-Domingue.",
            "Optimal_2": "Nice work! You used information from the text to show an effect or consequence of the rebellion in Saint-Domingue.",
            "Optimal_3": "Nice work! You used information from the text to show an effect or consequence of the rebellion in Saint-Domingue.",
            "Optimal_4": "Nice work! You used information from the text to show an effect or consequence of the rebellion in Saint-Domingue.",
            "Optimal_5": "Nice work! You used information from the text to show an effect or consequence of the rebellion in Saint-Domingue.",
            "Label_1": "It's true that Haiti eventually became independent, but that happened 13 years after the rebellion. Revise your response—focus on a direct effect or consequence of the rebellion. What happened as a result of the 1791 uprising?",
            "Label_2": "You're on the right track! Add a detail from the text to make your response more specific. How was slavery banned?",
            "Label_3": "France tried to regain control of the island—that's true. Now be more specific. What actions did France take to do this?",
            "Label_4": "Those actions were part of the rebellion. Focus on the impact of those actions instead. What happened as a result of the rebellion in 1791?",
            "Label_5": "The 1791 rebellion inspired many to organize and continue fighting—that's true. What happened as a result of these efforts?",
            "Label_6": "Almost there! Add a detail from the text to make your response more specific. Who did people unite around after the 1791 rebellion?",
            "Label_7": "It's true that France used diplomacy and force against Haiti. Now add more details from the text to make your response even stronger. Why did they do this?",
            "Label_0": "Try clearing your response and starting again. What was an immediate result of the 1791 rebellion? Check that your response only uses information from the text.",
        }
    },
    "examples": {
        "because": {
            "Optimal_1": [
                "the enslaved population wanted to control their own lives and end enslavement on the island.",
                "they wanted control of their individual lives and rights."
            ],
            "Optimal_2": [
                "they wanted to escape the inhumane treatments they received on the plantations",
                "they were fighting to be free from the harsh plantation life."
            ],
            "Optimal_3": [
                "they wanted to disrupt the plantation economy that abused them.",
                "they wanted to break up the plantation economy on the island."
            ],
            "Label_1": [
                "they were slaves and wanted to be free.",
                "they wanted to have more of their rights."
            ],
            "Label_2": [
                "they wanted a change in society."
            ],
            "Label_3": [
                "enslaved people from different plantations met together with spiritual leaders."
            ],
            "Label_4": [
                "- they were all enslaved there on the island.",
                "they lived in slavery that was incredibly brutal.",
                "Saint-Domigue had brutal living conditions and life expectancy being about 15 years."
            ],
            "Label_5": [
                "revolutionary ideas spread from France after the French Revolution.",
                "enslaved people used communication networks to share revolutionary ideas."
            ],
            "Label_6": [
                "there was a unstable social pyramid leading to a large wealth gap.",
                "they didn't want to pay taxes on their growing fortunes."
            ],
            "Label_7": [
                "they hated the people that made them be slaves."
            ],
            "Label_8": [
                "they believed Enlightenment ideas should be applied literally."
            ],
            "Label_0": [
                "hundreds of plantations were burned to the ground."
            ]
        },
        "but": {
            "Optimal_1": [
                "the French government used diplomats to stop the rebellion.",
                "France tried to use force and fighting to end it."
            ],
            "Optimal_2": [
                "some weren't sure that slavery could be abolished while France controlled the island.",
                "many wondered if it was possible to end slavery while under a colonial power."
            ],
            "Optimal_3": [
                "their goal wasn’t to gain independence from France at first.",
                "their original goal was to be able to control their own lives, not make another country."
            ],
            "Optimal_4": [
                "they didn’t win Haiti’s independence until 1804",
            ],
            "Label_1": [
                "some were wanting to escape brutality, and others were motivated by the belief of Enlightenment.",
                "it was also deeply personal for many enslaved people."
            ],
            "Label_2": [
                "many of the enslavers fled to places that still had slavery.",
                "a rebellion erupted all over the island and hundreds of their plantations were burned."
            ],
            "Label_3": [
                "there was still a big threat to their freedom."
            ],
            "Label_5": [
                "France tried everything to stop this from happening.",
                "the government of France fought against it."
            ],
            "Label_6": [
                "some didn't think it could be done.",
                "it didn’t seem like it was very possible to win.",
            ],
            "Label_7": [
                "slavery was still a thing.",
                "it didn’t actually make slavery end."
            ],
            "Label_8": [
                "that wasn't their first goal.",
            ],
            "Label_0": [
                "the social hierarchy was unbalanced."
            ]
        },
        "so": {
            "Optimal_1": [
                "some enslavers went into hiding or fled the island entirely.",
                "many enslavers went back to France or to the United States"
            ],
            "Optimal_2": [
                "slavery was made illegal in the new constitution.",
                "the Haitian constitution officially banned slavery in the nation."
            ],
            "Optimal_3": [
                "France attacked them to try to retake the island."
            ],
            "Optimal_4": [
                "many enslavers fled and the revolutionaries gained control over 30% of the island."
            ],
            "Optimal_5": [
                "members from different plantations joined together to keep fighting with leaders like Toussaint Louverture."
            ],
            "Label_1": [
                "they won their independence and became the first black free republic.",
                "they were able to win their independence in 1804.",
                "Haiti became the first free black republic."
            ],
            "Label_2": [
                "They made slavery illegal.",
                "they escaped slavery and banned it officially",
                "slavery isn’t allowed anymore."
            ],
            "Label_3": [
                "the French tried to stop it"
            ],
            "Label_4": [
                "hundreds of plantations were burned to the ground.",
                "this caused a lot of violence and for a lot of plantations to be burned down."
            ],
            "Label_5": [
                "they fought until they were free.",
                "their determination persists."
            ],
            "Label_6": [
                "many came together for the cause. "
            ],
            "Label_0": [
                "things were better then."
            ]
        }
    },
    "evaluation": {
        "because": {
            "Optimal_1": [
                "They wanted the right to control their own lives.",
                "They wanted the right to control their own lives.",
            ],
            "Optimal_2": [
                "They wanted to escape mistreatment on plantations.",
                "They wanted to escape mistreatment on plantations.",
            ],
            "Optimal_3": [
                "They wanted to disrupt the plantation economy.",
                "They wanted to disrupt the plantation economy.",
            ],
            "Label_1": [
                "They wanted more rights.",
                "They wanted more rights.",
            ],
            "Label_2": [
                "They wanted a change.",
            ],
            "Label_3": [
                "They met with others."
            ],
            "Label_4": [
                "They were enslaved and the conditions were brutal.",
                "They were enslaved and the conditions were brutal.",
                "They were enslaved and the conditions were brutal.",
            ],
            "Label_5": [
                "They had revolutionary ideas.",
                "They had revolutionary ideas.",
            ],
            "Label_6": [
                "Other socioeconomic groups also had grievances.",
                "Other socioeconomic groups also had grievances.",
            ],
            "Label_7": [
                "They hated slavers.",
            ],
            "Label_8": [
                "They took the ideals of the Enlightenment literally."
            ],
            "Label_0": [
                "Does not give a reason why enslaved people led a rebellion in Saint-Domingue in August of 1791."
            ]
        },
        "but": {
            "Optimal_1": [
                "France used diplomacy or force to stop the rebellion.",
                "France used diplomacy or force to stop the rebellion.",
            ],
            "Optimal_2": [
                "It was uncertain whether slavery could end while the French government was in power.",
                "It was uncertain whether slavery could end while the French government was in power.",
            ],
            "Optimal_3": [
                "Haitian independence from France was not the initial motivation.",
                "Haitian independence from France was not the initial motivation.",
            ],
            "Optimal_4": [
                "Haiti was not recognized as an independent country until years later."
            ],
            "Label_1": [
                "Gives a reason why enslaved people rebelled.",
                "Gives a reason why enslaved people rebelled.",
            ],
            "Label_2": [
                "Gives a consequence or result of the rebellion.",
                "Gives a consequence or result of the rebellion.",
            ],
            "Label_3": [
                "The threat remained. Does not specify what threat."
            ],
            "Label_5": [
                "France fought back. Does not specify how.",
                "France fought back. Does not specify how.",
            ],
            "Label_6": [
                "The revolutionaries didn't know if slavery could be stopped. Does not mention France or living under a colonial power.",
                "The revolutionaries didn't know if slavery could be stopped. Does not mention France or living under a colonial power.",
            ],
            "Label_7": [
                "The plantation economy continued growing/slavery remained legal.",
                "The plantation economy continued growing/slavery remained legal.",
            ],
            "Label_8": [
                "Something wasn't their first goal. Does not specify what."
            ],
            "Label_0": [
                "Does not show a contrasting or suprising idea about the 1791 rebellion in Saint-Domingue (Haiti)."
            ]
        },
        "so": {
            "Optimal_1": [
                "The slavers fled the island.",
                "The slavers fled the island.",
            ],
            "Optimal_2": [
                "Slavery was banned in the constitution of the new nation.",
                "Slavery was banned in the constitution of the new nation.",
            ],
            "Optimal_3": [
                "France tried to retake the island with force and diplomacy."
            ],
            "Optimal_4": [
                "Formerly enslaved people controlled a sizable part of the island."
            ],
            "Optimal_5": [
                "The people united to fight with Toussaint Louverture or other revolutionary leaders."
            ],
            "Label_1": [
                "Haiti became independent.",
                "Haiti became independent.",
                "Haiti became independent.",
            ],
            "Label_2": [
                "Slavery was banned.",
                "Slavery was banned.",
                "Slavery was banned.",
            ],
            "Label_3": [
                "France fought back."
            ],
            "Label_4": [
                "Enslaved people rebelled, for instance by burning plantations.",
                "Enslaved people rebelled, for instance by burning plantations."
            ],
            "Label_5": [
                "They continued fighting.",
                "They continued fighting.",
            ],
            "Label_6": [
                "People united for the cause."
            ],
            "Label_0": [
                "Does not show an effect or consequence of the rebellion in Saint-Domingue."
            ]
        }
    }
}