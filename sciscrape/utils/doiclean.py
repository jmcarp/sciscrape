
doi_rules = [
    ('/', '__'),
    (':', '--'),
]

def doi_clean(doi):
    
    return reduce(lambda d, rule: d.replace(rule[0], rule[1]), doi_rules, doi)

def doi_unclean(doi):
    
    return reduce(lambda d, rule: d.replace(rule[1], rule[0]), doi_rules, doi)
