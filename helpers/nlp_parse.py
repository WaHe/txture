from pattern.en import parsetree, lemma


invalid_noun = {'DT'}
valid_verbs = {'get', 'have', 'take', 'deliver', 'obtain'}
valid_prepositions = {'at', 'from', 'in', 'via'}


def nlp_parse(s):
    s = s.strip('?')
    s = parsetree(s)
    if len(s) != 1:
        return None, None
    sentence = s[0]
    last_np = None
    prep = None
    valid_preps = True
    prep_np = None
    sentence_invalid = False
    included_verbs = []
    for chunk in sentence.chunks:
        if chunk.type == 'PP':
            prep = chunk
            if not all(map(lambda w: word.string in valid_prepositions,
                           [word for word in chunk.words if word.pos == 'IN'])):
                print "Invalid preps"
                return None, None
        if chunk.type == 'NP':
            if prep is None:
                last_np = chunk
            elif prep_np is None:
                prep_np = chunk
            else:
                sentence_invalid = True
        if chunk.type == 'VP':
            included_verbs += [word.string for word in chunk.words if word.pos.startswith('VB')]
        print chunk.type + ":", [word for word in chunk.words]

    if last_np is None:
        sentence_invalid = True
    if prep is not None and prep_np is None:
        sentence_invalid = True

    if sentence_invalid:
        print "invalid sentence"
        return None, None
    else:
        preposition_string = [word.string for word in prep_np if word.pos not in invalid_noun]\
            if prep_np is not None else []
        noun_string = [word.string for word in last_np.words if word.pos not in invalid_noun]
        print 'nouns:', noun_string, 'preps:', preposition_string, 'verbs:', included_verbs
        # No valid verbs
        if not any(map(lambda v: lemma(v.lower()) in valid_verbs, included_verbs)) and len(included_verbs) > 0:
            print "No correct verbs!"
            return None, None
        return noun_string, preposition_string


if __name__ == '__main__':
    nlp_parse("can I get a cheeseburger from mcdonalds?")
