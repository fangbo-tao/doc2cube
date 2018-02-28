from data_table import DataTable
import traceback
import os
import sys
sys.path.append('../../')

if __name__ == "__main__":
    hier_meta_dict = {}
    data_folder = '../data_news/used'
    hier_meta_dict['Location'] = data_folder + '/Location.hier'
    # hier_meta_dict['Topic'] = data_folder + '/Topic.hier'

    data_file = data_folder + "/data_table.csv"
    doc_folder = data_folder + "/docs_linked/"      # the segphrased version
    splitter = "\t@@\t"

    dt = DataTable(data_file, hier_meta_dict)

    # used to store the constructing cells
    queries = []

    # if we want to sample at most K document from the cell for experiment
    K = 100000

    # group_name = 'Topics'
    # queries.append({'Topic':'Business'})
    # queries.append({'Topic':'Arts'})
    # queries.append({'Topic':'Travel'})
    # queries.append({'Topic':'World'})
    # queries.append({'Topic':'Science'})
    # queries.append({'Topic':'Health'})
    # queries.append({'Topic':'Technology'})
    # queries.append({'Topic':'Sports'})

    # group_name = 'Economies'
    # queries.append({'Location':'China', 'Topic':'Business'})
    # queries.append({'Location':'Russia', 'Topic':'Business'})
    # queries.append({'Location':'Japan', 'Topic':'Business'})
    # queries.append({'Location':'Korea', 'Topic':'Business'})
    # queries.append({'Location':'Germany', 'Topic':'Business'})
    # queries.append({'Location':'United Kingdom, with Dependencies and Territories', 'Topic':'Business'})
    # queries.append({'Location':'United States of America', 'Topic':'Business'})

    group_name = 'Countries'
    queries.append({'Location':'China'})
    queries.append({'Location':'Russia'})
    queries.append({'Location':'Japan'})
    queries.append({'Location':'North Korea'})
    queries.append({'Location':'Korea'})
    queries.append({'Location':'Syria'})
    queries.append({'Location':'United Kingdom, with Dependencies and Territories'})
    queries.append({'Location':'United States of America'})


    from cube_construction.joint_model import parse

    joint_docs = parse.find_joint_docs(data_folder)
    # print joint_docs


    query = queries[0]
    result = dt.slice_and_return_siblings(query)
    result_china = dt.slice_and_return_doc_id(query)
    result['Location|China;'] = result_china
    # print result_china 


    new_result = {}
    for item in result:
        doc_set = set()
        # print item  + ':' + str(len(result[item]))
        for k in result[item]:
            if str(k) in joint_docs:
                doc_set.add(str(k))
        new_result[item] = doc_set

    # print new_result['China']
    limit = 100
    refined_loc = {}
    for item in new_result:
        if len(new_result[item]) > limit:
            print item  + ':' + str(len(new_result[item]))
            refined_loc[item] = new_result[item]

    refined_loc['Location|England;'] = refined_loc['Location|United Kingdom, with Dependencies and Territories;']
    refined_loc['Location|The United States;'] = refined_loc['Location|United States of America;']
    refined_loc.pop('Location|United States of America;', None)
    refined_loc.pop('Location|United Kingdom, with Dependencies and Territories;', None)

    loc_list = ["Location|Italy;", "Location|France;", "Location|England;", "Location|Germany;", "Location|Netherlands;", "Location|Ireland;", "Location|Russia;", "Location|Spain;", "Location|Brazil;", "Location|Belgium;", "Location|The United States;", "Location|China;", "Location|Canada;", "Location|Australia;"]

    print refined_loc.keys()
    print '+++++'


    # exit(1)
    # with open(data_folder + '/doc_real.txt', 'w+') as f:
    dl_file = data_folder + '/../dl.txt'
    doc_file = data_folder + '/docs_parsed.txt'
    new_doc_file = data_folder + '/../d_prel.txt'
    label_file_prefix = data_folder + '/../l_prel'
    # linked_folder = data_folder + '/../docs_linked/'
    parse.create_data_file(joint_docs, refined_loc, dl_file, 
        doc_file, new_doc_file, label_file_prefix, loc_list)


    exit(1)




    result_file = data_folder + '/' + group_name + ".data"

    if os.path.isfile(result_file):
        print 'The resulting file exists, please backup.'
        exit(1)



    with open(result_file, "w+") as f:
        for query in queries:
            attrs = ""
            for k, v in query.items():
                attrs += "{0}|{1};".format(k, v)
            try:
                doc_list = dt.slice_and_return_doc_id(query)


                # get the first K documents
                if K > 0:
                    doc_list = doc_list[:K]

                doc_strs = [str(i) for i in doc_list]
                for doc_id in doc_strs:
                    with open(doc_folder + doc_id, 'r') as myfile:
                        data=myfile.read().replace('\n', '')
                    f.write(attrs + splitter + data + '\n')

                print "Attrs:{0};Doc#:{1}".format(attrs, len(doc_list))
            except:
                print "{1} failed to gen doc list".format(attrs)


    # with open(output_file + ".txt", "w+") as f:
    #     for query in queries:
    #         attrs = ""
    #         for k, v in query.items():
    #             attrs += "{0}|{1};".format(k, v)
    #         try:
    #             doc_list = dt.slice_and_return_doc_id(query)
    #             print "Attrs:{0};Doc#:{1}".format(attrs, len(doc_list))

    #             doc_str = [str(i) for i in doc_list]

    #             wline = "{0}:{1}\n".format(attrs, ",".join(doc_str))

    #             f.write(wline)
    #         except:
    #             print "{1} failed to gen doc list".format(attrs)

    # with open(output_file + "_parents.txt", "w+") as f:
    #     for query in queries:
    #         attrs = ""
    #         for k, v in query.items():
    #             attrs += "{0}|{1};".format(k, v)
    #         try:
    #             doc_lists = dt.slice_and_return_parents(query)
    #             print "Attrs:{0};Parent#:{1}".format(attrs, len(doc_lists))
    #             doc_strs = []
    #             for cell_name, doc_list in doc_lists.items():
    #                 doc_str = ",".join([str(i) for i in doc_list])
    #                 doc_strs.append(cell_name + "|" + doc_str)

    #             wline = "{0}:{1}\n".format(attrs, ";".join(doc_strs))

    #             f.write(wline)
    #         except:
    #             print "{1} failed to gen doc list".format(attrs)

    # with open(output_file + "_siblings.txt", "w+") as f:
    #     for query in queries:
    #         attrs = ""
    #         for k, v in query.items():
    #             attrs += "{0}|{1};".format(k, v)
    #         try:
    #             doc_lists = dt.slice_and_return_siblings(query)
    #             print "Attrs:{0};Siblings#:{1}".format(attrs, len(doc_lists))
    #             doc_strs = []
    #             for cell_name, doc_list in doc_lists.items():
    #                 doc_str = ",".join([str(i) for i in doc_list])
    #                 doc_strs.append(cell_name + "|" + doc_str)

    #             wline = "{0}:{1}\n".format(attrs, ";".join(doc_strs))

    #             f.write(wline)
    #         except:
    #             print(traceback.format_exc())
    #             print "{1} failed to gen doc list".format(attrs)


    # queries.append({'Location':'Illinois', 'Topic':'Sports'})
    # #queries.append({'Location':'New York'})
    # queries.append({'Location':'China'})
    # queries.append({'Location':'Russia'})
    # queries.append({'Location':'Japan'})
    # queries.append({'Location':'North Korea'})
    # queries.append({'Topic':'Asia Pacific'})
    # queries.append({'Topic':'Africa'})
    # queries.append({'Topic':'Gay Right'})
    # queries.append({'Location':'Syria'})
    # #queries.append({'Location':'Syria', 'Topic':'Military'}) => 0 doc
    # queries.append({'Location':'United States of America', 'Topic':'Military'})
    # queries.append({'Location':'United States of America', 'Topic':'Basketball'})
    # queries.append({'Location':'United States of America', 'Topic':'Music'})
    # queries.append({'Location':'United States of America', 'Topic':'Politics'})
    # queries.append({'Location':'United States of America', 'Topic':'Gun Control'})
    # queries.append({'Location':'United States of America', 'Topic':'Health'})
    # queries.append({'Location':'United States of America', 'Topic':'Immigration'})
    # queries.append({'Location':'China', 'Topic':'Politics'})
    # queries.append({'Location':'China', 'Topic':'Environment'})
    # #queries.append({'Location':'China', 'Topic':'Military'}) => 0 doc
    # queries.append({'Location':'China', 'Topic':'Business'})
    # queries.append({'Location':'United Kingdom, with Dependencies and Territories', 'Topic':'Business'})
    #queries.append({'Location':'Great Britain', 'Topic':'Business'})
