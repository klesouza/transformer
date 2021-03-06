Simple method for transforming CSV to JSON  

**USAGE**  
``python [PATH TO transform.py] [PATH TO MAPPER FILE]``   

*__Example usage:__*  
``python ~/transform.py ~/mapper.json``

*__Example CSV file:__*    
``Name;wage``  
``Joseph Smith;5.000,00``

*__Example Mapper file:__*    
```  
{
    "options": {
		"data_file": "~/data.csv",
		"output_file": "~/output.json",
		"encoding": "ISO-8859-1",
		"sep": ";",
		"limit": 2,
		"header": true,
		"verbose": true
	}
    "mapper": {
        "Name": 0, //field index definition
        "Wage":{ //Custom field definition
            "source": 1,
            "formatter": "float",
            "decimal": ","  
        }
    }
}  
```

*__Example output file:__*    
```
{  
    Name: "Joseph Smith",
    Wage: 5000.00
}
```

    - Custom fields definition  
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
        ignoreIfNullEmpty: the field is not added to the output if the value is null or empty
    - Defining array field names
        { "ArrayField[].Field": 0 }
        "The arrays items are grouped for records in sequence and with the same id"
