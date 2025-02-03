import spacy
from rapidfuzz import process
from rest import RobotAPI
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Callable
from rest import RobotType


@dataclass
class NLPResult:
    instruction: Optional[str]
    position: Optional[List[str]]
    mission: Optional[List[str]]

class PostProcessing(RobotAPI):

    SIMILARITY_THRESHOLD = 0.6
    FUZZY_MATCH_THRESHOLD = 70
    BASIC_INSTRUCTIONS = ["go", "execute", "send"]    

    def __init__(self, debug=False, robot_type: RobotType = RobotType.SUPERMAN):

        # Call the init from Rest_Api class
        super().__init__(robot_type)

        # Load english spaCy model
        try:
            self.nlp = spacy.load('en_core_web_lg')
        except OSError:
            raise RuntimeError("Failed to load spaCy model. Please install it with: python -m spacy download en_core_web_lg")

        self.instructions_nlp = [self.nlp(inst) for inst in self.BASIC_INSTRUCTIONS]
        self.debug = debug
        self.load_initial_data()

    def get_data(self) -> None:
        """
        Initial load of positions and missions data
        """
        self.positions = self.get_positions() or [] # From rest.py
        self.missions = self.get_missions() or [] # From rest.py
        if self.debug:
            print(f"Loaded {len(self.positions)} positions and {len(self.missions)} missions")
    
    def load_initial_data(self) -> None:
        """
        Initial load of positions and missions data
        """
        self.positions = self.get_positions() or []
        self.missions = self.get_missions() or []
        if self.debug:
            print(f"Loaded {len(self.positions)} positions and {len(self.missions)} missions")

    def normalize_phrase(self, phrase: str) -> str:
        """
        Normalize the phrase by making it lower and removing extra spaces   
        """
        return ' '.join(phrase.lower().split())

    def detect_synonyms(self, verbs: List[str]) -> Optional[str]:
        """
        Detect works that could be synonims of "go" in the phrase using
        spaCy model in english
        """
        
        if not verbs:
            return None

        for verb in verbs:
            # Reference verb
            verb_nlp = self.nlp(verb)
            similarities = [(instruction.text, instruction.similarity(verb_nlp)) 
                          for instruction in self.instructions_nlp]
            
            # Look for synonyms
            best_match = max(similarities, key=lambda x: x[1])
            if best_match[1] > self.SIMILARITY_THRESHOLD:
                if self.debug:
                    print(f"Found synonym: {verb} -> {best_match[0]} (similarity: {round(best_match[1], 2)})")
                return best_match[0]
            
        return None
        
    def extract_tokens(self, phrase: str) -> Tuple[List[str], List[str]]:
        """
        Function to extract the important verbs and words from the phrase
        """
        doc = self.nlp(phrase)

        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        words = [token.text for token in doc if 
                token.ent_type_ in ["LOC", "ORG", "GPE"] or 
                token.pos_ in ["PROPN", "NOUN"] or 
                token.dep_ in ["acomp", "relcl"]]
        possible_robot = [token.text for token in doc if token.pos_ == "NOUN"]

        return verbs, words, possible_robot

    def find_relation(self, tokens: List[str], data: List[str]) -> Optional[List[str]]:
        """
        Find a word that has a high relation with one word from data
        """
        if not tokens or not data:
            return None
        
        matches = []
        for token in tokens:
            match, score, _ = process.extractOne(token, data)
            if score > self.FUZZY_MATCH_THRESHOLD:
                matches.append(match)
        return matches if matches else None
    
    def select_robot(self, possible_robot: str) -> None:
        for robot in possible_robot:
            robot_enum = getattr(RobotType, robot.upper(), None)
            if robot_enum:
                self._base_url = robot_enum.value[1]
                self.robot_type = robot_enum.value[0]
                print(f"Robot {robot_enum.value[0]} selected")

    def analyze_phrase(self, phrase: str) -> NLPResult:
        """
        Extract the positions, instructions and missions from the phrase
        """
        phrase = self.normalize_phrase(phrase)
        verbs, words, possible_robot = self.extract_tokens(phrase)
        if possible_robot: self.select_robot(possible_robot)

        if self.debug:
            print("Verbs detected:", verbs)
            print("Words detected:", words)

        self.get_data()

        instruction = self.detect_synonyms(verbs)
        position = self.find_relation(words, self.positions)
        mission = self.find_relation(words, self.missions)

        if self.debug:
            print(f"Analysis results - Instruction: {instruction}, Position: {position}, Mission: {mission}")
        
        return NLPResult(instruction, position, mission)

    def select_mission(self, missions: List[str]) -> Optional[str]:
        """
        Function to select a specific mission in case of multiple choice.
        """
        if not missions:
            return None
        if len(missions) == 1:
            return missions[0] # In case there is only one mission, return it directly

        print("\nMore than one coincidence has been detected, select the mission you want to execute:")
        for i, mission in enumerate(missions):
            print(f"{i}. {mission}")
        
        try:
            selection = int(input("\nSelect the number of the mission you want to execute: "))
            if 0 <= selection < len(missions):
                return missions[selection]
        except ValueError:
            print("Selección inválida")
        return None

    def run_model(self, phrase: str) -> None:

        result = self.analyze_phrase(phrase)
 
        if not result.instruction:
            print("No instruction found.")
            return
        normalized_instruction = 'go' if result.instruction in ['send', 'move'] else result.instruction
        actions: Dict[str, Callable] = {
            'go': lambda: self.go_to(result.position[0]) if result.position else print("No valid position was found."),
            'execute': lambda: self.execute_mission(self.select_mission(result.mission)) if result.mission else print("No valid mision was found.")
        }

        action = actions.get(normalized_instruction)
        if action:
            action()
        else:
            print(f"Instruction not recognized: {normalized_instruction}")
    
