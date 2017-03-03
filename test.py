from dataloader import load_data_from_json

test = {"pear" : 1}
load_data_from_json(test, "test.json")
print test
