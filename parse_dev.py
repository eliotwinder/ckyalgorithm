import sys
from collections import defaultdict

RULE_TYPES = {
    "unary": "UNARYRULE",
    "binary": "BINARYRULE",
    "nonterm": "NONTERMINAL"
}


def read_counts(counts_file_path):
    list_of_counts = file(counts_file_path, 'r')

    counts_dict = {
        RULE_TYPES["unary"]: {
            "count": 0
        },
        RULE_TYPES["binary"]: {
            "count": 0
        },
        RULE_TYPES["nonterm"]: {
            "count": 0
        }
    }

    for count in list_of_counts:
        count_info = count.rstrip().split(" ")
        (count_value, count_type, left_tag), right_tag = count_info[:3], count_info[3:]

        counts_dict[count_type]["count"] += 1
        if count_type == RULE_TYPES["nonterm"]:
            counts_dict[count_type][left_tag] = count_value
        elif count_type == RULE_TYPES["unary"]:
            if left_tag not in counts_dict[count_type]:
                counts_dict[count_type][left_tag] = defaultdict(int)
            
            counts_dict[count_type][left_tag]["count"] += 1
            counts_dict[count_type][left_tag][right_tag[0]] += 1

        elif count_type == RULE_TYPES["binary"]:
            if left_tag not in counts_dict[count_type]:
                counts_dict[count_type][left_tag] = defaultdict(int)
            
            counts_dict[count_type][left_tag]["count"] += 1
            counts_dict[count_type][left_tag][(right_tag[0], right_tag[1])] += 1            

    return counts_dict

# def get_most_likely_tag(start_index, end_index, tag, words):



def parse_line(line, counts):
    words = line.rstrip().split(" ")
    pi_table = defaultdict(int)
    unary_counts = counts[RULE_TYPES["unary"]]
    binary_counts = counts[RULE_TYPES["binary"]]
    nonterminal_counts = counts[RULE_TYPES["nonterm"]]

    def get_q_value(tag, rule):
        return binary_counts[tag][rule] / binary_counts[tag]["count"]

    def get_pi_value(start_point, end_point, tag):
        max_prob = 0
        most_likely_parse_tree = None

        if pi_table[(start_point, end_point, tag)]:
            return pi_table[(start_point, end_point, tag)]
        elif start_point == end_point:
            prob = unary_counts[tag][words[start_point]] / unary_counts[tag]["count"]
            most_likely_parse_tree = [tag, words[start_point]]
            pi_table[(start_point, end_point, tag)] = (prob, most_likely_parse_tree)
        else:
            for split_point in xrange(start_point, end_point - 1):
                print start_point, end_point, tag, split_point
                for rule, count in binary_counts.items():
                    q_value = get_q_value(tag, rule)
                    (left_pi_value, left_parse_tree) = pi_table[(start_point, split_point, rule[0])]
                    (right_pi_value, right_parse_tree) = pi_table[(split_point + 1, end_point, rule[1])]
                    prob = q_value * left_pi_value * right_pi_value
                    parse_tree = [tag, left_parse_tree, right_parse_tree]
                    pi_table[(start_point, end_point, tag)] = (prob, parse_tree)
                    if prob > max_prob:
                        max_prob = prob
                        most_likely_parse_tree = parse_tree

        return (max_prob, most_likely_parse_tree)


    max_prob = 0
    most_likely_parse_tree = None
    
    for length in xrange(1, len(words)):
        for start_point in xrange(1, len(words) - length):
            for tag in counts[RULE_TYPES["nonterm"]].keys():
                end_point = start_point + length 
                if tag != "count":
                    get_pi_value(start_point, end_point, tag)
    return get_pi_value(1, len(words), "SBARQ")


def parse_file(parse_file, counts):
    for line in parse_file:
        print parse_line(line, counts)
    # return [parse_line(line, counts) for line in parse_file]


def main(to_be_tagged, counts_file_path):
    to_be_tagged_text = file(to_be_tagged, 'r')
    counts = read_counts(counts_file_path)
    print parse_file(to_be_tagged_text, counts)

if __name__ == "__main__": 
  if len(sys.argv) != 3:
    print 'wrong args'
    sys.exit(1)
  main(sys.argv[1], sys.argv[2])