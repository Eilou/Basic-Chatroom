# users = {"user_1" : {"connection" : "1", "room_id" : "2", "name" : "3"},
#          "user_2" : {"connection" : "4", "room_id" : "5", "name" : "6"}}

# print(users["user_2"]["connection"])
#             # key 1   # key 2
# users["user_2"]["connection"] = 9

# print(users["user_2"]["connection"])


# users.update({"user_3" : {"connection": "12", "room_id" : "-1", "name" : "15"}})
# print(users)
# users.pop("user_3")
# print(users)

received_dict_name = {
    "message" : "garbonzo beans",
    "user_id" : "2",
    "name" : "chicken"
}

received_dict_no_name = {
    "message" : "garbonzo beans",
    "user_id" : "2"
}

name_prequel = ""
if "name" in received_dict_no_name:
    name_prequel = f'{received_dict_no_name["name"]} '
    
received = f'\t\t\t{name_prequel}({received_dict_no_name["user_id"]}) : {received_dict_no_name["message"].strip()}'
print(received)