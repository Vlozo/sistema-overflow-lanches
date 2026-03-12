import unittest
from core.common.normalize import InvalidFormatError, normalize_list_dict, new_normalize_items, NORMALIZE_ERROR_CODES

class Test_Normalize_List_Dict(unittest.TestCase):
    data = [{"id": "1", "quantity":"2"}, 
            {"id": "2", "quantity":"5"}]
    
    def test_verify_lists(self):
        with self.assertRaises(InvalidFormatError) as context:
            normalize_list_dict([1, 2], "numbers")
        
        self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["2"])
    
    def test_data_is_not_dict(self):
        dict_format="{id, quantity}"

        with self.assertRaises(InvalidFormatError) as context:
            normalize_list_dict([1, 2], "numbers", dict_format=dict_format)
        
        self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["1"])
    
    def test_missing_callable(self):
        with self.assertRaises(InvalidFormatError) as context:
            normalize_list_dict(self.data, "products", dict_format="{id, quantity}")

        self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["2"])
    
    def test_callable_function(self):
        def fun_x(data_row):
            item = {}
            if int(data_row["id"]) == (1):
                item["product"] = "Pastel de carne"
            else:
                item["product"] = "Desconhecido"
            
            return item

        expected = [
            {"product": "Pastel de carne"},
            {"product": "Desconhecido"}
        ]

        self.assertEqual(
            normalize_list_dict(self.data, "products", fun_x, "{id, quantity}"),
            expected
        )
    
    def test_callable_not_returning_values(self):
        def fun_x(data_row):
            item = {}
            if int(data_row["id"]) == 1:
                item["product"] = "Pastel de carne"
            else:
                item["product"] = "Desconhecido"
        
        with self.assertRaises(InvalidFormatError) as context:
            normalize_list_dict(self.data, "products", fun_x, "{id, quantity}")
        
        self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["3"])

class Test_Normalize_Items(unittest.TestCase):
    data = [{"id": "1", "quantity":"2"}, 
            {"id": "2", "quantity":"3"}]

    def test_validation_rule(self):
        bad_data = [{"id": "foobar", "quantity" : ""}]
        bad_quantity = [{"id":"foobar", "quantity": -2}]

        with self.assertRaises(InvalidFormatError) as context:
            new_normalize_items(bad_data)
            self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["1"])

            new_normalize_items(bad_quantity)
            self.assertEqual(context.exception.code, NORMALIZE_ERROR_CODES["4"])

        result = new_normalize_items(self.data)
        self.assertEqual(result, [{'id': 1, 'quantity':2}, {'id': 2, 'quantity':3}]
)
        
    def test_returned_value_is_int(self):
        data = new_normalize_items(self.data)
        result = []
        for i in data:
            result.append(i["id"] + i["quantity"])

        self.assertEqual(result, [3, 5])

if __name__ == '__main__':
    unittest.main()