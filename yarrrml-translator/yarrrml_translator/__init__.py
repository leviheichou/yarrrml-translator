from .constants import *
from .mapping import add_prefix, add_mapping, add_inverse_prefix, get_non_asserted_mappings
from .source import get_initial_sources, add_source, generate_database_connections, add_table, add_inverse_source
from .subject import add_subject, add_inverse_subject
from .predicateobject import add_predicate_object_maps, add_inverse_pom
import rdflib
import yaml


def translate(yarrrml_data, mapping_format=RML_URI):
    logger.info("Translating YARRRML mapping to [R2]RML")

    list_initial_sources = get_initial_sources(yarrrml_data)
    rml_mapping = [add_prefix(yarrrml_data)]
    rml_mapping.extend(generate_database_connections(yarrrml_data))
    try:
        mappings = get_non_asserted_mappings(yarrrml_data,  dict.fromkeys(list(yarrrml_data.get(YARRRML_MAPPINGS).keys())))
        for mapping in yarrrml_data.get(YARRRML_MAPPINGS):
            if mapping_format == R2RML_URI:
                source_list = add_table(yarrrml_data, mapping, list_initial_sources)
            else:
                source_list = add_source(yarrrml_data, mapping, list_initial_sources)
            subject_list = add_subject(yarrrml_data, mapping)
            pred = add_predicate_object_maps(yarrrml_data, mapping, mapping_format)
            it = 0
            for source in source_list:
                for subject in subject_list:
                    map_aux = add_mapping(mapping, mappings, it)
                    if type(source) is list:
                        rml_mapping.append(map_aux + source[0] + subject + pred + source[1])
                    else:
                        rml_mapping.append(map_aux + source + subject + pred)
                    rml_mapping[len(rml_mapping) - 1] = rml_mapping[len(rml_mapping) - 1][:-2]
                    rml_mapping.append(".\n\n\n")
                    it = it + 1

        logger.info("RML content is created!")
        rml_mapping_string = "".join(rml_mapping)
        try:
            graph = rdflib.Graph()
            graph.parse(data=rml_mapping_string, format="turtle")
            logger.info("Mapping has been syntactically validated.")
        except Exception as e:
            logger.error("ERROR: There is a syntactic error in the generated mapping")
            logger.error(str(e))
            return None
    except Exception as e:
        logger.error("ERROR: The YARRRML mapping has not been translated")
        logger.error(str(e))
        return None

    logger.info("Translation has finished successfully.")

    return rml_mapping_string


def inverse_translation(rdf_mapping, mapping_format=RML_URI):
    yarrrml_mapping = {'prefixes': [], 'mappings': {}}
    rdf_mapping.bind('rml', rdflib.term.URIRef(RML_URI))
    rdf_mapping.bind('rr', rdflib.term.URIRef(R2RML_URI))
    rdf_mapping.bind('ql', rdflib.term.URIRef(QL_URI))
    yarrrml_mapping['prefixes'] = add_inverse_prefix(rdf_mapping)
    query = f'SELECT ?triplesMap WHERE {{ ?triplesMap {RDF_TYPE} {R2RML_TRIPLES_MAP} . }} '
    triples_map = [tm[rdflib.Variable('triplesMap')] for tm in rdf_mapping.query(query).bindings]

    for tm in triples_map:
        tm_name = tm.split("/")[-1]
        yarrrml_tm = {'sources': [add_inverse_source(tm, rdf_mapping, mapping_format)]}
        yarrrml_tm['s'], classes = add_inverse_subject(tm, rdf_mapping)
        yarrrml_tm['po'] = add_inverse_pom(tm, rdf_mapping, classes, yarrrml_mapping['prefixes'])
        yarrrml_mapping['mappings'][tm_name] = yarrrml_tm

    string_content = str(yaml.dump(yarrrml_mapping, default_flow_style=None, sort_keys=False)).replace("'\"",
                                                                                                       '"').replace(
        "\"'", ' " ').replace('\'', '')
    return string_content
