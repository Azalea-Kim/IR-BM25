import re, string, timeit
import stringprep

s = 'one two one two-one 123,\nhi     hi              hi\n h'
# s.lower()
#
# s = re.sub(r"\'s", " ", s)
#
#
# table = str.maketrans(dict.fromkeys(string.punctuation))  # OR {key: None for key in string.punctuation}
# s = s.translate(table)
# table1 = str.maketrans(dict.fromkeys(string.digits))
# s = s.translate(table1)
# # print(s)
#
#
#
# s = re.sub(' +', ' ', s)
# print(s)
#
# s = re.sub('\n', " ", s)
# # print(s)

# dict_whitespace = dict.fromkeys(string.whitespace)
# dict_whitespace.pop(" ")
# dict_whitespace[" +"] = None

table1 = str.maketrans({"\n":" "})
s = s.translate(table1)
print(s)



# def test_set(s):
#     return ''.join(ch for ch in s if ch not in exclude)
#
# def test_re(s):  # From Vinko's solution, with fix.
#     return regex.sub('', s)
#
# def test_trans(s):
#     return s.translate (string.punctuation)
#
# def test_repl(s):  # From S.Lott's solution
#     for c in string.punctuation:
#         s=s.replace(c,"")
#     return s
#
# # print ("sets      :",timeit.Timer('f(s)', 'from __main__ import s,test_set as f').timeit(1000000))
# print ("regex     :",timeit.Timer('f(s)', 'from __main__ import s,test_re as f').timeit(1000000))
# print ("translate :",timeit.Timer('f(s)', 'from __main__ import s,test_trans as f').timeit(1000000))
# # print ("replace   :",timeit.Timer('f(s)', 'from __main__ import s,test_repl as f').timeit(1000000))