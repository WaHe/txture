from pattern.en import parsetree, lemma


invalid_noun = {'DT', 'PRP'}
valid_verbs = {'get', 'have', 'take', 'deliver', 'obtain'}
valid_prepositions = {'at', 'from', 'in', 'via'}
ignore_nouns = {'i', 'me', 'my', 'myself', 'mine'}


def nlp_parse(s):
    s = s.strip('?')
    s = parsetree(s)
    if len(s) != 1:
        return None, None
    sentence = s[0]
    last_np = None
    prep = None
    prep_nps = []
    sentence_invalid = False
    included_verbs = []
    for chunk in sentence.chunks:
        if chunk.type == 'PP':
            prep = chunk
            if not all(map(lambda w: word.string in valid_prepositions,
                           [word for word in chunk.words if word.pos == 'IN'])):
                print "Invalid preps"
                return None, None
        elif chunk.type == 'NP':
            if prep is None:
                last_np = chunk
            else:
                prep_nps += chunk.words
        elif chunk.type != 'NP' and prep is not None:
            print "something after a preposition that's not a noun"
            return None, None
        elif chunk.type == 'VP':
            included_verbs += [word.string for word in chunk.words if word.pos.startswith('VB')]
        print chunk.type + ":", [word for word in chunk.words]

    if last_np is None:
        print "no noun"
        sentence_invalid = True
    if prep is not None and len(prep_nps) == 0:
        print "preposition not followed by noun"
        sentence_invalid = True

    if sentence_invalid:
        return None, None
    else:
        print
        preposition_string = [word.string for word in prep_nps if word.pos not in invalid_noun]
        noun_string = [word.string for word in last_np.words if word.pos not in invalid_noun]
        print 'nouns:', noun_string, 'preps:', preposition_string, 'verbs:', included_verbs
        # No valid verbs
        if not any(map(lambda v: lemma(v.lower()) in valid_verbs, included_verbs)) and len(included_verbs) > 0:
            print "No correct verbs!"
            return None, None
        return noun_string, preposition_string


if __name__ == '__main__':
    nlp_parse("can I get a cheeseburger from mcdonalds?")
