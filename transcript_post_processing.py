import spacy

class PostProcessing:

    def __init__(self):
        pass


    def detect_synonyms(self, frase, word):
        """
        Detect works that could be synonims of "go" in the phrase using
        spaCy model in english
        """
        # Load english spaCy model
        nlp = spacy.load('en_core_web_lg')
        
        # Reference work
        word_nlp = nlp(word)[0]
        
        # Proccess the phrase
        doc = nlp(frase)
        
        # Look for synonyms
        found_synonyms = []
        for token in doc:
            if token.pos_ == 'VERB':
                similitud = token.similarity(word_nlp)
                if similitud > 0.6:  # Similarity threshold
                    found_synonyms.append({
                        'word': token.text,
                        'similarity': round(similitud, 2)
                    })
        
        return found_synonyms

    def analyze_phrase(self, phrase, word):
        phrase = phrase.lower()
        results = self.detect_synonyms(phrase, word)
        if results:
            print("Similar words to '%s' found:" % (word))
            for r in results:
                print(f"- {r['word']} (similarity: {r['similarity']})")
        else:
            print("No similar founds were found to '%s'" % (word))
        return results