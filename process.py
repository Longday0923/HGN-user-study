import json
import csv

threshold = 0.01
readable_list = {
    'atlocation': 'at location',
    'capableof': 'capable of',
    'createdby': 'created by',
    'isa': 'is a',
    'hassubevent': 'has sub event',
    'partof': 'part of',
    'hascontext': 'has context',
    'hasproperty': 'has property',
    'madeof': 'made of',
    'notcapableof': 'not capable of',
    'notdesires': 'not desires',
    'receivesaction': 'receives action',
    'relatedto': 'related to',
    'usedfor': 'used for',
    '^atlocation': 'at location',
    '^capableof': 'capable of',
    '^createdby': 'created by',
    '^isa': 'is a',
    '^hassubevent': 'has sub event',
    '^partof': 'part of',
    '^hascontext': 'has context',
    '^hasproperty': 'has property',
    '^madeof': 'made of',
    '^notcapableof': 'not capable of',
    '^notdesires': 'not desires',
    '^receivesaction': 'receives action',
    '^relatedto': 'related to',
    '^usedfor': 'used for',
    '^antonym': 'antonym',
    '^causes': 'causes',
    '^desires': 'desires',
}

chosen = {1103, 750, 648, 605, 591, 573, 535, 493, 421, 377, 371, 368, 362, 354, 308, 304, 276, 246, 138, 125, 120, 108,
          69, 66, 52, 50, 49, 16, 9, 7, 1069}
read_file = 'user_study_full.jsonl'
stu_name = f'lab_stu_list.jsonl'
admin_name = f'non-zero-ext_thr-0.02_ans-correct_admin_pruned_format.jsonl'
admin_want = False
stu_want = True
chosen_want = True
check_flag = False
output_list = []
with open(read_file, 'r') as f, open(stu_name, 'w+') as stu_path, open(admin_name, 'w+',
                                                                       newline='') as admin_path:
    index = 0  # give index for every row(including wrong answer)
    request_cnt = 0
    for line in f:
        GEN = json.loads(line)
        if GEN['self_answer'] == GEN['correct_answer']:  # only consider statement with correct answer
            gen_cnt = 0  # counter for generated triples after threshold
            threshold_hybrid = []  # triples with hybrid and threshold
            all_extracted = []  # original extracted graph
            one_graph = []  # graph for students(merging of former two with no extra info)
            for triple in GEN['all_triples']:  # triples in one sentence
                '''
                structure:
                    ["serves", "bank", "is type of", "0.00", "generated"]
                '''
                triple[3] = float(triple[3])  # weight str->float
                if triple[-1] == 'extracted':  # for extracted triples
                    if triple[-3][0] == '^':  # swap cpt pair of reverse relation
                        triple[0], triple[1] = triple[1], triple[0]
                    if triple[-3] in readable_list.keys():
                        triple[-3] = readable_list[triple[-3]]  # change to readable relations
                    merge_flag = False
                    for recorded in all_extracted:  # relation merge: add weight for reverse relation
                        if triple[0:3] == recorded[0:3]:
                            recorded[3] = round(recorded[3] + triple[3], 2)
                            merge_flag = True
                    if not merge_flag:  # if not merge, append
                        one_graph.append(triple[0:3] + ['quality:0, usefulness:0'])  # For lab students, no weight and type
                        all_extracted.append(triple + ['(0*0=0)'])
                        if triple[3] > threshold:  # if threshold, append
                            threshold_hybrid.append(triple + ['(0*0=0)'])
                if triple[-1] == 'generated' and triple[-2] > threshold:  # for generated triples
                    one_graph.append(triple[0:3] + ['quality:0, usefulness:0'])
                    threshold_hybrid.append(triple + ['(0*0=0)'])
                    gen_cnt += 1  # counter for generated triples after threshold
            # for output
            index += 1
            # check_point
            if check_flag:
                if index == 6:
                    print()
            if admin_want and len(threshold_hybrid) != len(all_extracted) and len(all_extracted) != 0:
                request_cnt += 1
                output_admin = {
                    'index': index,
                    'thr/gen/ext/all': f'{len(threshold_hybrid)}/{gen_cnt}/{len(all_extracted)}/{len(GEN["all_triples"])}',
                    'question': GEN['question'],
                    'correct_answer': GEN['self_answer'],
                    'Base/Our': '(0/0,0)|(0/0,0)',
                    'prune_rate': f'{len(threshold_hybrid) / len(GEN["all_triples"]) * 100 if len(GEN["all_triples"]) else -1 :.2f}%',
                    'threshold_hybrid': threshold_hybrid,
                    'all_extracted': all_extracted,
                }
                admin_json = json.dumps(output_admin, sort_keys=False, indent=4, separators=(',', ':'))
                admin_path.write('{}\n'.format(admin_json))
            if stu_want and chosen_want and len(threshold_hybrid) != len(all_extracted) and index in chosen:
                output_stu = {
                    'index': index,
                    'question': GEN['question'],
                    'correct_answer': GEN['self_answer'],
                    'triples': one_graph
                }
                stu_json = json.dumps(output_stu, sort_keys=False, indent=4, separators=(',', ':'))
                stu_path.write('{}\n'.format(stu_json))
print(request_cnt)
