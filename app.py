from flask import Flask, request, jsonify
import jsonschema


app = Flask(__name__)

# Schema taken from the given schema file
schema = {
     "type": "object",
    "properties": {
        "filters": {
            "type": "object",
            "properties": {
                "main.uploaded_variation": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["13_101107503_G/A", "7_21866494_C/T", "16_21736318_G/T", "LYPD2", "LNCOC1"]}
                },
                "main.af_vcf": {"type": "number"},
                "main.dp": {"type": "number"},
                "details2.dann_score": {"type": "number"},
                "links.mondo": {"type": "string"},
                "links.pheno pubmed": {"type": "string"},
                "details2.provean": {"type": "string"}
            }
        },
     "ordering": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},  # Field to sort
                    "direction": {"type": "string", "enum": ["ASC", "DESC"]}  # Sort direction (ASC or DESC)
                },
                "required": ["field", "direction"]
            }
        }
},
    "required": ["filters", "ordering"]
}



@app.route('/assignment/query', methods=['POST'])
def query_data():
    try:
        
        # We receive the incoming request in JSON format
        request_data = request.get_json()

        # Compare the incoming request with the schema
        jsonschema.validate(instance=request_data, schema=schema)

        # We receive incoming filters
        filters = request_data.get("filters", {})
        ordering = request_data.get("ordering", [])

       
        # Dynamic filtering process
        for key, value in filters.items():
            if key in filtered_data:
                filtered_data = list(filter(lambda x: x.get(key) == value, filtered_data))

        # The process of sorting data
        if ordering:
            for order_item in ordering:
                field = order_item.get("field")
                direction = order_item.get("direction")
                filtered_data = sorted(filtered_data, key=lambda x: x.get(field, ""), reverse=(direction == "DESC"))


        # Paging process
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_data = filtered_data[start_index:end_index]

        # Return results in JSON format
        response = {
            "message": "Başarılı bir istek sonrasında veriler başarıyla döndürüldü.",
            "page": page,
            "page_size": page_size,
            "count": len(filtered_data),
            "results": paginated_data
        }

        return jsonify(response), 200
    
    #error management
    except jsonschema.exceptions.ValidationError as e:
        #If the incoming request does not comply with the schema, return an error (400 Bad Request)
        error_message = "Geçersiz istek gönderildi: " + str(e)
        return jsonify({"error": error_message}), 400

    except Exception as e:
        # In other error cases, appropriate error management is performed (500 Internal Server Error).
        error_message = "Sunucu tarafında bir hata oluştu: " + str(e)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)