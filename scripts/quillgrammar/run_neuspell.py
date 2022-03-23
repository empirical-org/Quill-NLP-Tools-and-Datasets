import time

from tqdm import tqdm

from neuspell import BertsclstmChecker, SclstmChecker
checker = SclstmChecker()
checker = checker.add_("elmo", at="input")
checker.from_pretrained("/home/yves/software/neuspell/data/checkpoints/elmoscrnn-probwordnoise")

input_file = "/home/yves/projects/Quill-NLP-Tools-and-Datasets/quillgrammar/data/new_turk_data.csv"

with open(input_file) as i:
    lines = i.readlines()

corrected = 0
total = 0

start = time.time()
for line in tqdm(lines):
    input_sentence = line.strip()
    output_sentence = checker.correct(input_sentence)

    if input_sentence != output_sentence:
        corrected += 1

        different += 1
        print("Input:")
        print(input_sentence)
        print("Medium:")
        print(output_sentence_big)
        print("")
        diff = difflib.SequenceMatcher(None, input_sentence, output_sentence_big)
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, input_sentence[i1:i2], output_sentence_big[j1:j2]))
        input()


    total += 1
    

end = time.time()
total_time = end-start

print(f"{corrected}/{total}={corrected/total*100}% sentences corrected")
print(f"{total}/{total_time}={total/total_time} sentences/second")