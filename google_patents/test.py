import time

import spacy
start_time = time.time()
# 加载英语语言模型
nlp = spacy.load("en_core_web_sm")

# 处理文本
text = "FIGS.4A and 4B illustrate contrast between the picture of a B/W image and the picture of a near IR image obtained according to the present invention."

# 使用 SpaCy 处理文本
doc = nlp(text)

# 获取主语
subject = None
for token in doc:
    if "subj" in token.dep_:
        subject = token.text
        break

# 打印结果
print(f"主语: {subject}")
print(time.time()-start_time)
