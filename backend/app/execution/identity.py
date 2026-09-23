class IdentityError(ValueError): pass
IDENTIFIERS={"phone","iin","policy_number","claim_number"}
def identify(mock_backend:dict, supplied:dict)->dict:
    matches=[]
    for client in mock_backend.get("clients",[]):
        if any(str(client.get(key,""))==str(value) for key,value in supplied.items() if key in IDENTIFIERS):matches.append(client)
    if not matches: raise IdentityError("not_found")
    if len({x.get("client_id") for x in matches})!=1: raise IdentityError("conflicting_identifiers")
    return matches[0]
