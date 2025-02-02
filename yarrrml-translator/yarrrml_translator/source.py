import re
import rdflib
from .constants import *


def get_initial_sources(data):
    list_initial_sources = []
    if YARRRML_SOURCES in data:
        for y in data.get(YARRRML_SOURCES):
            list_initial_sources.append(y)
    return list_initial_sources


def get_sources(data, mapping):
    if YARRRML_SOURCES in data.get(YARRRML_MAPPINGS).get(mapping):
        sources = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SOURCES)
    elif YARRRML_SOURCE in data.get(YARRRML_MAPPINGS).get(mapping):
        sources = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SOURCE)
    else:
        raise Exception("ERROR: sources not defined in mapping " + mapping)

    if type(sources) is not list:
        sources = [sources]

    return sources


def add_source(data, mapping, list_initial_sources):
    source_template = "\t" + RML_LOGICAL_SOURCE + " [\n\t\ta " + RML_LOGICAL_SOURCE_CLASS + \
                      ";\n\t\t" + RML_SOURCE + " "
    final_list = []
    sources = get_sources(data, mapping)
    for source in sources:

        if source in list_initial_sources:
            source = data.get(YARRRML_SOURCES).get(source)

        if YARRRML_ACCESS in source:
            if YARRRML_QUERY in source:
                final_list.append(source_template + database_source(mapping, source))
            else:
                final_list.append(source_template + add_source_full(mapping, source))
        elif type(source) is list:
            final_list.append(source_template + add_source_simplified(mapping, source))
        else:
            raise Exception("ERROR: source " + source + " in mapping " + mapping + " not valid")
    return final_list


def add_table(data, mapping, list_initial_sources):
    table_template = "\t" + R2RML_LOGICAL_TABLE + " [\n\t\ta " + R2RML_LOGICAL_TABLE_CLASS + \
                     ";\n\t\t"

    final_list = []
    sources = get_sources(data, mapping)
    for source in sources:
        sql_version = False
        if source in list_initial_sources:
            source = data.get(YARRRML_SOURCES).get(source)

        if YARRRML_ACCESS in source and YARRRML_QUERY in source:
            r2rml_access = database_source(mapping, source)
            sql_version = True
        elif YARRRML_QUERY in source:
            r2rml_access = R2RML_SQL_QUERY + " \"" + source.get(YARRRML_QUERY).replace("\n", " ").replace("\"",
                                                                                                          "\\\"") + "\""
        elif YARRRML_TABLE in source:
            r2rml_access = R2RML_TABLE_NAME + " \"" + source.get(YARRRML_TABLE) + "\""
        else:
            raise Exception("ERROR: table or query is not provided in " + source + " of mapping " + mapping)
        if not sql_version:
            if YARRRML_QUERY_FORMULATION in source:
                r2rml_access += ";\n\t\t" + R2RML_SQL_VERSION + " rr:" + source.get(YARRRML_QUERY_FORMULATION).upper()
            else:
                r2rml_access += ";\n\t\t" + R2RML_SQL_VERSION + " rr:SQL2008"
            r2rml_access += "\n\t];\n"
        final_list.append(table_template + r2rml_access)
    return final_list


def add_source_simplified(mapping, source):
    source_rdf = ""
    file_path = re.sub("~.*", "", source[0])
    reference_formulation = source[0].split('~')[1]
    source_extension = file_path.split('.')[1]
    ref_formulation_rml = reference_formulation.replace("jsonpath", "JSONPath").replace("csv", "CSV").replace("xpath",
                                                                                                              "XPath")
    if switch_in_reference_formulation(reference_formulation) != source_extension:
        raise Exception(
            "ERROR: mismatch extension and referenceFormulation in source " + source + " in mapping " + mapping)
    else:
        if len(source) == 1:  # si no tiene iterador
            if source_extension == "csv" or source_extension == "SQL2008":
                source_rdf += '"' + file_path + '"' + ";\n" + "\t\t" + RML_REFERENCE_FORMULATION + " ql:" \
                              + ref_formulation_rml + "\n" + "\t];\n"
            else:
                raise Exception("ERROR: source " + source + " in mapping " + mapping + " has no iterator")
        else:  # source[1] es el iterador en json y xml
            source_rdf += "\"" + file_path + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " ql:" \
                          + ref_formulation_rml + ";\n\t\t" + RML_ITERATOR + " \"" \
                          + source[1] + "\";\n\t];\n"
    return source_rdf


def add_source_full(mapping, source):
    source_rdf = ""

    access = str(source.get(YARRRML_ACCESS))
    extension = access.split(".")[1]

    if YARRRML_REFERENCE_FORMULATION in source:
        reference_formulation = str(source.get(YARRRML_REFERENCE_FORMULATION))
        format_from_reference = switch_in_reference_formulation(reference_formulation.lower())
        ref_formulation_rml = reference_formulation.replace("jsonpath", "JSONPath").replace("csv", "CSV").replace(
            "xpath",
            "XPath")
        if extension != format_from_reference or format_from_reference == "ERROR":
            raise Exception("ERROR: not referenceFormulation found or mismatch between the format and "
                            "referenceFormulation in source " + access + "in mapping " + mapping)
        if YARRRML_ITERATOR in source:
            source_iterator = str(source.get(YARRRML_ITERATOR))

            source_rdf += "\"" + access + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " ql:" \
                          + ref_formulation_rml + ";\n\t\t" + RML_ITERATOR + " \"" \
                          + source_iterator + "\"\n\t];\n"
        else:
            if extension == "csv" or extension == "SQL2008":
                source_rdf += "\"" + access + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " ql:" \
                              + ref_formulation_rml + ";\n\n\t];\n"
            else:
                raise Exception("ERROR: source " + access + "in mapping " + mapping + " has no referenceFormulation")

    else:
        if extension == "csv":
            source_rdf += "\"" + access + "\";\n\n\t];\n"
        else:
            raise Exception("ERROR: source " + access + "in mapping " + mapping + " has no referenceFormulation")

    return source_rdf


def database_source(mapping, source):
    source_rdf = ""
    if YARRRML_ACCESS in source:
        if YARRRML_CREDENTIALS in source:
            if YARRRML_TYPE in source:
                type = source.get(YARRRML_TYPE)
                access = source.get(YARRRML_ACCESS)
                username = source.get(YARRRML_CREDENTIALS).get(YARRRML_USERNAME)
                password = source.get(YARRRML_CREDENTIALS).get(YARRRML_PASSWORD)
                hash_datasource = abs(hash(access + type + username + password))
                source_rdf += "<#DataSource_" + str(hash_datasource) + ">;\n\t\t"
                if YARRRML_QUERY in source:
                    source_rdf += R2RML_SQL_QUERY + " \"" + source.get(YARRRML_QUERY) + "\""
                elif YARRRML_TABLE in source:
                    source_rdf += R2RML_TABLE_NAME + " \"" + source.get(YARRRML_TABLE) + "\""
                if YARRRML_REFERENCE_FORMULATION in source:
                    source_rdf += ";\n\t\t" + RML_REFERENCE_FORMULATION + " ql:" \
                                  + switch_in_reference_formulation(source.get(YARRRML_REFERENCE_FORMULATION))
                if YARRRML_QUERY_FORMULATION in source:
                    source_rdf += ";\n\t\t" + R2RML_SQL_VERSION + " rr:" + source.get(YARRRML_QUERY_FORMULATION).upper()
                else:
                    source_rdf += ";\n\t\t" + R2RML_SQL_VERSION + " rr:SQL2008"
                source_rdf += "\n\t];\n"
        else:
            raise Exception("ERROR: no credentials to get access to source in mapping " + mapping)
    else:
        raise Exception("ERROR: no access to the source in mapping " + mapping)

    return source_rdf


def switch_in_reference_formulation(value):
    value = value.lower()
    if value == "csv":
        switcher = value
    elif "json" in value:
        if "path" in value:
            switcher = "json"
        else:
            switcher = "jsonpath"
    elif "x" in value:
        if "path" in value:
            switcher = "xml"
        else:
            switcher = "xpath"
    return switcher


def generate_database_connections(data):
    database = []
    hash_ids = []
    for mapping in data.get(YARRRML_MAPPINGS):
        sources = get_sources(data, mapping)
        for source in sources:
            if YARRRML_QUERY in source and YARRRML_ACCESS in source:
                type = source.get(YARRRML_TYPE)
                if type == "mysql":
                    driver = "com.mysql.jdbc.Driver"
                elif type == "postgresql":
                    driver = "org.postgresql.Driver"
                elif type == "sqlserver":
                    driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
                else:
                    driver = None
                access = source.get(YARRRML_ACCESS)
                username = source.get(YARRRML_CREDENTIALS).get(YARRRML_USERNAME)
                password = source.get(YARRRML_CREDENTIALS).get(YARRRML_PASSWORD)
                hash_datasource = abs(hash(access + type + username + password))
                if not hash_datasource in hash_ids:
                    hash_ids.append(hash_datasource)
                    if driver is None:
                        database.append("<#DataSource_" + str(hash_datasource) + "> a " + D2RQ_DATABASE_CLASS + ";\n\t"
                                        + D2RQ_DSN + " \"" + access + "\";\n\t"
                                        + D2RQ_USER + " \"" + username + "\";\n\t"
                                        + D2RQ_PASS + " \"" + password + "\".\n\n")
                    else:
                        database.append("<#DataSource_" + str(hash_datasource) + "> a " + D2RQ_DATABASE_CLASS + ";\n\t"
                                        + D2RQ_DSN + " \"" + access + "\";\n\t"
                                        + D2RQ_DRIVER + " \"" + driver + "\";\n\t"
                                        + D2RQ_USER + " \"" + username + "\";\n\t"
                                        + D2RQ_PASS + " \"" + password + "\".\n\n")
    return database


def add_inverse_source(tm, rdf_mapping, mapping_format):
    try:
        query = f'SELECT ?source  WHERE {{ <{tm}> {R2RML_LOGICAL_TABLE}|{RML_LOGICAL_SOURCE} ?source . }} '
        source = [tm[rdflib.Variable('source')] for tm in rdf_mapping.query(query).bindings][0]
    except Exception as e:
        logger.error("Logical Source or Logical Table is not defined in the mapping")
        logger.error(str(e))


    if mapping_format == R2RML_URI:
        yarrrml_source = get_logical_table(source, rdf_mapping)
    else:
        yarrrml_source = get_logical_source(source, rdf_mapping)

    return yarrrml_source


def get_logical_table(logical_table_id, rdf_mapping):
    table_name = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).tableName)
    sql_query = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).sqlQuery)
    sql_version = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).sqlVersion)

    if table_name is None and sql_query is None:
        logger.error("Mapping does not define neither tableName nor sqlQuery")
        raise Exception()
    yarrrml_source = {}
    if table_name:
        yarrrml_source["table"] = table_name.value
    elif sql_query:
        yarrrml_source["query"] = sql_query.value

    if sql_version:
        yarrrml_source["queryFormulation"] = sql_version.toPython().replace(R2RML_URI, '').lower()

    return yarrrml_source


def get_logical_source(logical_source_id, rdf_mapping):
    source = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(RML_URI).source)
    iterator = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(RML_URI).iterator)
    reference_formulation = rdf_mapping.value(subject=logical_source_id,
                                              predicate=rdflib.Namespace(RML_URI).referenceFormulation)
    sql_query = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(R2RML_URI).sqlQuery)
    sql_version = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(R2RML_URI).sqlVersion)

    if source is None:
        logger.error("Mapping does not define source access")
        raise Exception()
    yarrrml_source = []
    if source and reference_formulation and iterator:

        yarrrml_source.append(
            [source.value + '~' + reference_formulation.toPython().replace(QL_URI, '').lower(), iterator.value])
    elif source and sql_query:
        # this means a database source
        source_dict = {"query": sql_query.value, "source": source.value}
        if reference_formulation:
            source_dict["referenceFormulation"] = reference_formulation.toPython().replace(QL_URI, '').lower()
        if sql_version:
            source_dict["queryFormulation"] = sql_version.toPython().replace(R2RML_URI, '').lower()
        yarrrml_source.append(source_dict)
    elif source and reference_formulation:
        yarrrml_source.append([source.value + '~' + reference_formulation.toPython().replace(QL_URI, '').lower()])
    else:
        if source.endsWith(".csv"):
            yarrrml_source.append([source.value + '~csv'])
        else:
            yarrrml_source.append([source.value])

    return yarrrml_source