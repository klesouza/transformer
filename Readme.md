Simple method for transforming CSV to JSON

**USAGE**
    - python [PATH TO transform.py] [PATH TO MAPPER FILE] [PATH TO CSV] [PATH OUTPUT FILE]
Example: 
> python ~/transform.py ~/mapper.json ~/mydata.csv ~/output.json

**MAPPER FILE**
    * JSON FILE
    * Format (Field name, csv position index (0-based)):
    ```
        {
            "Field1": 0, //field index definition
            "Field2":{ //Custom field definition
                "source": 0,
                "formatter": "float",
                "decimal": ","
            }
        }
    ```
    * Custom fields definition
        id(bool): specifies if the field identifies unique records
        source(int): csv position index (0-based)
        formatter(string): custom field formatting
            [
                date: "datetime cast, requires 'format' field",
                float: "float cast, accepts 'decimal' field",
                int: "cast to int",
                mapping: "requires 'mapping' field",
                static: "requires 'value'"
            ]
        format(string): specifies input date format
        decimal(char): specifies the decimal separator
        mapping(dictionary): a dictionary with dictionary with key(input) and value (output)
        value(anything): static value to be used
        padl(int): pad left the input
    - Defining array field names
        { "ArrayField[].Field": 0 }
        "The arrays items are grouped for records in sequence and with the same id"
