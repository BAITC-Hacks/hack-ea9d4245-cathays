class IdentityError(ValueError): pass
IDENTIFIERS={"phone","iin","policy_number","claim_number"}
def identify(mock_backend:dict, supplied:dict)->dict:
    candidates = None
    for key, value in supplied.items():
        if key not in IDENTIFIERS or value is None or not str(value).strip():
            continue
        collection = {"policy_number": "policies", "claim_number": "claims"}.get(key, "clients")
        matches = {record["client_id"] for record in mock_backend.get(collection, []) if str(record.get(key, "")) == str(value)}
        if not matches:
            raise IdentityError("not_found")
        candidates = matches if candidates is None else candidates & matches
        if not candidates:
            raise IdentityError("conflicting_identifiers")
    if not candidates:
        raise IdentityError("not_found")
    if len(candidates) != 1:
        raise IdentityError("conflicting_identifiers")
    return next(client for client in mock_backend["clients"] if client["client_id"] in candidates)
