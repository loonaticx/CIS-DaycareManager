def correctValType(entry_attr, _val_):
    """
    Attempts to correct input to the data type associated with the attribute in the database.
    """
    if isinstance(entry_attr, int) and _val_.isdigit():
        _val_ = int(_val_)
    if isinstance(entry_attr, str):
        _val_ = str(_val_)
    return _val_


class RequestHelper:
    @staticmethod
    def doPut(request, dbEntry, dataDict):
        # requested_arg here should be attributes/columns that were given to us from the input
        # & _val of course is the data we want to set the attribute to.
        for requested_arg, _val in request.args.items():
            if hasattr(dbEntry, requested_arg):
                val = correctValType(getattr(dbEntry, requested_arg), _val)
                dataDict[requested_arg] = val
                dbEntry.requested_arg = val

        return dbEntry, dataDict
