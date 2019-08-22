JUNKFOOD_BECAUSE_MAP = {
    "Unhealthy without Diabetes and Risk Factors": ["unhealthy"], 
    "Diabetes and Risk Factors": ["unhealthy", "diabetes and risk factors"],
    'Nutritional value without Diabetes and Risk Factors': ["nutritional value"], 
    'Obesity without Diabetes': ["obesity"]
}

JUNKFOOD_BUT_MAP = {
    "Schools providing healthy alternatives": ["schools", "healthy alternatives"], 
    "Students without choice": ["students"], 
    "Unclassified Off-Topic": ["off-topic"], 
    "School without generating money": ["schools"], 
    "Student choice": ["students", "choice"], 
    "Schools generate money": ["schools", "money"], 
    "Students can still bring/access junk food": ["students", "can bring junk food"]
}

EATINGMEAT_BECAUSE_MAP = {
    "Meat industry harms environment/uses resources w/o mentioning greenhouse gases or water": ["harms environment"],
    "Irrelevant fact from article": ["irrelevant"],
    "Meat industry harms animals": ["harms animals"],
    "Because as preposition": ["because as preposition"],
    "Meat industry produces greenhouse gases and/or uses water - specific numbers": ["harms environment",
                                                                                     "greenhouse gas or water",
                                                                                     "specific numbers"],
    "Outside of article's scope": ["outside scope"],
    "Meat industry produces greenhouse gases and/or uses water - general": ["harms environment",
                                                                            "greenhouse gas or water"],
    "Meat industry produces greenhouse gases and/or uses water - incorrect numbers or comparison": ["harms environment",
                                                                                                    "greenhouse gas or water",
                                                                                                    "incorrect numbers"]
}

EATINGMEAT_BUT_MAP = {
    "People will or should still eat meat": ["people will eat meat"],
    "Flexitarians benefit environment": ["flexitarian", "environment"],
    "Change without mentioning consumption": ["change"],
    "Meat creates jobs and benefits economy":["jobs and economy"],
    "Eating meat is necessary for good nutrition": ["nutrition"],
    "Eating meat is part of culture/tradition": ["culture"],
    "Outside of article's scope": ["outside scope"],
    "Flexitarian w/o connection to environment or jobs": ["flexitarian"],
    "Less meat consumption could harm economy and cut jobs": ["jobs and economy"],
    "The meat industry is important/thriving and/or exports/demand increasing": ["industry is thriving"],
    "Meat consumption harms environment": ["harms environment"]
}
