# yarrrml-translator

![GitHub](https://img.shields.io/github/license/oeg-upm/yarrrml-translator?style=flat)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7024501.svg)](https://doi.org/10.5281/zenodo.7024501)
[![PyPI](https://img.shields.io/pypi/v/yarrrml-translator?style=flat)](https://pypi.org/project/yarrrml-translator)
![GitHub Release Date](https://img.shields.io/github/release-date/oeg-upm/yarrrml-translator)

The tool translates mapping rules from YARRRML in a turtle-based serialization of RML or R2RML. The translation is based 
on the [RML](https://rml.io/specs/rml/) and [YARRRML](https://rml.io/yarrrml/spec/) specifications.

## Limitations
We are working on including the following features which are not yet implemented:
- Functions using the [FnO](https://fno.io/) Ontology

## Installation:
```
pip install yarrrml-translator
```

## Execution
To execute from command line run the following:
```bash
python3 -m yarrrml_translator -i path_to_input_yarrrml.yml -o path_to_output.ttl [-f R2RML]
```

`-f R2RML` is an optional parameter for translating input YARRRML into R2RML

If you want to include the module in your implementation:
- for translating **RML mappings**:
```python
import yarrrml_translator
import yaml

rml_content = yarrrml_translator.translate(yaml.safe_load(open("path-to-yarrrml")))
```

- for translating **R2RML mappings**:
```python
import yarrrml_translator
import yaml

R2RML_URI = 'http://www.w3.org/ns/r2rml#'
rml_content = yarrrml_translator.translate(yaml.safe_load(open("path-to-yarrrml")), mapping_format=R2RML_URI)
```

## Authors
Ontology Engineering Group - Data Integration:
- [David Chaves-Fraga](mailto:david.chaves@upm.es)
- Luis López Piñero (Final bachelor thesis - v0.1)



