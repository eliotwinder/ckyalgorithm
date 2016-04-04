import sys
import json

from pretty_print_tree import pretty_print_tree


def get_word_counts(training_tree):
    word_counts = {};
    
    def count_words(training_tree):
        if len(training_tree):
            poss_word = training_tree[-1]
            if type(poss_word) is unicode:
                if poss_word in word_counts:
                    word_counts[poss_word] += 1
                else:
                    word_counts[poss_word] = 1
            else:
                for sub_tree in training_tree[1:]:
                    count_words(sub_tree)

    count_words(training_tree)
    return word_counts


def get_rare_words(training_tree_file):
    word_counts = get_word_counts(training_tree_file)
    rare_words = [word for word, count in word_counts.items() if count < 5]
    return rare_words


def replace_rare_words(rare_words, training_trees):
    output = file(OUTPUT_FILEPATH, 'w')
    clean_trees = []

    def replace_in_tree(tree):
        clean_token = [tree[0]]
        for token in tree[1:]:
            if type(token) is unicode:
                if token in rare_words:
                    clean_token.append("__RARE__")
                else:
                    clean_token.append(token)
            else:
                clean_token.append(replace_in_tree(token))

        return clean_token

    for tree in training_trees:
        clean_tree = replace_in_tree(tree)
        clean_trees.append(json.dumps(clean_tree))

    output.write("\n".join(clean_trees))


def main(training_tree_file, output_filepath):
    training_trees_text = open(training_tree_file, 'r').read()
    training_trees = [json.loads(tree) for tree in training_trees_text.split("\n") if len(tree) > 0]
    rare_words = get_rare_words(training_trees)
    replace_rare_words(rare_words, training_trees)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    OUTPUT_FILEPATH = 'parse_train.rare.dat'
    main(sys.argv[1], OUTPUT_FILEPATH)
