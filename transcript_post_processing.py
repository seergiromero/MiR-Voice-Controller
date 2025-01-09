import spacy
from rapidfuzz import process
from rest import Rest_API

class PostProcessing(Rest_API):

    def __init__(self, debug=False):

        # Call the init from Rest_Api class
        super().__init__()

        # Load english spaCy model
        self.nlp = spacy.load('en_core_web_lg')
        self.instructions = ["go", "execute", "send", "move"]
        self.instructions_nlp = [self.nlp(inst) for inst in self.instructions]
        self.positions = self.get_positions()
        self.missions = self.get_missions()
        self.debug = debug
        self.instruction = ""
        self.position = []
        self.mission = []

    def normalize_phrase(self, phrase):
        '''
        Normalize the phrase by making it lower 
        '''
        return phrase.lower()

    def detect_synonyms(self, verbs):
        """
        Detect works that could be synonims of "go" in the phrase using
        spaCy model in english
        """
        
        for verb in verbs:
            # Reference verb
            verb_nlp = self.nlp(verb)

            # Look for synonyms
            for instruction in self.instructions_nlp:
                instruction = self.nlp(instruction)
                similarity = instruction.similarity(verb_nlp)
                if similarity > 0.6:  # Similarity threshold
                    if self.debug: print(f"- {instruction} (similarity: {round(similarity, 2)})")
                    return instruction
                    
        return None 
        
    def extract_tokens(self, phrase):
        '''
        Function to extract the important verbs and words from the phrase
        '''
        doc = self.nlp(phrase)

        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        words = [token.text for token in doc if token.ent_type_ in ["LOC", "ORG", "GPE"] or token.pos_ in ["PROPN", "NOUN"] or token.dep_ in ["acomp", "relcl"]]

        return verbs, words

    def find_relation(self, tokens, data):
        '''
        Find a word that has a high relation with one word from data
        '''
        matches = []
        for token in tokens:
            match, score, _ = process.extractOne(token, data)
            if score > 70:
                matches.append(match)
        return matches if matches else None
    
    def normalize_instruction(self):
        self.instruction = str(self.instruction)

        self.instruction = 'go' if self.instruction == 'send' else self.instruction
        self.instruction = 'go' if self.instruction == 'move' else self.instruction

    def select_mission(self):
        """
        Function to select a specific mission in case of multiple choice.
        """
        if len(self.mission) > 1:
            print("More than one coincidence has been detected, select the mission you want to execute:")
            for i, mission in enumerate(self.mission):
                print(f"{i}. {mission}")
            result = int(input("Select the number of the mission you want to execute: "))
            return self.mission[result]
        return self.mission[0]  # In case there is only one mission, return it directly

    def run_model(self, phrase):
        self.analyze_phrase(phrase)
        self.normalize_instruction()
        actions = {
            'go': lambda: self.go_to(self.position[0]) if self.position[0] else print("No position found."),
            'execute': lambda: self.execute_mission(self.select_mission())
        }

        if self.instruction in actions:
            actions[self.instruction]()
        else:
            print("Instruction not recognized.")
        
    def analyze_phrase(self, phrase):
        '''
        Extract the positions, instructions and missions from the phrase
        '''

        phrase = self.normalize_phrase(phrase)
        verbs, words = self.extract_tokens(phrase)

        if self.debug:
            print("Verbs detected:", verbs)
            print("Words detected:", words)

        self.instruction = self.detect_synonyms(verbs)
        print(self.positions)
        print(self.missions)
        self.position = self.find_relation(words, self.positions)
        self.mission = self.find_relation(words, self.missions)

        if self.debug:
            print("Instruction found:", self.instruction)
            print("Position found:", self.position)
            print("Mission found:", self.mission)
