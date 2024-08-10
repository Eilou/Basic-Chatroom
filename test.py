users = {"user_1" : {"connection" : "1", "room_id" : "2", "name" : "3"},
         "user_2" : {"connection" : "4", "room_id" : "5", "name" : "6"}}

print(users["user_2"]["connection"])
            # key 1   # key 2
users["user_2"]["connection"] = 9

print(users["user_2"]["connection"])


users.update({"user_3" : {"connection": "12", "room_id" : "-1", "name" : "15"}})
print(users)
users.pop("user_3")
print(users)