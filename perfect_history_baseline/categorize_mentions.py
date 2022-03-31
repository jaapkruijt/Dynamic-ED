
# Override spacy function (RECOMMENDED):

names = ['Bye Ryan', 'Ursula', 'Alan', 'Paul', 'Danielle', 'Horton', 'Randy Brown', 'Tommy Rollerson', 'Scott',
         'Carol', 'Julie', 'Dana', 'Michelle', 'Celia', 'Remore', 'Wong', 'Thomas', 'Greene', 'George',
         'Jason Hurley', 'Tina', 'Chandler', 'Jason', 'Joey', 'Helen', 'Monica', 'Rodney McDowell', 'Uncle Joey',
         'Susan', 'James Michener', 'Leon', 'Brian', 'Ed Begley', 'Bobby', 'Barry', 'Andie McDowell', 'Aunt Monica',
         'Todd', 'Aunt Phoebe', 'Amber', 'Bob', 'Stevie Fisher', 'Rachel', 'Ross', 'baby Ben', 'Janice',
         'Judy Jetson', 'Ryan', 'Ed', 'Stevie', 'Roger', 'Ben', 'Mary Tyler Moore', 'Lowell', 'Frankie',
         'Uncle Chandler', 'Drake Ramore', 'Eddie', 'Nina', 'Marcel', 'Shelley', 'Mindy', 'Geller', 'Silvian',
         'Bookbinders', 'Paulo', 'Drake', 'Bing', 'Peanut', "Andie McDowell 's", 'Gobb', "Ugly Naked Guy 's",
         'Paolo', 'Franks', 'Mira', 'Phoebe', 'Cobb', 'Tso']
fst_snd_prons = ['me I', 'MY', 'Me', 'You', 'My', 'my', 'ya', 'me', 'you', 'yourself', 'your', 'myself', 'ME', 'I',
                 'Your', 'mine', 'Ya', "what'cha", 'Whaddya', 'howdya', 'youve', 'youre', 'i']
prons = ['Her', 'her', 'she', 'himself', 'he', 'She', 'He', 'him', 'his', 'herself']
endearing = ['Nana', 'Mon', 'Dad', 'Mommy', 'Rach', 'Phoebs', 'mom', 'buddy', 'Hon', 'Pheebs', 'dad', 'Urse',
             'Daddy', 'birthday sweetie', 'honey', 'Rossy', 'pal']
context_dep = ['doctor', 'sister', 'grandmother', 'dad guy', 'son', 'chef', 'mother', 'boyfriend', 'man', 'uncle',
               'brother', 'Mr. 21', 'girl', 'baby', 'father', 'one', 'guy', 'nephew', 'giant', 'partner', 'husband',
               'aunt', 'grade teacher', 'roommate', 'person', 'typist', 'boy', 'team', 'tailor', 'voice woman',
               'fat boy', 'kid', 'home man', 'bitch', 'friend', 'woman', 'buyer', 'Mr. Sweet', 'surgeon guy',
               'pharmacist guy']
errors = ['her I', 'him I']

# make spacy function


def read_outfiles(out_file, reference_list):
    with open(out_file) as out:
        out_list = out.read().splitlines()
    out_tuples = list(zip(out_list, reference_list))

    return out_tuples


def split_todict(out_tups):
    names_list = []
    fst_snd_list = []
    prons_list = []
    endearing_list = []
    context_dep_list = []
    errors_list = []

    for entity, reference in out_tups:
        if reference in names:
            names_list.append(entity)
        elif reference in fst_snd_prons:
            fst_snd_list.append(entity)
        elif reference in prons:
            prons_list.append(entity)
        elif reference in endearing:
            endearing_list.append(entity)
        elif reference in context_dep:
            context_dep_list.append(entity)
        elif reference in errors:
            errors_list.append(entity)
        else:
            print(entity, reference)

    return {'names': names_list, 'fst_snd': fst_snd_list, 'prons': prons_list, 'endearing': endearing_list,
            'context_dep': context_dep_list, 'errors': errors_list}


def split_todict_for_analysis(out_dict):
    names_dict = {}
    fst_snd_dict = {}
    prons_dict = {}
    endearing_dict = {}
    context_dep_dict = {}
    errors_dict = {}

    for tstamp, tup in out_dict.items():
        if tup[1] in names:
            names_dict[tstamp] = tup
        elif tup[1] in fst_snd_prons:
            fst_snd_dict[tstamp] = tup
        elif tup[1] in prons:
            prons_dict[tstamp] = tup
        elif tup[1] in endearing:
            endearing_dict[tstamp] = tup
        elif tup[1] in context_dep:
            context_dep_dict[tstamp] = tup
        elif tup[1] in errors:
            errors_dict[tstamp] = tup
        else:
            print(tstamp, tup)

    return {'names': names_dict, 'fst_snd': fst_snd_dict, 'prons': prons_dict, 'endearing': endearing_dict,
            'context_dep': context_dep_dict, 'errors': errors_dict}


def write_to_out(out_dict, category_list, system):
    for category in category_list:
        f = open(f'{category}_{system}.out', 'w')
        for ent in out_dict[category]:
            f.write(ent+'\n')
        f.close()