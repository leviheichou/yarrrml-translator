import yaml
import sys
import os
import mapping as mappingmod
import source as sourcemod
import subject as subjectmod
import predicateobject as predicateobjectmod



if __name__ =="__main__":
    if len(sys.argv)==1:
        print("Introduce the .yml file you want to convert to RML")
        file = input()
        #file="../test/gtfs-csv.yml"
        print("\n")
        #../test/example1/rml/mapping.yml
        with open(file) as f:
            print("Name for your file:")
            end=input()
            #end="prueba"
            if(end[:-4]!=".rml"):
                nuevo_fich=open(end+".rml","a")
            else:
                nuevo_fich=open(end,"a")
            data = yaml.safe_load(f)
            yaml_stream = True

    elif len(sys.argv)==5 and sys.argv[1]=="-m" and sys.argv[3]=="-o":
        file=sys.argv[2]
        with open(file) as f:
            end=sys.argv[4]
            if(end[:-4]!=".rml"):
                nuevo_fich=open(end+".rml","a")
            else:
                nuevo_fich=open(end,"a")
            data = yaml.safe_load(f)
            yaml_stream = True
    else:
        sys.tracebacklimit=0
        raise Exception("\n####################################\nERROR: Wrong argument input. You can:\n-Use no arguments\n-Use arguments: -m YARRRMLfile -o RMLFile\n####################################\n")


    print("------------------------START RML-------------------------------")
    mapping_list=[]
    list_initial_sources= sourcemod.getInitialSources(data)
    final=""
    final = mappingmod.addPrefix(data)
    try:
        for mapp in data.get("mappings"):
            subject_list=[]
            subject_list = subjectmod.addSubject(data, mapp)
            source_list=[]
            source_list=sourcemod.addSource(data,mapp,list_initial_sources)
            pred =predicateobjectmod.addPredicateObject(data,mapp)
            it = 0
            for source in source_list:
                for subject in subject_list:
                    map=mappingmod.addMapping(data,mapp,it)
                    if type(source) is list:
                        final += map + source[0] +subject + pred + source[1]
                    else:
                        final += map + source +subject + pred
                    final = final[:-3]
                    final+= ".\n\n\n"
                    it=it+1
        nuevo_fich.write(final)
    except Exception as e:
            print(str(e))
            print("------------------------END RML-------------------------------")
            print("FILE NOT SUCCESSFULY CREATED")
            if(".rml" in end):
                os.remove(end)
            else:
                os.remove(end+".rml")
            sys.exit()


    print("------------------------END RML-------------------------------")
    print("FILE SUCCESSFULY CREATED!")