def generate_sql_schema(neo4j_connector):
    node_query = """
    MATCH (n)
    RETURN DISTINCT labels(n) AS labels, keys(n) AS properties
    """
    node_result = neo4j_connector.query(node_query)

    tables = {}
    for record in node_result:
        label = record['labels'][0] if record['labels'] else None
        properties = record['properties']

        if not label:
            continue

        if label not in tables:
            tables[label] = {
                "columns": [],
                "foreign_keys": []
            }

        for prop in properties:
            col = (prop, "VARCHAR(255)")
            if col not in tables[label]["columns"]:
                tables[label]["columns"].append(col)

        if ("id", "VARCHAR(255)") not in tables[label]["columns"]:
            tables[label]["columns"].insert(0, ("id", "VARCHAR(255) PRIMARY KEY"))

    rel_query = """
    MATCH (a)-[r]->(b)
    RETURN DISTINCT labels(a) AS startLabels, type(r) AS relType, labels(b) AS endLabels
    """
    rels_result = neo4j_connector.query(rel_query)

    for rel in rels_result:
        start_labels = rel.get('startLabels', [])
        end_labels = rel.get('endLabels', [])

        if not start_labels or not end_labels:
            continue

        start_label = start_labels[0]
        end_label = end_labels[0]

        fk_column = f"{end_label.lower()}_id"

        if start_label in tables:
            tables[start_label]['foreign_keys'].append({
                "column": fk_column,
                "ref_table": end_label,
                "ref_column": "id"
            })

            if (fk_column, "VARCHAR(255)") not in tables[start_label]['columns']:
                tables[start_label]['columns'].append((fk_column, "VARCHAR(255)"))

    sql_statements = []
    for table_name, data in tables.items():
        cols = ",\n  ".join([f"{name} {type}" for name, type in data['columns']])
        fks = ",\n  ".join([
            f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['ref_table']}({fk['ref_column']})"
            for fk in data['foreign_keys']
        ])

        table_def = f"CREATE TABLE {table_name} (\n  {cols}"
        if fks:
            table_def += ",\n  " + fks
        table_def += "\n);"

        sql_statements.append(table_def)

    return "\n\n".join(sql_statements)
