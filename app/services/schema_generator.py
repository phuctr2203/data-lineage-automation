def generate_sql_schema(neo4j_connector):
    nodes_query = """
    MATCH (n)
    WITH labels(n) AS labels, n LIMIT 100
    UNWIND labels AS label
    WITH label, collect(n) AS nodes
    RETURN label,
           keys(nodes[0]) AS properties
    """

    nodes_result = neo4j_connector.query(nodes_query)

    rels_query = """
    MATCH (a)-[r]->(b)
    RETURN DISTINCT labels(a) AS startLabels, type(r) AS relType, labels(b) AS endLabels
    """

    rels_result = neo4j_connector.query(rels_query)

    tables = {}

    for node in nodes_result:
        label = node['label']
        properties = node['properties']

        columns = []
        for prop in properties:
            sql_type = "VARCHAR(255)"
            columns.append((prop, sql_type))

        pk = 'id' if 'id' in properties else None

        tables[label] = {
            "columns": columns,
            "primary_key": pk,
            "foreign_keys": []
        }

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

            if fk_column not in [col[0] for col in tables[start_label]['columns']]:
                tables[start_label]['columns'].append((fk_column, "VARCHAR(255)"))


    sql_statements = []
    for table_name, table_info in tables.items():
        columns_sql = []
        for col_name, col_type in table_info['columns']:
            col_def = f"{col_name} {col_type}"
            if col_name == table_info['primary_key']:
                col_def += " PRIMARY KEY"
            columns_sql.append(col_def)

        fk_sql = []
        for fk in table_info['foreign_keys']:
            fk_sql.append(
                f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['ref_table']}({fk['ref_column']})"
            )

        all_constraints = columns_sql + fk_sql

        create_table_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(all_constraints) + "\n);"
        sql_statements.append(create_table_sql)

    return "\n\n".join(sql_statements)
