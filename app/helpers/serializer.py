def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

def serialize_docs(docs):
    result = [serialize_doc(doc) for doc in docs]
    return result