from core.database import db

async def Aggregation_pipeline(queries):
    try:
        status = queries.get("status", "Active")
        limit = queries.get("limit", 10)
        sort_field = queries.get("sort_field", "first_name")
        sort_direction = queries.get("sort_direction", "asc")

        result = db.users.aggregate([
            {
                "$match" : {
                    "status": status
                }
            },
            {
                "$lookup": {
                    "from" : "teams",
                    "localField": "team_id",
                    "foreignField": "_id",
                    "as": "team_info"
                }
            },
            {
                "$unwind": "$team_info"
            },
            {
                "$project": {
                    "user_name": { "$concat": ["$first_name", " ", "$last_name"]},
                    "first_name": "$first_name",
                    "last_name": "$last_name",
                    "email": "$email",
                    "status": "$status",
                    "team": "$team_info.team_name"
                }
            },
            {
                "$sort": { sort_field: 1 if sort_direction == "asc" else -1 }
            },
            {
                "$limit": limit
            }
        ]).to_list(length=None)

        return result

    except:
        return []