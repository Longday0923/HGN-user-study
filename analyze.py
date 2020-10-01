import json

file1 = './lab_students/lab_stu_format_junyi.jsonl'
file2 = './lab_students/lab_stu_format_Suji.jsonl'
file3 = './lab_students/lab_stu_format_A.jsonl'
file4 = './lab_students/lab_stu_format_B.jsonl'
file_me = 'thr-0.02_ans-correct_admin_pruned_chosen.jsonl'

check_annotator = True


def triple_in_graph(triple: list, graph: list):
    for ref_triple in graph:
        if triple[0:3] == ref_triple[0:3]:
            return True
    return False


def score_cal(one_graph_triples: list, ref_graph: list, sent_score: dict, ref_type: str):
    stu_valid = 0
    stu_all = 0
    stu_score_all = 0
    for stu_triple in one_graph_triples:
        if triple_in_graph(stu_triple, ref_graph):
            stu_all += 1
            stu_valid += 1 if stu_triple[3][8] == '1' else 0
            stu_score_all += float(stu_triple[3][-1]) if stu_triple[3][8] == '1' else 0
    sent_score[ref_type + '_all'] = stu_all
    sent_score[ref_type + '_valid'] = stu_valid
    sent_score[ref_type + '_percent'] = round(stu_valid / stu_all, 2) if stu_all != 0 else 0
    sent_score[ref_type + '_avg'] = round(stu_score_all / stu_all, 2) if stu_all != 0 else 0


def make_stu_sheet(sheet: list, stu_sent: dict, base: list, our: list):
    score_stu = {'index': stu_sent['index']}
    score_cal(stu_sent['triples'], base, score_stu, 'base')
    score_cal(stu_sent['triples'], our, score_stu, 'our')
    sheet.append(score_stu)


def main():
    with open(file1, 'r') as handle1, open(file2, 'r') as handle2, open(file3) as handle3, open(file4) as handle4, open(
            file_me) as handle_me:

        stu1 = json.load(handle1)
        stu2 = json.load(handle2)
        stu3 = json.load(handle3)
        stu4 = json.load(handle4)
        stume = json.load(handle_me)

        sheet_me = []
        sheet_1 = []
        sheet_2 = []
        sheet_3 = []
        sheet_4 = []

        # Parallel calculation: stu need information from mine
        for sent_num in range(0, 30):
            '''1.Take info from MINE annotation'''
            sent_me = stume[sent_num]
            my_score_str = sent_me['Base/Our']
            score_me = {'index': sent_me['index'],
                        'base_valid': int(my_score_str[1:3]),
                        'base_all': int(my_score_str[4:6]),
                        'base_percent': round(float(my_score_str[1:3]) / float(my_score_str[4:6]), 2) if
                        float(my_score_str[4:6]) != 0 else 0,
                        'base_avg': float(my_score_str[7:11]),
                        'our_valid': int(my_score_str[14:16]),
                        'our_all': int(my_score_str[17:19]),
                        'our_percent': round(float(my_score_str[14:16]) / float(my_score_str[17:19]), 2) if
                        float(my_score_str[17:19]) != 0 else 0,
                        'our_avg': float(my_score_str[20:24])}
            sheet_me.append(score_me)
            '''2.Calculate score for lab students annotation'''
            make_stu_sheet(sheet_1, stu1[sent_num], sent_me['all_extracted'], sent_me['threshold_hybrid'])
            make_stu_sheet(sheet_2, stu2[sent_num], sent_me['all_extracted'], sent_me['threshold_hybrid'])
            make_stu_sheet(sheet_3, stu3[sent_num], sent_me['all_extracted'], sent_me['threshold_hybrid'])
            make_stu_sheet(sheet_4, stu4[sent_num], sent_me['all_extracted'], sent_me['threshold_hybrid'])

        '''Calculate average score for each validation'''
        sheet_matric = [sheet_me, sheet_1, sheet_2, sheet_3, sheet_4]
        final_sheet = {'final_base_percent': 0, 'final_our_percent': 0, 'final_base_avg': 0, 'final_our_avg': 0}
        for every_sheet in sheet_matric:
            for every_sent in every_sheet:
                final_sheet['final_base_percent'] += every_sent['base_percent']
                final_sheet['final_base_avg'] += every_sent['base_avg']
                final_sheet['final_our_percent'] += every_sent['our_percent']
                final_sheet['final_our_avg'] += every_sent['our_avg']
            if check_annotator:
                final_sheet['final_base_percent'] = round(final_sheet['final_base_percent'] / len(sheet_me) * 100, 2)
                final_sheet['final_base_avg'] = round(final_sheet['final_base_avg'] / len(sheet_me), 2)
                final_sheet['final_our_percent'] = round(final_sheet['final_our_percent'] / len(sheet_me) * 100, 2)
                final_sheet['final_our_avg'] = round(final_sheet['final_our_avg'] / len(sheet_me), 2)
                print('Annotator_check:\t', '#' * 90, '\n', final_sheet)
                final_sheet['final_base_percent'] = 0
                final_sheet['final_base_avg'] = 0
                final_sheet['final_our_percent'] = 0
                final_sheet['final_our_avg'] = 0

        final_sheet['final_base_percent'] = round(
            final_sheet['final_base_percent'] / (len(sheet_matric) * len(sheet_me)) * 100, 2)
        final_sheet['final_base_avg'] = round(final_sheet['final_base_avg'] / (len(sheet_matric) * len(sheet_me)), 2)
        final_sheet['final_our_percent'] = round(
            final_sheet['final_our_percent'] / (len(sheet_matric) * len(sheet_me)) * 100, 2)
        final_sheet['final_our_avg'] = round(final_sheet['final_our_avg'] / (len(sheet_matric) * len(sheet_me)), 2)
        if not check_annotator:
            print(final_sheet)


if __name__ == '__main__':
    main()
